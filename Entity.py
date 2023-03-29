
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

        #Mentioned it earlier but will mention it again here
        #We transition between the use of tuples and occasionally lists for our coords 
        #This is because tuple items dont suppourt assignment - which is necessary forus to do.
        #so we change them to lists
        #BUT
        #lists are unhashable so can't be used as dictionary keys
        #Rather than change the larger part of the system, I elected to just have a small bit of code swapping between when necessary 
        self.__Location = ()

        self.__Rep = GivenRep
        self.__Batch = GivenBatch
        self.__Group = GivenGroup

        #Are any AI hunting us down? 
        self._Hunter = None

        if bAutoSpawn == True:
            self._Spawn(GivenLocation)
        
        #e.g.: we wont want to when writing our map cells
    


    #Spawn a sprite for our entity at this point...
    def _Spawn(self, GivenLocation):
        #The entities sprite used for representing it within the world...
        #* 16 as thats the size in pixels of each space on the grid...
        self._Sprite = pyglet.sprite.Sprite(self.__Rep, GivenLocation[0] * 16, GivenLocation[1] * 16, batch=self.__Batch, group=self.__Group)
        self.__Location = GivenLocation

    #Set our sprite location to here
    def _SetSpriteLocation(self, Given):
        self._Sprite.x = Given[0] * 16
        self._Sprite.y = Given[1] * 16
        self.__Location = Given


    #Functionality for removing the entity
    def _Death(self):
        #Ensure our sprite is gone - according to pyglet documentation, occasionally just using del self leaves the sprite there (a bug with pyglet) - this is to ensure it dissapears...

        #If our sprite still exists, delete it!
        self._Sprite.delete()
        del self


    ###
    ###Getters and setters
    ###

    def _GetLocation(self):
        return self.__Location
    
    def _SetLocation(self, Given):
        self.__Location = Given

    def _GetBatch(self):
        return self.__Batch