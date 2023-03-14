import Resident
import random
import IMGS
import math
import Goal
import Tag
import pickle

#Siida management manages the residents in our Siida - essentially assigning goals to them

#Apologies for slightly confusing file name, our main file is called Siida so we couldnt call it that

class Siida():

    #A function to return a random land coordinate within a certain radius of what we take the siida to be - this will mean people will spawn together, and build structures in largely the same area....    
    def GetLocationInSiida(self):
        #Get which land coords satisfy the radius, then pick a random one

        InBounds = []
        for It in self.World.LandCoords:
            #Copy pasted Manhattan distance from A* - its not much repeated code I spose, and otherwise we get circular import problemos...
            if (abs(It[0] - self.CentreLocation[0]) + abs(It[1] - self.CentreLocation[1])) <= self.SiidaRadius:
                InBounds.append(It)
                #NOT CALLING HERE              

        return InBounds[random.randrange(0, len(InBounds))]

    #Created at the start of the game...
    # Spawn radius is the distance around the main point we class this Siida at
    def __init__(self, StartingMembers, SpawnRadius, GivenWorld, Saver):

        #Find a point for our Siida to put themselves in the meantime...

        self.World = GivenWorld 

        self.SiidaRadius = 5

        #The Lavvu in our world!
        self.Lavvu = []

        self.SiidaResidents = []
        

        #ADD SAVES FOR THIS 
        #How many days should we wait before sending out another request for a goal? Indexes are as follows
        #0 -> Food cry
        #1 -> Build lavvu cry
        self.CryCooldown = [0, 0]

        if Saver.bFileToLoad == True:
            
            #We need to convert the stored coordinates, remember...
            self.CentreLocation = Saver.ConvertCoordinates(Saver.SaveData[3])           
                
            #As it were saved...
            self.NeededGoals = pickle.loads(Saver.SaveData[4])
            
            self.ResourcesInStock = {
                "FoodSupply":Saver.SaveData[5]
            }
            

            #Now we need to load up our residents again...
            self.SiidaResidents = []
            for i in Saver.ResidentData:
        
                #Reconstruct these members from all the variables...

                OldResident = Resident.Resident(IMGS.PersonIMG, self.World, Saver.ConvertCoordinates(i[10]), self)

                OldResident.CurrentState = i[1]
                OldResident.ActionQueue = pickle.loads(i[2])
                OldResident.ActiveTags = pickle.loads(i[3])
                OldResident.ActiveGoal = pickle.loads(i[4])
                OldResident.ActiveAction = pickle.loads(i[5])
                OldResident.MoveQueue = pickle.loads(i[6])
                OldResident.Hunter = pickle.loads(i[7])
                OldResident.Hunting = pickle.loads(i[8])
                OldResident.GoalLocation = Saver.ConvertCoordinates(i[9])
                #Dont need to set location, already handled that gubbins
                OldResident.Name = i[11]

                self.SiidaResidents.append(OldResident)      
        else:

            #Here we are specifying a coord to be taken as the current centre of the Siida -
            self.CentreLocation = self.World.LandCoords[random.randrange(0, len(self.World.LandCoords))]
       

            #Spawn in our initial siida members
            for it in range(0, StartingMembers):
 
                self.SiidaResidents.append(Resident.Resident(IMGS.PersonIMG, self.World,  self.GetLocationInSiida(), self))
           

            #Each member of the Siida will eat 5 arbitrary food units a day - this is enough food for a month  
            #Seems like a lot but trust me its gonna get scarce....    

            #Tracking what structres are in the siida - need to be all packed up in order to migrate...

            self.StructuresInSiida = []
                          
            self.ResourcesInStock = {
           
                #Food is consumed by each resident, 5 a day
                #When residents don't have enough food, they will get the hungry tag. If they remain hungry for a week, they die.
                "FoodSupply":len(self.SiidaResidents) * 150,

                #Wood is used for the construction of lavvu and the burning of fires
                #Running out of wood can be either a none issue in summer, or a catastrophe in winter when wood is vital for staying warm
                "WoodSupply": 25,

                #More resources????
            }

            #What goals do the Siida currently need to pay attention to?
            self.NeededGoals = []

    #Choose a location that we will migrate to - dependant upon what stage in the migration cycle we are set to hit...
    def UpdateSiidaLocation(TerrainTypeList):
       
        #We will be handed a differing terrain type list depending on the season of migration taking place
        #We pick that new location

        #Might want to add protection for the area being too small, but that might also come with the refinement of the shapes that the map generates in...

        return TerrainTypeList[random.randrange(0, len(TerrainTypeList))]

    #The function run every day, checking the stats of the siida and assigning goals if the problem arises....
    def DailyFunction(self):

        #Update of statistics
   
        self.ResourcesInStock["FoodSupply"] -= (len(self.SiidaResidents) * 5)

        #Now we address any goals that need passing out....
         
        #If there is less than enough food for a week left, we need to get more (the threshold at which we decide more food must be gathered may chane...)

        if ((self.ResourcesInStock["FoodSupply"] < len(self.SiidaResidents) * 100)) and self.CryCooldown[0] == 0:
            print("Food's running low!")
            self.CryCooldown[0] += 50
                                                                   #When quantity stuff is repaired, add a quantity of food that will satisfy the crowd for 2 weeks [SUBJECT TO CHANGE W/ BALANCE]
            self.NeededGoals.append(Goal.Goal([Tag.Tag("Deposited"), Tag.Tag("HasFood")], "get some food", 10))
        elif self.CryCooldown[0] > 0:
            self.CryCooldown[0] -= 1



        #Checks to see if we should build any houses...
        #If we have more people than we have lavvu, we should build a house...        
        LavvuNeeded = len(self.SiidaResidents) - len(self.Lavvu) * 2
        if(LavvuNeeded != 0) and self.CryCooldown[1] == 0:
            for i in range(LavvuNeeded):
                self.CryCooldown[1] += 50
                self.NeededGoals.append(Goal.Goal([Tag.Tag("BuiltLavvu")], "build a lavvu", 5))
        elif self.CryCooldown[1] > 0:
            self.CryCooldown[1] -= 1
    

        #Sort our needed goal list so the first goals are the ones that need to be addressed first....
        self.NeededGoals.sort(key=lambda x: x.Priority, reverse=True)
   
        #Sort our residents ascending by the priority of their current goals so those with the least important goals will get assigned goals first
        self.SiidaResidents.sort(key=lambda x: x.ActiveGoal.Priority)
       

        #Now we go through our residents and run their daily function..
        for ResIt in self.SiidaResidents:

            #Take down our food 
            ResIt.DailyFunction(self.NeededGoals)

    #The goal at the front of our needed goal list has been accepted - and so no longer needs to be in the to do list!
    def TakeGoal(self):
        self.NeededGoals.pop(0)
       
    #The goal to migrate is given at the same time every year
    #Febuary -> Mountain calving grounds...
