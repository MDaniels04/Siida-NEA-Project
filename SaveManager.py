import sqlite3
import pickle

#class that handles iinterfacing with our saves database...
class SaveManager():

    #Called before the world is created - makes the tables if they don't already exist...
    def __CreateDatabaseTables(self):
            self.SaveCursor.execute("""
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
            self.SaveCursor.execute("""
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

                    FOREIGN KEY(Save) REFERENCES Saves(SaveName)
            );
            """)

            self.SaveCursor.execute("""
                CREATE TABLE IF NOT EXISTS Clouds(
                    Save TEXT NOT NULL,
                    CloudLocation INTEGER NOT NULL,
                    CloudGrid TEXT NOT NULL,
                    _CloudAge INTEGER NOT NULL,
    
                    FOREIGN KEY(Save) REFERENCES Saves(SaveName)
                );
            """)

            self.SaveController.commit()

    #Called before the world is created - so all the info is filled later on - this just handles ettling on a save name and prepping db for that when we want to save...
    def __CreateNewSave(self):        

                #Get our existing saves 
                SaveNames = self.SaveCursor.execute("SELECT SaveName FROM Saves").fetchall()      
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
                    self.SaveName =  GivenSaveName
                    self.SaveController.commit()

           
    def __InputSaveChoice(self):


            Choice = input("Please enter the name of the save you would like to load! Alternately, you can enter 'NEW' to start a new save! ")
                    
            if Choice == "NEW":
                #New save
                self.__CreateNewSave()
            else:
                
                #Check that the given name actually exists...         
                self.SaveData = self.SaveCursor.execute("""
                    SELECT * FROM Saves WHERE SaveName = :Name         
                """, {'Name':Choice}).fetchone()

                if self.SaveData != None:
              
                    #Get all AI not including residents...
                    self.AIData = self.SaveCursor.execute("""
                    SELECT * FROM AIs WHERE Save = :SaveName AND Name IS NULL
                    """, { 'SaveName':Choice}).fetchall()

                    #And now the residents...
                    self.ResidentData = self.SaveCursor.execute("""
                    SELECT * FROM AIs WHERE Save = :SaveName AND Name IS NOT NULL
                    """, { 'SaveName':Choice}).fetchall()
        
                    #Get our existing clouds
                    self.CloudsSaved = self.SaveCursor.execute("""
                    SELECT * FROM Clouds WHERE Save = :SaveName
                    """, {'SaveName':Choice}).fetchall()

                    #We also want to delete all the AI loaded as ALL of their stats are very likely to have changed by the time of next save, and in addition we have nothing to point each opbject in the game to the entity in the database it points to
                    #while we could use stuff like name and location these have potential to be the same and then everything goes wrong.
                    self.SaveCursor.execute("""
                    DELETE FROM AIs WHERE Save = :SaveName
                    """, {'SaveName':Choice})


                    #Same thing for clouds - all the stuff will have changed and they might not even exist anymore...
                    self.SaveCursor.execute("""
                    DELETE FROM Clouds WHERE Save = :SaveName
                    """, {'SaveName':Choice})


                    self.SaveName = Choice
                    print("Loading ", self.SaveName)

                    self.bFileToLoad = True
                else:
                    print("There was an error with your input name - likely the name couldn't be found in the saves database...")
                    self.__InputSaveChoice()
            


    #Set up controller n shiz
    def __init__(self):     

                   
    
        #Controller of the save file...
        #A good thing abt SQLite is that it will auto error validate the file - creating then connecting if this file doesn't exists
        self.SaveController = sqlite3.connect("Saves.db")
        self.SaveCursor = self.SaveController.cursor()

        #Data read from save file about their respective tables...
        self.SaveData = None
        self.AIData = None
        self.ResidentData = None

        self.CloudsSaved = None

        #Save name that refers to the simulation we are running this time...
        self.SaveName = ""

        #Is there a file we should load?
        self.bFileToLoad = False

        #We will be constructed upon system start, so want to handle the opening of files...

        self.__CreateDatabaseTables()

        #Query save file to see if we can find any existing saves
        Saves = self.SaveCursor.execute("""
                SELECT SaveName, DayNumber FROM Saves
            """).fetchall()

            #In case you close the program on start before making a first save...
        if len(Saves) < 1:
            print("No saves found")
            self.__CreateNewSave()
        else:
            print("We found some saves!")

            self.AverageDayNumber = self.SaveCursor.execute("SELECT AVG(DayNumber) FROM Saves").fetchone()
            print("Average save day number = ", self.AverageDayNumber[0])
            print("--------")

            for i in Saves:
                print("{} - Day number {}".format(i[0], i[1]))
            self.__InputSaveChoice()


    #Convert coordinates into or out of a form that can be saved as an integer...
    def ConvertCoordinates(self, Given):
   
        #Turn the location into a number we can use in the database!
        try:
            return Given[0] * 100 + Given[1]

            #E.G.: 5021 = (50, 21) 
            #Thanks to the Skeleton code for this stupendous idea...

        #Back the other way...
        except:
            return (Given // 100, Given % 100)


    

    #Run length encode / un run length encode a grid of cells so it can be saved...
    def ConvertGrid(self, Given, UncompTo = None, **ConvertRepsTo):
        
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
                        Current = j._ChrRep
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
    def Save(self, GivenWorld):
 
        MapComp = self.ConvertGrid(GivenWorld._Grid)

        AIToSave = GivenWorld.Siida.SiidaResidents + GivenWorld.Reindeer
        for i in AIToSave:

            #Get all the variables we would otherwise need
            
            PickledAQ = pickle.dumps(i._ActionQueue)        
            PickledTags = pickle.dumps(i._ActiveTags)
            PickledGoal = pickle.dumps(i._ActiveGoal)
            PickledAction = pickle.dumps(i._ActiveAction)
            PickledMoves = pickle.dumps(i._MoveQueue)
            PickledHunter = pickle.dumps(i._Hunter)

            #Only our residents have a found so we use this try and except to catch the cases in which this is a reindeer...
            PickledHunting = None
            try:
                PickledHunting = pickle.dumps(i.Found)
            except:
                pass
            
            GoalLocComp = self.ConvertCoordinates(i._GoalLocation)
            LocComp = self.ConvertCoordinates(i.Location)


            Name = None

            #This is what discerns our AI - between residents and reindeer - 
            try:
                Name = i.Name
            except:
                pass
            
            self.SaveCursor.execute("""
            INSERT INTO AIs VALUES(:Save,  :State, :ActionQ, :Tags, :ActiveGoal, :ActiveAction, :MoveQ, :Hunter, :Hunting, :GoalLoc, :Loc, :Name)""", 
            {'Save': self.SaveName, 'State': i._CurrentState, 'ActionQ': PickledAQ, 'Tags': PickledTags, 'ActiveGoal': PickledGoal, 'ActiveAction': PickledAction, 'MoveQ': PickledMoves, 'Hunter': PickledHunter, 'Hunting':PickledHunting, 'GoalLoc':GoalLocComp, 'Loc': LocComp, 'Name': Name})

        for i in GivenWorld.Weather._CloudsInWorld:
            GridComp = self.ConvertGrid(i._Grid)          
            LocComp = self.ConvertCoordinates(i.Location)
            Age = i._CloudAge
            self.SaveCursor.execute("INSERT INTO Clouds VALUES (:Save, :Location, :Grid, :Age)", {"Save":self.SaveName, "Location":LocComp, "Grid":GridComp, 'Age':Age})  


        #No need to do the injection protection here...                                                                            
        
        
        SiidaLocation = self.ConvertCoordinates(GivenWorld.Siida.CentreLocation)
        PickleGoals = pickle.dumps(GivenWorld.Siida.NeededGoals)

        #If this already exists
        if self.SaveCursor.execute("SELECT 1 FROM Saves WHERE EXISTS(SELECT SaveName FROM Saves WHERE SaveName = :Save)", {'Save':self.SaveName}).fetchone():
            self.SaveCursor.execute("""
            UPDATE Saves 
            SET DayNumber = :Day, Map = :Comp, SiidaLocation = :SiidaLoc, SiidaNeededGoals = :Goals, FoodStock = :Food, CloudChance = :CChance, LavvuStocked = :LavvuStock, WoodStock = :Wood
            WHERE SaveName = :Save             
            """, {'Save': self.SaveName, 'Day': GivenWorld.Time.DayNumber, 'Comp': MapComp, 'SiidaLoc': SiidaLocation, 'Goals': PickleGoals, 'Food': GivenWorld.Siida.ResourcesInStock["FoodSupply"], 'CChance': GivenWorld.Weather._CumCloudChance, 'LavvuStock': GivenWorld.Siida.LavvuStocked, 'Wood': GivenWorld.Siida.ResourcesInStock["WoodSupply"]})
        else:
            self.SaveCursor.execute("INSERT INTO Saves VALUES (:Save, :Day, :Comp, :SiidaLoc, :Goals, :Food, :CChance, :LStock, :WoodStock)", {'Save': self.SaveName, 'Day': GivenWorld.Time.DayNumber, 'Comp': MapComp, 'SiidaLoc': SiidaLocation, 'Goals': PickleGoals, 'Food': GivenWorld.Siida.ResourcesInStock["FoodSupply"], 'CChance':GivenWorld.Weather._CumCloudChance, 'LStock': GivenWorld.Siida.LavvuStocked, 'WoodStock': GivenWorld.Siida.ResourcesInStock["WoodSupply"]})

        #And that SHOULD be us saved to a file...
        self.SaveController.commit()
        print("Simulation saved!")

