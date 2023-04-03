import Resident
import random
import IMGS
import math
import Goal
import Tag
import pickle
import pyglet.clock as PC
import Hut

#Siida management manages the residents in our Siida - essentially assigning goals to them

#Apologies for slightly confusing file name, our main file is called Siida so we couldnt call it that

class Siida():

    #A function to return a random land coordinate within a certain radius of what we take the siida to be - this will mean people will spawn together, and build structures in largely the same area....    
    def _GetLocationInSiida(self):
        #Get which land coords satisfy the radius, then pick a random one
        InBounds = []
        for It in self.__World._GetLandCoords():
            #Copy pasted Manhattan distance from A* - its not much repeated code I spose, and otherwise we get circular import problemos...
            if (abs(It[0] - self.CentreLocation[0]) + abs(It[1] - self.CentreLocation[1])) <= self.__SiidaRadius:
                InBounds.append(It)
                #NOT CALLING HERE              
        return random.choice(InBounds)

    #Created at the start of the game...
    # Spawn radius is the distance around the main point we class this Siida at
    def __init__(self, StartingMembers, SpawnRadius, GivenWorld, Saver):

        #Find a point for our Siida to put themselves in the meantime...

        self.__World = GivenWorld 

        self.__SiidaRadius = 5

        #The Lavvu in our world!
        self.__Lavvu = []

        #Are we migrating?
        self.__bMigrating = False

        #How many lavvu do we have stocked and want to put down...
        self.__LavvuStocked = 0

        self.__SiidaResidents = []
        

        #ADD SAVES FOR THIS 
        #How many days should we wait before sending out another request for a goal? Indexes are as follows
        #0 -> Food cry
        #1 -> Build lavvu cry
        self.CryCooldown = [0, 0]

        if Saver._GetFileToLoad() == True:
            
            #We need to convert the stored coordinates, remember...
            self.CentreLocation = Saver._ConvertCoordinates(Saver._GetSaveData()[3])           
                
            #As it were saved...
            self.NeededGoals = pickle.loads(Saver._GetSaveData()[4])
            
            self.ResourcesInStock = {
                "FoodSupply":Saver._GetSaveData()[5],
    
                "WoodSupply":Saver._GetSaveData()[8]
            }
            
            self.__LavvuStocked = Saver._GetSaveData()[7]

            #Now we need to load up our residents again...
            self.__SiidaResidents = []
            for i in Saver._GetResidentData():

                #Reconstruct these members from all the variables...

                OldResident = Resident.Resident(IMGS.PersonIMG, self.__World, Saver._ConvertCoordinates(i[10]), self)

                OldResident._SetCurrentState(i[1])
                OldResident._SetActionQueue(pickle.loads(i[2]))
                OldResident._SetActiveTags(pickle.loads(i[3]))
                OldResident._SetActiveGoal(pickle.loads(i[4]))
                OldResident._SetActiveAction(pickle.loads(i[5]))
                OldResident._SetMoveQueue(pickle.loads(i[6]))
                OldResident._Hunter = pickle.loads(i[7])
                OldResident._SetFound(pickle.loads(i[8]))
                OldResident._SetGoalLocationSetter(Saver._ConvertCoordinates(i[9]))
                
                #Dont need to set location, already handled that gubbins
                OldResident._SetName(i[11])
                OldResident._SetHunger(i[12])
                Resources = pickle.loads(i[13])

                for i in Resources:                
                    OldResident._SetCarryingResources(i, Resources[i])
               
                self.__SiidaResidents.append(OldResident)  


            for i in Saver._GetLavvuData():
        
                self.__Lavvu.append(Hut.Lavvu(IMGS.LavvuIMG, Saver._ConvertCoordinates(i[0]), self.__World._GetDrawBatch()))    
        else:

            #Here we are specifying a coord to be taken as the current centre of the Siida -
            self.CentreLocation = self.__World._GetLandCoords()[random.randrange(0, len(self.__World._GetLandCoords()))]
       

            #Spawn in our initial siida members
            for it in range(0, StartingMembers):
 
                self.__SiidaResidents.append(Resident.Resident(IMGS.PersonIMG, self.__World,  self._GetLocationInSiida(), self))
           

            #Each member of the Siida will eat 5 arbitrary food units a day - this is enough food for a month  
            #Seems like a lot but trust me its gonna get scarce....    

            #Tracking what structres are in the siida - need to be all packed up in order to migrate...

            self.StructuresInSiida = []
                          
            self.ResourcesInStock = {

                #When residents don't have enough food, they will get the hungry tag. If they remain hungry for a week, they die.
                "FoodSupply":len(self.__SiidaResidents) * 150,

                #Wood is used for the construction of lavvu and the burning of fires
                #Running out of wood can be either a none issue in summer, or a catastrophe in winter when wood is vital for staying warm
                "WoodSupply": 25,

                #More resources????
            }

            #What goals do the Siida currently need to pay attention to?
            self.NeededGoals = []


    #The function run every day, checking the stats of the siida and assigning goals if the problem arises....
    def _DailyFunction(self):


        #Look into migrating
        DayOfYear = self.__World._GetTime()._GetDayNumber() % 365

        #Migrate to mountains


        #We want to go to random tiles of a type so the migrations are more noticeable than just moving 2 cells away, though it may not make the most logical sense for a siida to do so.

        bMigrationStart = False

        if DayOfYear == 1:
            self.CentreLocation = random.choice(self.__World._GetMountainCoords())
            bMigrationStart = True
        elif DayOfYear == 274:
            self.CentreLocation = random.choice(self.__World._GetLowlandCoords())
            bMigrationStart = True
        elif DayOfYear == 335:
            self.CentreLocation = random.choice(self.__World._GetForestCoords())
            bMigrationStart = True

        #Assign enough new goals to migrate for each lavvu and give everyone the migration tag...
        if bMigrationStart:
            self.bMigrationStart = False
            if len(self.__Lavvu) > 0:
     
                #Give all residents the ability to do this...
                for i in self.__SiidaResidents:
                                            #When a resident is "migrating" they can pack up lavvu rather than going to make...
                    i._SetActiveTags(i._GetActiveTags() + [Tag.Tag("PackingAbility")])
                #This should automatically be removed when they place the huts...

                for j in range(len(self.__Lavvu)):
                    self.NeededGoals.append(Goal.Goal([Tag.Tag("BuiltLavvu")], " pack up lavvus to migrate", 5))


        #Now we address any goals that need passing out....
         
        #If there is less than enough food for a week left, we need to get more (the threshold at which we decide more food must be gathered may chane...)

        if ((self.ResourcesInStock["FoodSupply"] < len(self.__SiidaResidents) * 100)) and self.CryCooldown[0] == 0:
            print("Food's running low!")
            self.CryCooldown[0] += 50
                                                                   #When quantity stuff is repaired, add a quantity of food that will satisfy the crowd for 2 weeks [SUBJECT TO CHANGE W/ BALANCE]
            self.NeededGoals.append(Goal.Goal([Tag.Tag("Deposited"), Tag.Tag("HasFood")], "get some food", 10))
        elif self.CryCooldown[0] > 0:
            self.CryCooldown[0] -= 1

        #Checks to see if we should build any houses...
        #2 People per Lavvu - if we don't have that, we go get some more!      
        LavvuNeeded = math.ceil((len(self.__SiidaResidents) /2) - (len(self.__Lavvu) + self.__LavvuStocked))
        if LavvuNeeded > 0 and self.CryCooldown[1] == 0:
            self.CryCooldown[1] += 1000
            for i in range(LavvuNeeded):              
                self.NeededGoals.append(Goal.Goal([Tag.Tag("BuiltLavvu")], "build a lavvu", 2))
        elif self.CryCooldown[1] > 0:
            self.CryCooldown[1] -= 1

        #Sort our needed goal list so the first goals are the ones that need to be addressed first....
        self.NeededGoals.sort(key=lambda x: x._GetPriority(), reverse=True)
   
        #Sort our residents ascending by the priority of their current goals so those with the least important goals will get assigned goals first
        self.__SiidaResidents.sort(key=lambda x: x._GetActiveGoal()._GetPriority())
       

        #Now we go through our residents and run their daily function..
        for ResIt in self.__SiidaResidents:
            #Take down our food 
            ResIt._DailyFunction(self.NeededGoals)

    #The goal at the front of our needed goal list has been accepted - and so no longer needs to be in the to do list!
    def TakeGoal(self):
        self.NeededGoals.pop(0)
       


    def _GetWorld(self):
        return self.__World

    def _GetLavvu(self):
        return self.__Lavvu


    def _GetLavvuStocked(self):
        return self.__LavvuStocked

    def _SetLavvuStocked(self, Given):
        self.__LavvuStocked = Given

    def _GetSiidaResidents(self):
        return self.__SiidaResidents