
#Weather manager manages our clouds and the global temperature

import random
import Cloud as C
import math

class WeatherManager():

    
    def __init__(self, GivenOwner, Saver, GivenTempOffset = -10): 
    
        #We have clouds to load in!
        
        #A list to keep track of what clouds are currently in the world so they can be easily found again for dissapation
        self.__CloudsInWorld = []
    
        #The global temperature (differs on a cell by cell basis due to modifiers in the terrain)                
        self.__GlobalTemperature = 0
    
        #The cumulative chance of spawning a cloud every day
        self.__CumCloudChance = 0


        #Temp offset is the amount we translate the graph by - normally at the start of year it would be -20 degrees, but our offset makes it even colder 
        self.__TempOffset = GivenTempOffset

        self.__Owner = GivenOwner

        if Saver._GetFileToLoad() == True:

            self.__CumCloudChance = Saver._GetSaveData()[6]

            for i in Saver._GetCloudsSaved():
                #Create a new cloud, set this as the grid, etc...
                NewCloud = C.Cloud(self, i[3])
                NewCloud._SetLocation(Saver._ConvertCoordinates(i[1]))
                NewCloud._Grid = Saver._ConvertGrid(i[2], NewCloud._Grid)       
                NewCloud._ApplyToMap()
                self.__CloudsInWorld.append(NewCloud)

        
    def __SpawnCloud(self):
        self.__CloudsInWorld.append(C.Cloud(self))


    def __UpdateTemperature(self, DayNumber):

        #Temperature fluctuation to make it slightly more random
        Fluct =  random.randrange(1,6)       
        self.__GlobalTemperature = round(((-20 * math.cos((2 * math.pi * DayNumber) / 365)) + self.__TempOffset + Fluct), 0)
                                                                             
    #Function ran every "day"
    def _DailyFunction(self):

        '''
    
        Clouds

        '''
        
        #Firstly we update existing clouds by telling them to degenerate..
    
        for Cloud in self.__CloudsInWorld:
            Cloud._Degenerate()
        
        #Chance to spawn a cloud, if not increase cumultaive  chance
        
        #Max number of clouds at once is 4...

        #Else we dont even touch our cumulative cloud chance...
        if len(self.__CloudsInWorld) < 4:

            Chance = random.randrange(self.__CumCloudChance, 15)

            if Chance == 14:
                self.__SpawnCloud()
                self.__CumCloudChance = 0

            else:
                self.__CumCloudChance += 1

        '''

        TEMPERATURES        

        '''
        
        self.__UpdateTemperature(self.__Owner._GetTime()._GetDayNumber())
              
            
            

             
            
    def _GetCloudsInWorld(self):
        return self.__CloudsInWorld
    
    def _GetGlobalTemperature(self):
        return self.__GlobalTemperature

    def _GetCumulativeCloudChance(self):
        return self.__CumCloudChance

    def _GetOwner(self):
        return self.__Owner