
#Weather manager manages our clouds and the global temperature

import random
import Cloud as C
import math

class WeatherManager():

    
    def __init__(self, GivenOwner, Saver, GivenTempOffset = -10): 
    
        #We have clouds to load in!
        
        #A list to keep track of what clouds are currently in the world so they can be easily found again for dissapation
        self.CloudsInWorld = []
    
        #The global temperature (differs on a cell by cell basis due to modifiers in the terrain)                
        self.GlobalTemperature = 0
    
        #The cumulative chance of spawning a cloud every day
        self.CumCloudChance = 0


        #Temp offset is the amount we translate the graph by - normally at the start of year it would be -20 degrees, but our offset makes it even colder 
        self.TempOffset = GivenTempOffset

        self.Owner = GivenOwner

        if Saver.bFileToLoad == True:

            self.CumCloudChance = Saver.SaveData[6]

            for i in Saver.CloudsSaved:
                #Create a new cloud, set this as the grid, etc...
                NewCloud = C.Cloud(self, i[3], Saver.ConvertCoordinates(i[1]))
                NewCloud.Grid = Saver.ConvertGrid(i[2], NewCloud.Grid)       
                NewCloud.ApplyToMap()
                self.CloudsInWorld.append(NewCloud)

        
    def __SpawnCloud(self):
        self.CloudsInWorld.append(C.Cloud(self))


    def __UpdateTemperature(self, DayNumber):

        #Temperature fluctuation to make it slightly more random
        Fluct =  random.randrange(1,6)       
        Temp = round(((-20 * math.cos(2 * math.pi * DayNumber) / 365) + self.TempOffset + Fluct), 0)
                                                                     #Change 365 to year length when we add leap years!
        self.GlobalTemperature =  round(Temp, 1)
        
      
    #Function ran every "day"
    def DailyFunction(self):

        '''

        Clouds

        '''
        
        #Firstly we update existing clouds by telling them to degenerate..
    
        for Cloud in self.CloudsInWorld:
            Cloud.Degenerate()
        
        #Chance to spawn a cloud, if not increase cumultaive  chance
        
        #Max number of clouds at once is 4...

        #Else we dont even touch our cumulative cloud chance...
        if len(self.CloudsInWorld) < 4:

            #Randrange is not inclusive for the upper bound, apparently 
            Chance = random.randrange(self.CumCloudChance, 15)

            if Chance == 14:
                self.__SpawnCloud()
                self.CumCloudChance = 0

            else:
                self.CumCloudChance += 1

        '''

        Temperature

        '''
        
        self.__UpdateTemperature(self.Owner.Time.DayNumber)
              
            
            

             
            
    
    