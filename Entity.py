
import IMGS
import pyglet.sprite 

#An entity is any class which is represented within the world using a sprite
class Entity():
                                                   
    #Constructor
    #Given rep -> the image we will use to represent this entity in the world
    #Given Location -> The location we spawn our entity at
    #Given batch -> The batch we want to add our entity to...
    #__Group ->The draw group (i.e.: what order should it be drawn in...)
    #bAutoSpawn -> should we create this sprite when constructing the entity

    def __init__(self, GivenRep, GivenLocation, GivenBatch, GivenGroup, bAutoSpawn = True):

        self.Location = ()
        self.__Rep = GivenRep
        self._Batch = GivenBatch
        self.__Group = GivenGroup

        #Are any AI hunting us down? 
        self._Hunter = None

        if bAutoSpawn == True:
            self.Spawn(GivenLocation)
        
        #e.g.: we wont want to when writing our map cells
    


    #Spawn a sprite for our entity at this point...
    def Spawn(self, GivenLocation):
        #The entities sprite used for representing it within the world...
        #* 16 as thats the size in pixels of each space on the grid...
        self._Sprite = pyglet.sprite.Sprite(self.__Rep, GivenLocation[0] * 16, GivenLocation[1] * 16, batch=self._Batch, group=self.__Group)
        self.Location = GivenLocation

    #Set our sprite location to here
    def SetSpriteLocation(self, Given):
        self._Sprite.x = Given[0] * 16
        self._Sprite.y = Given[1] * 16
        self.Location = Given


    #Functionality for removing the entity
    def Death(self):
        #Ensure our sprite is gone - according to pyglet documentation, occasionally just using del self leaves the sprite there (a bug with pyglet) - this is to ensure it dissapears...

        #If our sprite still exists, delete it!
        self._Sprite.delete()
        del self
