#A cloud is a cellular automaton that shrinks every day, but classes the areas it is under as precipitating
import CellularAutomata as CA
import random
import pyglet
import IMGS 
import pyglet
import pyglet.sprite as PS

class Cloud(CA.CellularAutomata):

    #We want all cells that will no longer be covered 
    def _ApplyToMap(self,Movement = (0,0)):

            self.__CloudSprites.clear()

            #Coord we treat the top left of the grid as...
            TopCoord = (self.Location[0] + Movement[0], self.Location[1] + Movement[1])

            #Cells that we are now affecting by the cloud
            NewCells = []
            
            #Iterate through our grid, apply sprites and such to 
            for iC, iV in enumerate(self._Grid):
                if TopCoord[0] + iC < self.__WeatherManager._Owner.GridDims[0]:

                    for jC, jV in enumerate(iV):
                        #Protection of going over map range
                        if TopCoord[1] + jC < self.__WeatherManager._Owner.GridDims[1]:
                            if jV == "~":
                                #Grid locations of where this cloud should be precipitating now...
                                NewCells.append((TopCoord[0] + iC, TopCoord[1] + jC))

                                #We also track the location of that cell in a seperate array so we know which index to delete when we are looking for a sprite at a specific location
            #Update our next position to spawn in...
            self.Location = TopCoord  

            #FUTURE MORGAN FIX HERE!

            #Compare the cells that should be raining now with those that were raining last iteration...
            for Cell in NewCells:         
                if Cell not in self.__AffectingCells:
                    CellObj = self.__WeatherManager._Owner._Grid[Cell[1]][Cell[0]]
                    CellObj.Precipitating = 1
                    if self.__WeatherManager.GlobalTemperature < 0:
                        CellObj.Precipitating = 2

                    NewSprite = pyglet.sprite.Sprite(IMGS.CloudIMG, Cell[1] * 16, Cell[0] * 16, batch=self.__WeatherManager._Owner.DrawBatch, group=IMGS.Weather)
                    NewSprite.opacity = 195
                    self.__CloudSprites.append(NewSprite)
            
            #No cells, so we can class this cloud as gone...
            if len(self.__CloudSprites) < 1:
                self.DestroyCloud()

            self.__AffectingCells = NewCells

    
                    

    def __init__(self, Given_Owner, Age = 0):


        #The weather manager this belongs to - used for accessing data on weather intensity to inform the desicion about whether or not the cloud should increase in size...
        self.__WeatherManager = Given_Owner

        self.Location = (random.randrange(1,26), random.randrange(1,26))

        #To add later when we've integrated the weather component: a function changing the possible dimensions
        #Untill that time lets just say 10x10

        #Our grid is actually a grid of 1s and 0s for our cloud -  we simply take cells as raining - we then apply thbis grid over the world grid and take it as precipitating in those cells!
        super().__init__((25,25), ".")
       
        #Keeps track of the coords of cells we are currently affecting so we can reset their statistics...
        self.__AffectingCells = []
    
        #Sprites visualising the cloud
        self.__CloudSprites = []

        #Cumulative chance for the cloud to be deleted completely...
        self._CloudAge = Age
        
        #If not we are loading a cloud and can manually set our grid...
        if Age == 0:
            self._AddNoiseToGrid("~", ".", 50)
            self._RefineFeature(1, "~", ".", 5, 6)
            self._ApplyToMap()
                
    #Cant use destructor cos we cant access variables after its deleted and we need to ensure the sprites are gone!
    def DestroyCloud(self):
            #Ensure our sprites are gone
            for d in self.__CloudSprites:
                d.delete()
            self.__CloudSprites.clear()
            self.__WeatherManager._CloudsInWorld.remove(self)
            del self
                     
    #Spent a long time trying to think of a name that captured what this does
    #Basically it is the daily progression of each cloud - shrinking in size and moving
    def Degenerate(self):
        self._CloudAge += 1
         
        #Reset precipitation for nearby cells...
        for Cell in self.__AffectingCells:
            CellObj = self.__WeatherManager._Owner._Grid[Cell[1]][Cell[0]]
            CellObj.Precipitating = 0

        if random.randrange(self._CloudAge, 11) == 10:
            self.DestroyCloud()
        else:

        #Our cellular automation algorithm basically will run on the grid for a pass or 2, with differing adjacency
        #We essentially allow our cloud to run itself out this way....
            self._RefineFeature(1, "~", ".", 3,4)
               
            #Generate movement

            XChange = random.randrange(-5,6)
            YChange = random.randrange(-5,6)

            self._ApplyToMap((YChange, XChange))
