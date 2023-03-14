#Resident is an AI belonging to the siida.
import AI
import Action
import Tag
import random

#Its like a reindeer but has far more actions available to it....

class Resident(AI.AI):
    #Overload of entity aloows for option of sprite creation and spawning in the constructor - disabled by default so the 
    def __init__(self, GivenRep, GivenWorld, SpawnLocation, GivenSiida):

        #The siida this entity belongs to - effects the available actions to this entity and goal assignment
        self.Siida = GivenSiida

        #Most of these are Sami names, according to https://www.nordicnames.de/wiki/Category:Sami_Names
        #Of course, I have smuggled in the odd reference name...                                                                                                            
        Names = [

        #These are all real
        "Ruigi", "Speadina", "Bierdn", "Sire", "Gustu", "Nigo", "Migil", "Filpa", "Juhvo", "Johanas", "Duvká", "Olen", "Ailo", "Egel", "Benne",  "Dure", "Buohttá", "Aron", 

        #Joke names / References past this point

        "Utrid", 
        "Dovahkiin",

        #I reckoned I wouldnt get away with sans or papyrus :(
        "Toriel", "Alphy", "Asgore", "Undyne", "Frisk"]

        #For the flavour texts purpose, so we get an idea of who's doing what...
        self.Name = Names[random.randint(0, (len(Names) - 1))]

        print(self.Name, "has joined the Siida!")

        #What resources are we currently carrying? While we carry stuff we have got back to the "siida". Doesn't really affect things except if we die on our way back to the siida
        self.CarryingResource = {
        
        "FoodSupply": 0,

        "WoodSupply": 0
        
        }
    

        self.PersonalResource = {

        #For now same food as a reindeer.... dk how likely this is to remain the same...
        "FoodSupply": 25
        
        }
        super().__init__(GivenRep, GivenWorld, SpawnLocation)

        #We want to get to the reindeer...

        self.AvailableActions = self.AvailableActions + [

                #Find (& hunt) a reindeer...
                Action.Find([Tag.Tag("CaughtPrey")], True, self.World.Reindeer, "hunt a reindeer"),


                Action.Kill([Tag.Tag("KilledPrey")], False, "kill their prey", 1, [Tag.Tag("CaughtPrey")]),

                #Go to the Siida, should we find ourselves outside of it and need to deposit stuff...            
                Action.GoTo([Tag.Tag("AtSiidaCentre")], True, "go back to the Siida", self.Siida.CentreLocation),
            
                #Consider this a fishing action - going to the coast to get some fish!
                Action.GoToType([Tag.Tag("AtCoast")], True, self.World.SeaCoords,  "go to a fishing spot", 1),

                #Get the food from a reindeer carcass
                Action.Get([Tag.Tag("HasFood")], False, "FoodSupply", 1, "gather food from the carcass", 1,[Tag.Tag("KilledPrey")]),
        
                #Consider this a "fishing" action
                Action.Get([Tag.Tag("HasFood")], False, "FoodSupply", 250, "fish", 1, [Tag.Tag("AtCoast")]),

                #Go to a forest to get some wood!
                Action.GoToType([Tag.Tag("AtForest")], True, self.World.ForestCoords, "gather wood from the forest", 1),

                #Chop down some trees at a forest...
                Action.Get([Tag.Tag("Wood")], False, "WoodSupply", 250, "chop down some trees", 1, [Tag.Tag("AtForest")]),

                #Build a lavvu
                Action.BuildLavvu([Tag.Tag("BuiltLavvu")], False, "build a lavvu to rest their weary bones!", 1,  [Tag.Tag("Wood")]),

                #Go to a location in Siida
                #Action.GoToInSiida([Tag.Tag("AtBuildSite")], True, "find a place in the Siida to build!", 1),

                #future morgan, implement this action here - problems come from not checking that goals tags are still met - if we performa ctions we r assuming we have tags....
                Action.Deposit([Tag.Tag("Deposited")], False, "drop off the food at the Siida", 1, [Tag.Tag("AtSiidaCentre")])
                
            ]
    
        self.ActiveTags = self.ActiveTags + [

            Tag.Tag("InSiida")
        ]

    #Resident's version of death will take any goals we were undertaking and pop them back into the Siida's needed goal's list...
    def Death(self):
        super().Death()

        if self.ActiveGoal != None:
            self.Siida.NeededGoals.append(self.ActiveGoal)


    #Overload sets the sprite location, but with checks as to whether or not this moves them in / out of the Siida
    def SetSpriteLocation(self, Given):    
        super().SetSpriteLocation(Given)

        Found = None  
        for iC, iV in enumerate(self.ActiveTags):
            if iV.TagName == "InSiida":
                Found = iC
        #Done this way as if tags have the same name they are still different objects and not the same value - so we couldnt just remove Tag.Tag("InSiida") because thats a different object to the one we would've appended         


        #If we found it, we want to check for leaving the Siida...
        if Found != None:
            
            if (abs(self.Location[0] - self.Siida.CentreLocation[0]) + abs(self.Location[1] - self.Siida.CentreLocation[1])) > self.Siida.SiidaRadius:
                self.ActiveTags.pop(iC)
                print(self.Name, " has walked outside of the siida...")

        #If not we are checking for moving into the Siida to append the tag
        else:
            
            if (abs(self.Location[0] - self.Siida.CentreLocation[0]) + abs(self.Location[1] - self.Siida.CentreLocation[1])) <= self.Siida.SiidaRadius:
                self.ActiveTags.append(Tag.Tag("InSiida"))
                print(self.Name, " has walked inside of  the siida...")