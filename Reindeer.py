 
import AI
import IMGS
import Action
import Goal
import Tag

#Reindeer are AI that can roam in the wild, moving as a herd and migrating themselves, or be part of a Siida, staying within the Siida, and migrating when the Siida migrates


class Reindeer(AI.AI):
    
    def __init__(self, GivenRep, GivenWorld, GivenLocation):
        
        super().__init__(GivenRep, GivenWorld, GivenLocation)

        self.PersonalResource = {
        
        "FoodSupply":25

        }        

        self.AvailableActions = self.AvailableActions + [

        ]

        