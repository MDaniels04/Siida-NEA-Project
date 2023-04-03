#World is - erm - our world - tracks statistics about what affects our world, its climate, and the none  
import CellularAutomata as CA
import Cell 
import IMGS
import WeatherManager as W
import Time as T
import pyglet.sprite as PS
import Reindeer
import SiidaManagement as SM
import random
import Goal
import Tag
import pickle

class World(CA.CellularAutomata):

    #Utility function adds the map cells to the batch thats drawn
    #Used in init and if any of the map cells should change [I.E.: THEY ARE SNOWED ON]
    def __AddSelfToBatch(self):

        StartX = 0
        StartY = 0
    
        #We trust that we will have handed popping of old sprites before hand...

        for i in self._Grid:
            for j in i:
                j._Spawn((StartY, StartX))
                self.__MapSprites.append(j._Sprite)
                #self.__MapSprites.append(j)

                #Cell weight initially unique so we use this to ID our cells


                #As double digits of AI could have the task of searching for a certain type of cell, then discerning the closest, then constructing a pathfinding route to that, I decided to streamline the process a little by filling an array with coordinates of types of cell
                #AI may want to pathfind to. Its not the most efficient right now, but it will save time in thbe long run - trust me, w/o this we had a half-second delay or so from when the day should fire if this happened en mass...                

                if j._GetWeight() != 10000:

                    self.__LandCoords.append((StartY, StartX))

                    #We also fill lists of types of cells for easier identification - for example, rather than having an algorithm searching for tiles, we simply fill the lists, then have them iterated through and 
                    if j._GetWeight() == 1:
                        self.__ForestCoords.append((StartY, StartX)) 
                   

                    elif j._GetWeight() == 50:

                        #As you've likely guessed, storing where mountains are in the worldight == 50:
                        self.__MountainCoords.append((StartY, StartX))
                    else:
      
                        self.__LowlandCoords.append((StartY, StartX))
                else:
                    self.__SeaCoords.append((StartY, StartX))

                StartX += 1
            StartX = 0
            StartY += 1

    #Create amap using cellular automata, and initialise the other important components of our world
    #bLoading world will determine if we generate a new map or if we dont, assuming we are supplied with one...
    def __init__(self, GivenDims, GivenDrawBatch, Saver):  

        #All the world's components hand their sprites back to this batch so we can draw them all in main...
        self.__DrawBatch = GivenDrawBatch      
          

         #Different kinds of cells
        SeaCell = Cell.Cell(IMGS.CoastIMG, 10000, (0,0), self.__DrawBatch, "S", 1)
        LandCell = Cell.Cell(IMGS.LandIMG,  0, (0,0), self.__DrawBatch, "L", 0)
        HillCell = Cell.Cell(IMGS.HillIMG, 2, (0,0), self.__DrawBatch, "H",-5)
        MountainCell = Cell.Cell(IMGS.MountainIMG, 50, (0,0), self.__DrawBatch, "M",-15)
        ForestCell = Cell.Cell(IMGS.TreeIMG, 1, (0,0), self.__DrawBatch, "F",5)


        '''

        Map creation

        '''
        super().__init__(GivenDims, SeaCell)


        self.__MapSprites = []
       

        #Decided to store lists of coordinates of a type of cell to simplify the process of finding the closest ones of a type - rather than have to spiral outwards from a location
        #checking if it is a correct type, we can simply find the closest coord from a likst

        #An array storing the coordinates of cells that aren't in the sea - used for finding locations to spawn entities... 
        self.__LandCoords = []
    
        #Basic land cells
        self.__LowlandCoords = []

        #Same thing for sea cells 
        self.__SeaCoords = []

        #The difference between this and the above is the above stores where has the wood resource - and shrinks as trees are cut down... This is the forest tiles - tree or not.
        self.__ForestCoords = []

        #As you've likely guessed, storing where mountains are in the world
        self.__MountainCoords = []

        #Our weather manager, dealing with the weather across the world.
        self.__Weather = W.WeatherManager(self, Saver)
    
        self.__Time = T.TimeManager(self)


        #Reindeer currently in the world...
        self.__Reindeer = []

        if Saver._GetFileToLoad() == True:
            self.__Time._SetDayNumber(Saver._GetSaveData()[1])
            
            #Get our uncompressed map, add it on...

            self._Grid =  Saver._ConvertGrid(Saver._GetSaveData()[2], self._Grid, S = SeaCell, L = LandCell, H = HillCell, F = ForestCell, M = MountainCell,)
            
            self.__Weather.CumCloudChance = Saver._GetSaveData()[6]            

            #Map is sorted

            #Add our AI in...


            for i in Saver._GetAIData():

                OldReindeer = Reindeer.Reindeer(IMGS.ReindeerIMG, self, Saver._ConvertCoordinates(i[10]))

                OldReindeer.CurrentState = i[1]
                OldReindeer.ActionQueue = pickle.loads(i[2])
                OldReindeer.ActiveTags = pickle.loads(i[3])
                OldReindeer.ActiveGoal = pickle.loads(i[4])
                OldReindeer.ActiveAction = pickle.loads(i[5])
                OldReindeer.MoveQueue = pickle.loads(i[6])
                OldReindeer.Hunter = pickle.loads(i[7])
                OldReindeer.GoalLocation = Saver._ConvertCoordinates(i[9])
            
                self.__Reindeer.append(OldReindeer)
            self.__AddSelfToBatch()
            

        else:

            #Land on sea
            self._AddNoiseToGrid(LandCell, SeaCell, 35)
            self._RefineFeature(5, LandCell, SeaCell, 4,4)


            #Hills on land
            self._AddNoiseToGrid(HillCell, LandCell, 48)
            self._RefineFeature(5, HillCell, LandCell, 4,6)

            #EDIT SHAPES THEY UGLY DANG
    
            #Mountain on hills
            self._AddNoiseToGrid(MountainCell, HillCell, 90)
            self._RefineFeature(2, MountainCell, HillCell, 6,5)

            self._AddNoiseToGrid(ForestCell, LandCell, 90)
            self._RefineFeature(4, ForestCell, LandCell, 6,7)

            self.__AddSelfToBatch()
        
            #Randomly spawn some reindeer...
            for i in range(1,7):
                self.__Reindeer.append(Reindeer.Reindeer(IMGS.ReindeerIMG, self, self.__LandCoords[random.randrange(0, len(self.__LandCoords))]))
        
            '''

            Spawn our "Siida" 

            '''     

        #The siida constructor itself will handle if we need to load data or create new stuff
        self.Siida = SM.Siida(10, 5, self, Saver)

    #The world's daily function :)
    def _DailyFunction(self):
        self.__Weather._DailyFunction()
        self.Siida._DailyFunction()

        for Rein in self.__Reindeer:
           Rein._DailyFunction()


    def _GetDrawBatch(self):
        return self.__DrawBatch

    def _GetLandCoords(self):
        return self.__LandCoords

    def _GetLowlandCoords(self):
        return self.__LowlandCoords

    def _GetSeaCoords(self):
        return self.__SeaCoords

    def _GetForestCoords(self):
        return self.__ForestCoords

    def _GetMountainCoords(self):
        return self.__MountainCoords

    def _GetWeather(self):
        return self.__Weather

    def _GetTime(self):
        return self.__Time

    def _GetReindeer(self):
        return self.__Reindeer