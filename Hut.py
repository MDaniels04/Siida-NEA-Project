import Entity
import IMGS

#Perhaps this class is a little redundant? The original plan was to add more functionality on spawn - but we are out of time...
class Lavvu(Entity.Entity):
    def __init__(self, GivenRep, GivenLocation, GivenBatch,  bAutoSpawn = True):
        super().__init__(GivenRep, GivenLocation, GivenBatch, IMGS.People, bAutoSpawn)    
        print("Plonk! A Lavvu has been erected!")