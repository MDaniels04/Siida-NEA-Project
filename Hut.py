import Entity
import IMGS

class Lavvu(Entity.Entity):
    def __init__(self, GivenRep, GivenLocation, GivenBatch,  bAutoSpawn = True):
        super().__init__(GivenRep, GivenLocation, GivenBatch, IMGS.People, bAutoSpawn)
        
        #Is this Lavvu erected in the world?
        self.bPlaced = False

        print("Plonk! A Lavvu has been erected!")