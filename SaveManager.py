import sqlite3
import pickle

#class that handles iinterfacing with our saves database...
class SaveManager():

    #Called before the world is created - makes the tables if they don't already exist...
    def __CreateDatabaseTables(self):
            self.__SaveCursor.execute("""
                CREATE TABLE IF NOT EXISTS Saves(
                    SaveName TEXT NOT NULL PRIMARY KEY,
                    DayNumber INTEGER, 
                    Map TEXT,
                    SiidaLocation INTEGER,
                    SiidaNeededGoals BLOB,
                    FoodStock INTEGER,
                    CloudChance INTEGER,
                    LavvuStocked INTEGER,
                    WoodStock INTEGER
                    
                ) WITHOUT ROWID;
            """)

                #We also wont have a residents table, so we create that too.

            #We dont need a primary key - we can just use ROWID
            self.__SaveCursor.execute("""
                CREATE TABLE IF NOT EXISTS AIs(

                    Save TEXT NOT NULL,
                    State INTEGER NOT NULL,
                    ActionQ BLOB, 
                    ActiveTags BLOB,
                    ActiveGoal BLOB,
                    ActiveAction BLOB,
                    MoveQ BLOB,
                    Hunter BLOB,
                    Hunting BLOB,
                    GoalLoc INTEGER,
                    Loc INTEGER,
                    Name TEXT,
                    Hunger INTEGER,
                    Carrying BLOB,

                    FOREIGN KEY(Save) REFERENCES Saves(SaveName)
            );
            """)

            self.__SaveCursor.execute("""
                CREATE TABLE IF NOT EXISTS Clouds(
                    Save TEXT NOT NULL,
                    CloudLocation INTEGER NOT NULL,
                    CloudGrid TEXT NOT NULL,
                    CloudAge INTEGER NOT NULL,
    
                    FOREIGN KEY(Save) REFERENCES Saves(SaveName)
                );
            """)
            self.__SaveCursor.execute("""
                CREATE TABLE IF NOT EXISTS Lavvu(
                    Save TEXT NOT NULL,
                    Loc INTEGER,

                    FOREIGN KEY(Save) REFERENCES Saves(SaveName)
                );
            """)

            self.__SaveController.commit()

    #Called before the world is created - so all the info is filled later on - this just handles ettling on a save name and prepping db for that when we want to save...
    def __CreateNewSave(self):        

                #Get our existing saves 
                SaveNames = self.__SaveCursor.execute("SELECT SaveName FROM Saves").fetchall()      
                GivenSaveName = input("Please enter the name for your new save ")

                if GivenSaveName == "NEW":
                    print("Sorry! You can't call a save 'NEW' - this keyword is reserved for making a new save when choosing between existing saves")
                    self.__CreateNewSave()
                else:

                    #Remember this'll be fetched in the format ([Name], ) so we want to take a gander at the 0th item from the fetched tuples
                    for i in SaveNames:         
                        if GivenSaveName == i[0]:                     
                            print("Error - that save name already exists! You will have to choose a different one!")
                            self.__CreateNewSave()

                    #Reaching this point means we can accept this save name
                    self.__SaveName =  GivenSaveName
                    self.__SaveController.commit()

           
    def __InputSaveChoice(self):


            Choice = input("Please enter the name of the save you would like to load! Alternately, you can enter 'NEW' to start a new save! ")
                    
            if Choice == "NEW":
                #New save
                self.__CreateNewSave()
            else:
                
                #Check that the given name actually exists...         
                self.__SaveData = self.__SaveCursor.execute("""
                    SELECT * FROM Saves WHERE SaveName = :Name         
                """, {'Name':Choice}).fetchone()

                if self.__SaveData != None:
              
                    #Get all AI not including residents...
                    self.__AIData = self.__SaveCursor.execute("""
                    SELECT * FROM AIs WHERE Save = :SaveName AND Name IS NULL
                    """, { 'SaveName':Choice}).fetchall()

                    #And now the residents...
                    self.__ResidentData = self.__SaveCursor.execute("""
                    SELECT * FROM AIs WHERE Save = :SaveName AND Name IS NOT NULL
                    """, { 'SaveName':Choice}).fetchall()
        
                    #Get our existing clouds
                    self.__CloudsSaved = self.__SaveCursor.execute("""
                    SELECT * FROM Clouds WHERE Save = :SaveName
                    """, {'SaveName':Choice}).fetchall()
    
                    self.__LavvuData = self.__SaveCursor.execute("""
                    SELECT Loc FROM Lavvu WHERE Save = :SaveName
                    """, {'SaveName':Choice}).fetchall()


                    #We also want to delete all the AI loaded as ALL of their stats are very likely to have changed by the time of next save, and in addition we have nothing to point each opbject in the game to the entity in the database it points to
                    #while we could use stuff like name and location these have potential to be the same and then everything goes wrong.
                    self.__SaveCursor.execute("""
                    DELETE FROM AIs WHERE Save = :SaveName
                    """, {'SaveName':Choice})


                    #Same thing for clouds - all the stuff will have changed and they might not even exist anymore...
                    self.__SaveCursor.execute("""
                    DELETE FROM Clouds WHERE Save = :SaveName
                    """, {'SaveName':Choice})


                    self.__SaveName = Choice
                    print("Loading ", self.__SaveName)

                    self.__bFileToLoad = True
                else:
                    print("There was an error with your input name - likely the name couldn't be found in the saves database...")
                    self.__InputSaveChoice()
            


    #Set up controller n shiz
    def __init__(self):     

                   
    
        #Controller of the save file...
        #A good thing abt SQLite is that it will auto error validate the file - creating then connecting if this file doesn't exists
        self.__SaveController = sqlite3.connect("Saves.db")
        self.__SaveCursor = self.__SaveController.cursor()

        #Data read from save file about their respective tables...
        self.__SaveData = None
        self.__AIData = None
        self.__ResidentData = None
        self.__LavvuData = None
        self.__CloudsSaved = None

        #Save name that refers to the simulation we are running this time...
        self.__SaveName = ""

        #Is there a file we should load?
        self.__bFileToLoad = False

        #We will be constructed upon system start, so want to handle the opening of files...

        self.__CreateDatabaseTables()

        #Query save file to see if we can find any existing saves
        Saves = self.__SaveCursor.execute("""
                SELECT SaveName, DayNumber FROM Saves
            """).fetchall()

            #In case you close the program on start before making a first save...
        if len(Saves) < 1:
            print("No saves found")
            self.__CreateNewSave()
        else:
            print("We found some saves!")

            self.AverageDayNumber = self.__SaveCursor.execute("SELECT AVG(DayNumber) FROM Saves").fetchone()
            print("Average save day number = ", self.AverageDayNumber[0])
            print("--------")

            for i in Saves:
                print("{} - Day number {}".format(i[0], i[1]))
            self.__InputSaveChoice()


    #Convert coordinates into or out of a form that can be saved as an integer...
    def _ConvertCoordinates(self, Given):
   
        #Turn the location into a number we can use in the database!
        try:
            return Given[0] * 100 + Given[1]

            #E.G.: 5021 = (50, 21) 
            #Thanks to the Skeleton code for this stupendous idea...

        #Back the other way...
        except:
            return (Given // 100, Given % 100)


    

    #Run length encode / un run length encode a grid of cells so it can be saved...
    def _ConvertGrid(self, Given, UncompTo = None, **ConvertRepsTo):
        
        #Into RLE 2D array -> String
        if UncompTo == None:

            GivenComp = ""
            Last = ""
            LastAmount = 0
            for i in Given:
                for j in i:       
                    Current = None
                    #If this is a grid of cell objects we want their rep char, else itll be just a character and that is fine to represent it...
                    try:
                        Current = j._GetChrRep()
                    except:
                        Current = j
                    if Last == Current:
                        LastAmount += 1
                    else:
                        #else add them all to the thing, and reset variables...
                        if Last != "":
                            GivenComp = GivenComp + Last + str(LastAmount) + " "
                        Last = Current
                        LastAmount = 1
                        
            #Final append so last ones are there
            GivenComp = GivenComp + Last + str(LastAmount) + " "
            return GivenComp
        else:

            #Why a string? so we can concatentate more digits as we find em    
            Amount = ""

            #How many cells have we added?
            Done = 0
            
            UnComped = UncompTo

            #What is the representative for a cell we have in the run length encodeed
            CellRep = ""
            for i in Given:
                
                #Space marks the end of info about a cell - so we can add to the grid...
                if i == " ":

                    #Get from the input dictionary what this rep should be - defaulting to repping itself...
                    ActualCell = ConvertRepsTo.get(CellRep, CellRep)
                
                    for j in range(int(Amount)):
                        #We get what the cell is supposed to represent, and put it in the next point in the grid...                    
                        UnComped[Done // len(UncompTo)][Done % len(UncompTo)] = ActualCell
                        Done += 1
                    Amount = 0
                elif i.isdigit():

                    Amount = str(Amount) + str(i)
                else:
                    CellRep = i

            return UnComped
                         
    #Save our simulation - note down the stuff we need
    def _Save(self, GivenWorld):
 
        MapComp = self._ConvertGrid(GivenWorld._Grid)

        AIToSave = GivenWorld.Siida._GetSiidaResidents() + GivenWorld._GetReindeer()
        for i in AIToSave:

            #Get all the variables we would otherwise need
            
            PickledAQ = pickle.dumps(i._GetActionQueue())        
            PickledTags = pickle.dumps(i._GetActiveTags())
            PickledGoal = pickle.dumps(i._GetActiveGoal())
            PickledAction = pickle.dumps(i._GetActiveAction())
            PickledMoves = pickle.dumps(i._GetMoveQueue())
            PickledHunter = pickle.dumps(i._Hunter)

            #Only our residents have a found so we use this try and except to catch the cases in which this is a reindeer...
            PickledHunting = None
            try:
                PickledHunting = pickle.dumps(i._GetFound())
            except:
                pass
            
            GoalLocComp = self._ConvertCoordinates(i._GetGoalLocation())
            LocComp = self._ConvertCoordinates(i._GetLocation())


            Name = None
            Hunger = 0
            CResources = None
            #This is what discerns our AI - between residents and reindeer - 
            try:
                Name = i._GetName()
                Hunger = i._GetHunger()
                CResources = pickle.dumps(i._GetCarryingResources())
            except:
                pass
            
            self.__SaveCursor.execute("""
            INSERT INTO AIs VALUES(:Save, :State, :ActionQ, :Tags, :ActiveGoal, :ActiveAction, :MoveQ, :Hunter, :Hunting, :GoalLoc, :Loc, :Name, :Hunger, :Carrying)""", 
            {'Save': self.__SaveName, 'State': i._GetCurrentState(), 'ActionQ': PickledAQ, 'Tags': PickledTags, 'ActiveGoal': PickledGoal, 'ActiveAction': PickledAction, 'MoveQ': PickledMoves, 'Hunter': PickledHunter, 'Hunting':PickledHunting, 'GoalLoc':GoalLocComp, 'Loc': LocComp, 'Name': Name, 'Hunger': Hunger, 'Carrying': CResources})

        for i in GivenWorld._GetWeather()._GetCloudsInWorld():
            GridComp = self._ConvertGrid(i._Grid)          
            LocComp = self._ConvertCoordinates(i._GetLocation())
            Age = i._GetCloudAge()
            self.__SaveCursor.execute("INSERT INTO Clouds VALUES (:Save, :Location, :Grid, :Age)", {"Save":self.__SaveName, "Location":LocComp, "Grid":GridComp, 'Age':Age})  


        #No need to do the injection protection here...                                                                            
        
        
        SiidaLocation = self._ConvertCoordinates(GivenWorld.Siida.CentreLocation)
        PickleGoals = pickle.dumps(GivenWorld.Siida.NeededGoals)

        #If this already exists
        if self.__SaveCursor.execute("SELECT 1 FROM Saves WHERE EXISTS(SELECT SaveName FROM Saves WHERE SaveName = :Save)", {'Save':self.__SaveName}).fetchone():
            self.__SaveCursor.execute("""
            UPDATE Saves 
            SET DayNumber = :Day, Map = :Comp, SiidaLocation = :SiidaLoc, SiidaNeededGoals = :Goals, FoodStock = :Food, CloudChance = :CChance, LavvuStocked = :LavvuStock, WoodStock = :Wood
            WHERE SaveName = :Save             
            """, {'Save': self.__SaveName, 'Day': GivenWorld._GetTime()._GetDayNumber(), 'Comp': MapComp, 'SiidaLoc': SiidaLocation, 'Goals': PickleGoals, 'Food': GivenWorld.Siida.ResourcesInStock["FoodSupply"], 'CChance': GivenWorld._GetWeather()._GetCumulativeCloudChance(), 'LavvuStock': GivenWorld.Siida._GetLavvuStocked(), 'Wood': GivenWorld.Siida.ResourcesInStock["WoodSupply"]})
        else:
            self.__SaveCursor.execute("INSERT INTO Saves VALUES (:Save, :Day, :Comp, :SiidaLoc, :Goals, :Food, :CChance, :LStock, :WoodStock)", {'Save': self.__SaveName, 'Day': GivenWorld._GetTime()._GetDayNumber(), 'Comp': MapComp, 'SiidaLoc': SiidaLocation, 'Goals': PickleGoals, 'Food': GivenWorld.Siida.ResourcesInStock["FoodSupply"], 'CChance':GivenWorld._GetWeather()._GetCumulativeCloudChance(), 'LStock': GivenWorld.Siida._GetLavvuStocked(), 'WoodStock': GivenWorld.Siida.ResourcesInStock["WoodSupply"]})


        #And now for our lavvu
        #Iterating through the lavvu that exist in the table and the ones in the world - if exists in both simply update the location
        #If not existing in table add it
        #If not existing in lavvu in world remove it from the table

        #Get our lavvu saved
        LavvuInTable = self.__SaveCursor.execute("SELECT rowid, Loc FROM Lavvu WHERE Save = :GivenSave", {'GivenSave':self.__SaveName}).fetchall()

        #If we have more lavvu saved then existing, pop the difference from the table. 
        LengthDiff = len(LavvuInTable) - len(GivenWorld.Siida._GetLavvu())
        if LengthDiff > 0:
                #kick it out of the table!
                self.__SaveCursor.execute("""
                DELTE TOP(:Diff)
                FROM Lavvu
                """, {'Diff':LengthDiff})
        
        for i in GivenWorld.Siida._GetLavvu():
            bFound = False
            for j in LavvuInTable:
        
                if self._ConvertCoordinates(i._GetLocation()) == j[1]:        
                    bFound = True

                    #Remove this from our lavvu saved list so we do not use it again for others
                    LavvuInTable.remove(j)

            #If we couldn't find our lavvu location, we want to update - but only if there are the same number of records in the world and in the table - so we will add new till the difference is 0
            if bFound == False:

                if LengthDiff < 0:
                    LengthDiff += 1
                    self.__SaveCursor.execute("""INSERT INTO Lavvu VALUES(:SaveName, :Location)""", {'SaveName': self.__SaveName, 'Location': self._ConvertCoordinates(i._GetLocation())})

                #else if we now have the same number of records update where the top location from the 
                else:
                    self.__SaveCursor.execute("""
                    UPDATE Lavvu
                    SET Loc = :NewLoc
                    WHERE rowid = :GivenID  """, {'NewLoc': self._ConvertCoordinates(i._GetLocation()), 'GivenID': LavvuInTable[0][0]})
                    LavvuInTable.pop(0)

        #HOPEFULLY that has worked...
        
        #And that SHOULD be us saved to a file...
        self.__SaveController.commit()
        print("Simulation saved!")


        ##
        #GETTERS AND SETTERS
        ##

    def _GetSaveData(self):
        return self.__SaveData

    def _GetAIData(self):
        return self.__AIData

    def _GetResidentData(self):
        return self.__ResidentData

    def _GetLavvuData(self):
        return self.__LavvuData

    def _GetCloudsSaved(self):
        return self.__CloudsSaved

    def _GetFileToLoad(self):
        return self.__bFileToLoad