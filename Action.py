import Goal
import Tag
import math
import random
import Hut
import IMGS

#An action is a child of goal with effects and functionality around "performing" it
class Action(Goal.Goal):
   
    #Constructor
    #Given effect tags <- The tags this action will grant upon its completion
    #Interruptable <- Whether or not this action can be stopped part way through...
    #Given goal name <- The text to display in the console to identify it when functionality is called
    #Given weight <- The weight assigned to completing this action
    #Giveb prerequisite tags <- The tags we want AI to have before being able to do this action
    #Given removes tags <- Tags in addition to this action's prerequisites completing it will remove
    def __init__(self, GivenEffectTags, Interruptable, GivenGoalName, GivenWeight = 1,  GivenPrerequisiteTags = [], GivenRemovesTags = []):
        super().__init__(GivenPrerequisiteTags, GivenGoalName)


        self._bInterruptable = Interruptable    
        self._EffectTags = GivenEffectTags
        self._RemovesAdditionalTags = GivenRemovesTags
        self._Weight = GivenWeight

        #MORGZ FINISH THIS HERE
        #How much weight will failing this action add to the 
        self._FailureWeightOffset = 5

        #Can this action be repeated or not (If it is finite, tags will be appended upon completion, else they will not)
        self._bFinite = True

    #The action did not succeed and we need to replan
    #Performer <- The performer who failed to do the action
    #Reason <- Text string to print in the console for the purpose of giving more insight into why an action failed
    def ActionFailed(self, Performer, Reason = None):
        
        try:
            #Print this "flavour text"
            print(Performer.Name, " wasn't able to ", self.GoalName, Reason if Reason != None else " - something went wrong!")   

        #If they don't have a name (i.e.: aren't a resident) this will throw an except - in which case we dont want any flavour text  
        except:
            pass   

        Performer._ActionFailed()


    #Do the thing actually detailed in the action....
    #Base action functionality is simply ensuring we know that we have the correct tags before continuing
    #Performer <- The AI performing this action
    def PerformAction(self, Performer):
        Performer._ActiveAction = self

        #Check we have the necessary tags to perform this action. If we do not we need to plan for this goal again, as something has gone wrong :(
        for PrereqIt in self.Prereqs:
            bFound = False
            for ActiveIt in Performer._ActiveTags:
                if ActiveIt.TagName == PrereqIt.TagName:
                    bFound = True
            #Performer didn't have the necessary tags
            if bFound == False:
                    self.ActionFailed(Performer, "they didn't have the right tags!")
            else:
                #We only want to print info for residents as the console will likely be cluttered enough as it is...
                try:
                    print(Performer.Name, " is going to ", self.GoalName, "!")
                except:
                    pass

    #Append our effect tags, remove our remove tags
    #A function we keep seperate from the main perform action function as some actions will not end within the same call that they begin (& actions may not be succesful so we don't always want this)
    #Performer <- The AI performing this action
    def ActionComplete(self, Performer):
       
        Performer._ActiveAction = None

        #If we are supposed to only do this action once
        if self._bFinite:

            #Update the tags of our performer
            for TagIt in self._EffectTags:
                if TagIt not in Performer._ActiveTags:
                    Performer._ActiveTags.append(TagIt)

            #Remove the tags we should remove by doing this
            for PrereqIt in self.Prereqs:
                for ActiveIt in Performer._ActiveTags:
                    if PrereqIt.TagName == ActiveIt.TagName:
                        Performer._ActiveTags.remove(ActiveIt)

        #If we are infinite, we still want to remove any additionally specified remove tags
        #(Just not our prerequisites as this would prevent us from doing it again)
        for RemoveIt in self._RemovesAdditionalTags:
            for ActiveIt in Performer._ActiveTags:
                if RemoveIt.TagName == ActiveIt.TagName:
                    Performer._ActiveTags.remove(ActiveIt)
        
            
#Get actions will "get" an amount of a resource...
class Get(Action):
    
    def __init__(self, GivenEffectTags, Interruptable, Given__ResourceName, Given__Amount, GivenGoalName = "", GivenWeight = 1, GivenPrerequisiteTags = []):
        super().__init__(GivenEffectTags, Interruptable, GivenGoalName, GivenWeight, GivenPrerequisiteTags)

        #The name in resource dictionaries of the resource we are getting
        self.__ResourceName = Given__ResourceName
        self.__Amount = Given__Amount

    def PerformAction(self, Performer):
        super().PerformAction(Performer)
        Performer.CarryingResource[self.__ResourceName] += self.__Amount
        self.ActionComplete(Performer)
    


#Go To actions, shockingly, involve going to a given coordinate
#They do not call action complete themselves for this is automatically called when the move queue generated by them is empty
class GoTo(Action):

     #[Parameters are as for the base action]
     def __init__(self, GivenEffectTags, Interruptable, GivenGoalName = "", GivenWeight = 1, GivenPrerequisiteTags = [], GivenRemovesTags = []):
        super().__init__(GivenEffectTags, Interruptable, GivenGoalName, GivenWeight, GivenPrerequisiteTags, GivenRemovesTags)

        #Where do we want to go?
        #Initilaised to 0,0 - it should always changed in child overloads
        self._GoTo = (0,0)
    
    #Go to that place!
     def PerformAction(self, Performer):
         super().PerformAction(Performer)

         #Get the performer to pathfind to this point
         Performer.SetGoalLocation(self._GoTo)  




#Child class for specifically returning to the centre of the siida as this requires updating incase it has moved since being set
class Return(GoTo):
    
    #Update to the current siida location...
    def UpdateGoTo(self, Performer):
        self._GoTo = Performer.Siida.CentreLocation

    def PerformAction(self, Performer):
        self.UpdateGoTo(Performer)
        super().PerformAction(Performer)

#Goes to a random point in the Siida bounds (used for random places for Lavvu)
class GoToInSiida(GoTo):

    def PerformAction(self, Performer):
        self._GoTo = Performer.Siida.GetLocationInSiida()
        super().PerformAction(Performer)
    
#go to a specific type of terrain (as defined in lists passed in)
class GoToType(GoTo):
    
    #Init overload allows us to also be passed a search list!
    #[Other parameters as with before]
    #Given search list <- the list of coordinates of typesz of cell we want to be able to pathfind to one of
    def __init__(self, GivenEffectTags, Interruptable, GivenSearchList, GivenGoalName = "", GivenWeight = 1, GivenPrerequisiteTags = []):
        super().__init__(GivenEffectTags, Interruptable, GivenGoalName, GivenWeight, GivenPrerequisiteTags)
        self.SearchList = GivenSearchList

    #Determine the closest in the given search list then go to it!
    def PerformAction(self, Performer):
        ClosestDistance = 9999       

        #Using our Manhattan distance, we can guess how far it may be...
        for i in self.SearchList:
            
            #We *could* factor the path to get there but in the interest of not spending years of processing time, we shall not
            Dist = Performer.ManhattanDistance(Performer.Location, i)       
            if Dist < ClosestDistance:
                self._GoTo = i
                ClosestDistance = Dist

        #Why call this here? so we set go to location only when we know where we want that!
        super().PerformAction(Performer)

        
#WANDER action - Go to a random place around a point - the Siida centre if this is a resident, or where they are now if not. [Our idle action]
class Wander(GoTo):

    def __init__(self, GivenEffectTags, Interruptable, GivenGoalName = "", GivenWeight = 1, GivenPrerequisiteTags = [], GivenRemovesTags = []):
        super().__init__(GivenEffectTags, Interruptable, GivenGoalName, GivenWeight, GivenPrerequisiteTags, GivenRemovesTags)
        self._bFinite = False


    def PerformAction(self, Performer):
        try:
            self._GoTo = Performer.Siida.GetLocationInSiida()
        except:
           
            #Go to a random land coordinate
            #Might have to fix...
            self._GoTo = random.choice(Performer._World.LandCoords)

        super().PerformAction(Performer)


#Track a found AI - assuming we will have set the performer's found here...
class Hunt(GoTo):

    def PerformAction(self, Performer):
       self._GoTo = Performer.Found.Location
       super().PerformAction(Performer)
       
       #Action complete handeled when our action queue is empty

    #Overload of action complete called whenever the AI reaches wherever it thinks the thing its tracking is (i.e.: when the move queue is empty) - if the reindeer is next to us, we will "kill" it and get the food. If not we will fail the action :(
    def ActionComplete(self, Performer):

        try:
            #When we have finished moving to where we thought the reindeer was - if we are close enough, we will "kill" it - if not we can consider that it has escaped us...
            if Performer.ManhattanDistance(Performer.Found.Location, Performer.Location) < 2:
         
                #Consider this us having caught and killed the thing we were hunting
                Performer.Found.Death()
                Performer.Found = None
                super().ActionComplete(Performer)

            else:
                self.ActionFailed(Performer, "they lost sight of the reindeer!")
        except:
            super().ActionComplete(Performer)


#FIND action - find something (Only used for rarer entities)
#Again utilising a search list rather than iterating through the world in an attempt to find stuff
class Find(Action):       
    
    def __init__(self, GivenEffectTags, Interruptable, GivenSearchList, GivenGoalName = "", GivenWeight = 1, GivenPrerequisiteTags = []):
        super().__init__(GivenEffectTags, Interruptable, GivenGoalName, GivenWeight, GivenPrerequisiteTags)
        self.SearchList  = GivenSearchList
        self._FailureWeightOffset = 500

    def PerformAction(self, Performer):
        super().PerformAction(Performer)
        #Determine if a thing in a given search list is in our "view" - if not go to somewhere with better visibility (Hill)
        #If found, coninue, else fail!


        #We also make sure that closest does not have a hunter so we dont end up going for the same thing and breaking stuff!
        Closest = None
        ClosestDist = 999
        for i in self.SearchList:
            D = Performer.ManhattanDistance(Performer.Location, i.Location)
            #If we can see a reindeer close enough..
            if   D < ClosestDist and i._Hunter == None:  
                try:
                    Closest._Hunter = None  
                except:
                    pass
                Closest = i
                Closest._Hunter = Performer                
                ClosestDist = D

        #If we have found something, we can consider this action complete and may move on with what we plan to do with this thing
        if Closest != None:
            Performer.Found = Closest   
            self.ActionComplete(Performer)
        else:
            self.ActionFailed(Performer, "They couldn't find anything!")
    
#Pack up a hut in preperation for migration. We choose a hut here too!
class PackLavvu(Hunt):

     #We should have a nearest hut we can GoTo already - we can call base functionality of hunt

    #Difference between this and stock is rather than kill it, we will put it in stock (and THEN kill it)
    def ActionComplete(self, Performer):
        Performer.Siida.Lavvu.remove(Performer.Found)
        Performer.Found.Death()
        Performer.Siida.LavvuStocked += 1
        super().ActionComplete(Performer)
        
#DEPOSIT action - all resources we are carrying will be put into the siida stockpile...
class Deposit(Action):

    def PerformAction(self, Performer):
        super().PerformAction(Performer) 
        
        for i in Performer.CarryingResource:   
            #We wont always have keys that exist in carrying resources in personal resources - e.g.: wood...
            try:     
                Performer.Siida.ResourcesInStock[i] += Performer.CarryingResource[i] - Performer.PersonalResource[i]
                Performer.CarryingResource[i] = 0
            except:
                pass

        self.ActionComplete(Performer)

#Build a lavvu where we are to keep us warm!
class BuildLavvu(Action):

    def PerformAction(self, Performer):
        super().PerformAction(Performer)

        #Plonk down a hut! [Assuming we are in the right location to do so!
        Performer.Siida.Lavvu.append(Hut.Lavvu(IMGS.LavvuIMG, Performer.Location, Performer._Batch))
    
        if Performer.Siida.LavvuStocked > 0:
            Performer.Siida.LavvuStocked -= 1
        else:
           Performer.Siida.ResourcesInStock["WoodSupply"] -= 10
        self.ActionComplete(Performer)

    

    