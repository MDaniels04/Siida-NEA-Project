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
    def AddSelfToBatch(self):

        StartX = 0
        StartY = 0
    
        #We trust that we will have handed popping of old sprites before hand...

        for i in self._Grid:
            for j in i:
                j.Spawn((StartY, StartX))
                self.MapSprites.append(j._Sprite)
                #self.MapSprites.append(j)

                #Cell weight initially unique so we use this to ID our cells


                #As double digits of AI could have the task of searching for a certain type of cell, then discerning the closest, then constructing a pathfinding route to that, I decided to streamline the process a little by filling an array with coordinates of types of cell
                #AI may want to pathfind to. Its not the most efficient right now, but it will save time in thbe long run - trust me, w/o this we had a half-second delay or so from when the day should fire if this happened en mass...                

                if j._Weight != 10000:

                    self.LandCoords.append((StartY, StartX))

                    #We also fill lists of types of cells for easier identification - for example, rather than having an algorithm searching for tiles, we simply fill the lists, then have them iterated through and 
                    if j._Weight == 1:
                        self.ForestCoords.append((StartY, StartX)) 
                    
                    elif j._Weight == 2:
                        self.HillCoords.append((StartY, StartX))

                    elif j._Weight == 50:
                        self.MountainCoords.append((StartY, StartX))
                    else:
      
                        self.LowlandCoords.append((StartY, StartX))
                else:
                    self.SeaCoords.append((StartY, StartX))

                    #For now, lets say there is 10 food in places with fish....
                    j.ResourcesInCell["FoodSupply"] = 10
        

                StartX += 1
            StartX = 0
            StartY += 1

    #Create amap using cellular automata, and initialise the other important components of our world
    #bLoading world will determine if we generate a new map or if we dont, assuming we are supplied with one...
    def __init__(self, GivenDims, GivenDrawBatch, Saver):  

        #All the world's components hand their sprites back to this batch so we can draw them all in main...
        #Fairly sure it all in one batch is correct, right?
        self.DrawBatch = GivenDrawBatch      
          

         #Different kinds of cells
        SeaCell = Cell.Cell(IMGS.CoastIMG, 10000, (0,0), self.DrawBatch, "S", 1)
        LandCell = Cell.Cell(IMGS.LandIMG,  0, (0,0), self.DrawBatch, "L", 0)
        HillCell = Cell.Cell(IMGS.HillIMG, 2, (0,0), self.DrawBatch, "H",-5)
        MountainCell = Cell.Cell(IMGS.MountainIMG, 50, (0,0), self.DrawBatch, "M",-15)
        ForestCell = Cell.Cell(IMGS.TreeIMG, 1, (0,0), self.DrawBatch, "F",5)


        '''

        Map creation

        '''
        super().__init__(GivenDims, SeaCell)


        self.MapSprites = []
       
        #An array storing the coordinates of cells that aren't in the sea - used for finding locations to spawn entities... 

        self.LandCoords = []
    
        #Basic land cells
        self.LowlandCoords = []

        #Same thing for sea cells 
        self.SeaCoords = []

        #The difference between this and the above is the above stores where has the wood resource - and shrinks as trees are cut down... This is the forest tiles - tree or not.
        self.ForestCoords = []

        #Storing where hills are on the map
        self.HillCoords = []

        self.MountainCoords = []


        #Our weather manager, dealing with the weather across the world.
        self.Weather = W.WeatherManager(self, Saver)
    
        self.Time = T.TimeManager(self)


        #Reindeer currently in the world...
        self.Reindeer = []

        if Saver.bFileToLoad == True:
            self.Time.DayNumber = Saver.SaveData[1]
            
            #Get our uncompressed map, add it on...

            self._Grid =  Saver.ConvertGrid(Saver.SaveData[2], self._Grid, S = SeaCell, L = LandCell, H = HillCell, F = ForestCell, M = MountainCell,)
            
            self.Weather.CumCloudChance = Saver.SaveData[6]            

            #Map is sorted

            #Add our AI in...


            for i in Saver.AIData:

                OldReindeer = Reindeer.Reindeer(IMGS.ReindeerIMG, self, Saver.ConvertCoordinates(i[10]))

                OldReindeer.CurrentState = i[1]
                OldReindeer.ActionQueue = pickle.loads(i[2])
                OldReindeer.ActiveTags = pickle.loads(i[3])
                OldReindeer.ActiveGoal = pickle.loads(i[4])
                OldReindeer.ActiveAction = pickle.loads(i[5])
                OldReindeer.MoveQueue = pickle.loads(i[6])
                OldReindeer.Hunter = pickle.loads(i[7])
                OldReindeer.GoalLocation = Saver.ConvertCoordinates(i[9])
            
                self.Reindeer.append(OldReindeer)
            self.AddSelfToBatch()
            

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

            self.AddSelfToBatch()
        
            #Randomly spawn some reindeer...
            #for i in range(1,7):
                #self.Reindeer.append(Reindeer.Reindeer(IMGS.ReindeerIMG, self, self.LandCoords[random.randrange(0, len(self.LandCoords))]))
        
            '''

            Spawn our "Siida" 

            '''     

        #The siida constructor itself will handle if we need to load data or create new stuff
        self.Siida = SM.Siida(10, 5, self, Saver)

    #The world's daily function :)
    def DailyFunction(self):
        self.Weather.DailyFunction()
        self.Siida.DailyFunction()

        for Rein in self.Reindeer:
           Rein.DailyFunction()
