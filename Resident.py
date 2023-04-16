#Resident is an AI belonging to the siida.
import AI
import Action
import Tag
import random

#Its like a reindeer but has far more actions available to it....

class Resident(AI.AI):
    #Overload of entity allows for option of sprite creation and spawning in the constructor - disabled by default so the 
    #If bLoading is true we do not need to spend any time on calculating values for these - they will be given to us...
    def __init__(self, GivenRep, GivenWorld, SpawnLocation, GivenSiida, bLoading = False):

        #The siida this entity belongs to - effects the available actions to this entity and goal assignment
        self.__Siida = GivenSiida

        self.__Name = ""
        
        #0 - 100 - hown hungry are we? If this hits 100, we die!!
        self.__Hunger = 0

        #0 - 100 - how exposed to the elements (cold) are we? If this hits 100, we die!
        self.__Expsoure = 0

        #An entity we have been trying to findgoes here once found...
        self.__Found = None

        self.__CarryingResources = None

        if bLoading == False:

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
            self.__Name = Names[random.randint(0, (len(Names) - 1))]

            print(self.__Name, "has joined the Siida!")

            #What resources are we currently carrying? While we carry stuff we have got back to the "siida". Doesn't really affect things except if we die on our way back to the siida
            self.__CarryingResource = {
        
            "FoodSupply": 0,

            "WoodSupply": 0
        
            }

        super().__init__(GivenRep, GivenWorld, SpawnLocation)

        self._SetAvailableActions(self._GetAvailableActions() + [

                #Find (& hunt) a reindeer...
                Action.Find([Tag.Tag("FoundPrey")], True, self._GetWorld()._GetReindeer(), "Look for a reindeer to hunt"),

                #Track what we have __Found...
                Action.Hunt([Tag.Tag("KilledPrey")], True, "Hunt their prey", 1, [Tag.Tag("FoundPrey")]),

                #In preperation for migration pack up a lavvu
                Action.Find([Tag.Tag("FoundLavvu")], True, self.__Siida._GetLavvu(), "find a lavvu to pack up in preperation for migration"),

                #Go towards a lavvu and pack it up - after this action is performed we will likely wander again - meaning we will go to a random location in the Siida - and hence move to the new siida location...
                                                                                                                               #Only want to be able to do this in a migration
                Action.PackLavvu([Tag.Tag("LavvuReady")], False, "pack up the lavvu they found", 1, [Tag.Tag("FoundLavvu"), Tag.Tag("PackingAbility")]),

                #Go to the Siida, should we find ourselves outside of it and need to deposit stuff...            
                Action.Return([Tag.Tag("At_SiidaCentre")], True, "go back to the Siida"),
            
                #Consider this a fishing action - going to the coast to get some fish!
                Action.GoToType([Tag.Tag("AtCoast")], True, self._GetWorld()._GetSeaCoords(),  "go to a fishing spot", 1),

                #Get the food from a reindeer carcass
                Action.Get([Tag.Tag("HasFood")], False, "FoodSupply", 500, "gather food from the carcass", 1,[Tag.Tag("KilledPrey")]),
        
                #Consider this a "fishing" action
                Action.Get([Tag.Tag("HasFood")], False, "FoodSupply", 250, "fish", 1, [Tag.Tag("AtCoast")]),

                #Go to a forest to get some wood!
                Action.GoToType([Tag.Tag("AtForest")], True, self._GetWorld()._GetForestCoords(), "gather wood from the forest", 1),

                #Chop down some trees at a forest...                                                  We want em to unpack if they can
                Action.Get([Tag.Tag("LavvuReady")], False, "WoodSupply", 10, "chop down some trees", 500, [Tag.Tag("AtForest")]),

                #Build a lavvu
                Action.BuildLavvu([Tag.Tag("BuiltLavvu")], False, "build a lavvu to rest their weary bones!", 1,  [Tag.Tag("AtBuildSite"), Tag.Tag("Deposited"), Tag.Tag("LavvuReady")]),

                #Go to a location in Siida
                Action.GoToInSiida([Tag.Tag("AtBuildSite")], True, "find a place in the Siida to build!", 1),

                #Deposit resources back at the Siida.
                Action.Deposit([Tag.Tag("Deposited")], False, "drop off the food at the Siida", 1, [Tag.Tag("At_SiidaCentre")])
           
            ])
    
    #Resident's version of _Death will take any goals we were undertaking and pop them back into the Siida's needed goal's list...
    def _Death(self, Reason):

        #Flavour text to better understand
        print(self.__Name, " has died due to ", Reason)

        #If we were working to fulfill a goal, then we want it to go back on to the needed goals to allow others to do it!
        if self._GetActiveGoal() != None and self._GetActiveGoal()._GetPriority() > 0:
            self.__Siida.NeededGoals.append(self._GetActiveGoal())


        self.__Siida._GetSiidaResidents().remove(self)
        super()._Death()

    #Overload of daily function to check for temperature...
    def _DailyFunction(self, NeededGoals = []):
        
        #Our exposure increases if we are in a cold place

        TempDiff = self._GetWorld()._Grid[self._GetLocation()[1]][self._GetLocation()[0]]._GetTemperature(self._GetWorld()._GetWeather()._GetGlobalTemperature()) + 25
        if TempDiff < 0:
            self.__Expsoure += abs(TempDiff * 5)
        else:
            self.__Expsoure = 0

        if self.__Expsoure >= 500:
            self._Death("overexposure to the cold!")
            pass
        else:
            FoodDiff = self.__Siida.ResourcesInStock["FoodSupply"] - 5
            if FoodDiff >= 0:
                self.__Siida.ResourcesInStock["FoodSupply"] -= 5
                self.__Hunger = 0
            else:
                self.__Siida.ResourcesInStock["FoodSupply"] = 0
                self.__Hunger += FoodDiff 

            if self.__Hunger >= 100:
                self._Death("starvation!")
                pass
            else:
                super()._DailyFunction(NeededGoals)

    ##
    #GETTERS AND SETTERS
    ##

    def _GetSiida(self):
        return self.__Siida

    def _GetName(self):
        return self.__Name
       
    def _SetName(self, Given):
        self.__Name = Given

    def _GetHunger(self):
        return self.__Hunger

    def _SetHunger(self, Given):
        self.__Hunger = Given

    def _GetFound(self):
        return self.__Found

    def _SetFound(self, Given):
        self.__Found = Given

    def _GetCarryingResources(self):
        return self.__CarryingResource

    def _SetCarryingResources(self, Key, Amount):
        self.__CarryingResource[Key] += Amount