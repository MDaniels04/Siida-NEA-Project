#An action is  a goal that also has effects upon its completion, and a function called whenever it is completed

import Goal
import Tag
import math
import random
import Hut
import IMGS

#As actions will all be unique children due to their new functionality, we can define stuff they need in their own constructors,
class Action(Goal.Goal):
   
    #Construct us - we are an action with effects!
    def __init__(self, GivenEffectTags, Interruptable, GivenGoalName, GivenWeight = 1,  GivenPrerequisiteTags = [], GivenRemovesTags = []):
        super().__init__(GivenPrerequisiteTags, GivenGoalName)

        #Can we stop this action part way through?
        self.bInterruptable = Interruptable    

        #Tags that will be granted upon completing this action
        self.EffectTags = GivenEffectTags

        #We will awlays remove the prerequisites to this action to prevent us from being able to skip steps if we come to do an action sequence again...
        self.RemovesTags = GivenRemovesTags + self.Prereqs
         
        #Weight is a sort of representation of the cost to do an action - for example, going to cut down a tree would have higher weight than getting wood from the stockpile....
        self.Weight = GivenWeight

        #Some actions shouldn't append their effect tags as they don't technicall have an effect - this is simply so we can trace between the 2 
        self.bFinite = True

        #The action we were performing has failed - either due to a lack of the proper tags, or other bespoke reasons.
    #
    def ActionFailed(self, Performer, Reason = None):
        
        try:
            print(Performer.Name, " wasn't able to ", self.GoalName, Reason if Reason != None else " we aren't quite sure what happened, but something went ary...")   
        #If they don't have a name (i.e.: aren't a resident) this will throw an except - in which case we dont want any flavour text  
        except:
            pass   

        #Allow for custom functionality - like dying cos you screwed up hunting...
        Performer.ActionFailed()


    #Do the thing actually detailed in the action....
    #Base action functionality is simply ensuring we know
    def PerformAction(self, Performer):
        Performer.ActiveAction = self

        #Check we have the necessary tags to perform this action. If we do not we need to plan for this goal again, as something has gone wrong :(
        for PrereqIt in self.Prereqs:
            bFound = False

            for ActiveIt in Performer.ActiveTags:
                if ActiveIt.TagName == PrereqIt.TagName:
                    bFound = True

            if bFound == False:
               try:
                    self.ActionFailed(Performer, "they didn't have the right tags!")
               except:
                    #We don't want to announce what an unnamed AI is doing...
                    self.ActionFailed(Performer)
               #This action has failed - now we call the performer's fail state...
               

                #Can't keep on down this rabbit warren...
               return
        try:
            print(Performer.Name, " is going to ", self.GoalName, "!")
        except:
            pass


    #A function we keep seperate from the main perform action function as some actions will not end within the same call that they begin (& actions may not be succesful so we don't always want this)
    def ActionComplete(self, Performer):
       
        Performer.ActiveAction = None
        if self.bFinite:
            #Update the tags of our performer
            for TagIt in self.EffectTags:
                if TagIt not in Performer.ActiveTags:
                    Performer.ActiveTags.append(TagIt)

            for RemoveIt in self.RemovesTags:
                if RemoveIt in Performer.ActiveTags:
                    Performer.ActiveTags.remove(RemoveIt)



#"Get" something from where we are - for example, if we were at the coast, we could get fish....
#No need for try / except as strictly residents will be performing this....
class Get(Action):
    
    def __init__(self, GivenEffectTags, Interruptable, GivenResourceName, GivenAmount, GivenGoalName = "", GivenWeight = 1, GivenPrerequisiteTags = []):
        super().__init__(GivenEffectTags, Interruptable, GivenGoalName, GivenWeight, GivenPrerequisiteTags)
        self.ResourceName = GivenResourceName
        self.Amount = GivenAmount

    def PerformAction(self, Performer):
        super().PerformAction(Performer)
        Performer.CarryingResource[self.ResourceName] += self.Amount
        print("We just got", self.Amount, " ", self.ResourceName)
        self.ActionComplete(Performer)
    

#//////////////////////////////////////////////////
#GO TO ACTIONS - ACTIONS THAT INVLOVE GOING TO A PLACE DETERMINED BY THE ACTION (E.G.: THE CLOSEST COAST)
#//////////////////////////////////////////////////


#Go to either a given coordinate or a coordinate got from functionality w/ in the action...
class GoTo(Action):

     def __init__(self, GivenEffectTags, Interruptable, GivenGoalName = "", GivenGoTo = (), GivenWeight = 1, GivenPrerequisiteTags = []):
        super().__init__(GivenEffectTags, Interruptable, GivenGoalName, GivenWeight, GivenPrerequisiteTags)
        #Where do we want to go?
        self.GoTo = GivenGoTo
    
     def PerformAction(self, Performer):
         super().PerformAction(Performer)
         Performer.SetGoalLocation(self.GoTo)  

        #We don't call action complete after a go to action - that is done once we have emptied the move queue...

#Different function so we can call the get coord in siida at action performance and get a unique location each time
class GoToInSiida(Action):

    def PerformAction(self, Performer):
        self.GoTo = Performer.Siida.GetLocationInSiida()
        print(self.GoTo)
        super().PerformAction(Performer)
    
#GOTO actions are actions that involve going to a cell of a certain type for a specific resource - so for example, coast for fish....
class GoToType(GoTo):
    
    #Init overload allows us to also be passed a search list!#
    def __init__(self, GivenEffectTags, Interruptable, GivenSearchList, GivenGoalName = "", GivenWeight = 1, GivenPrerequisiteTags = []):
        super().__init__(GivenEffectTags, Interruptable, GivenGoalName, (), GivenWeight, GivenPrerequisiteTags)
        self.SearchList = GivenSearchList

    def PerformAction(self, Performer):
        ClosestDistance = 999       

        #Using our Manhattan distance, we can guess how far it may be...
        for i in self.SearchList:
            
            #We *could* factor the path to get there but in the interest of not spending years, we shall not...
            Dist = Performer.ManhattanDistance(Performer.Location, i)       
            if Dist < ClosestDistance:
                self.GoTo = i
                ClosestDistance = Dist

        #Why call this here? so we set go to location only when we know where we want that!
        super().PerformAction(Performer)

        
#WANDER action - Go to a random place around a point - the Siida centre if this is a resident, or where they are now if not.
class Wander(GoTo):

    def __init__(self, GivenEffectTags, Interruptable, GivenGoalName = "", GivenWeight = 1, GivenPrerequisiteTags = []):
        super().__init__(GivenEffectTags, Interruptable, GivenGoalName, (), GivenWeight, GivenPrerequisiteTags)
        self.bFinite = False

    def PerformAction(self, Performer):
       
        try:
            self.GoTo = Performer.Siida.GetLocationInSiida()
        except:
           
            #Go to a random land coordinate
            #Might have to fix...
            self.GoTo = random.choice(Performer.World.LandCoords)

        super().PerformAction(Performer)


#//////////////////////////////////////////////////
#MISC ACTIONS THAT DONT FIT INTO ANYTHING ELSE
#//////////////////////////////////////////////////



#FIND action - find something (We only use this for rarer stuff like AI - for more common stuff like the coast we just assume they have enough situational awareness to know where that is)
#Again utilising a search list rather than iterating through the world in an attempt to find stuff
class Find(Action):       
    
    def __init__(self, GivenEffectTags, Interruptable, GivenSearchList, GivenGoalName = "", GivenWeight = 1, GivenPrerequisiteTags = []):
        super().__init__(GivenEffectTags, Interruptable, GivenGoalName, GivenWeight, GivenPrerequisiteTags)
        self.SearchList  = GivenSearchList

    #Overload of action complete called whenever the AI reaches wherever it thinks the thing its tracking is (i.e.: when the move queue is empty) - if the reindeer is next to us, we will "kill" it and get the food. If not we will fail the action :(
    def ActionComplete(self, Performer):

        try:
            #When we have finished moving to where we thought the reindeer was - if we are close enough, we will "kill" it - if not we can consider that it has escaped us...
            if Performer.ManhattanDistance(Performer.Hunting.Location, Performer.Location) < 1:
                super().ActionComplete(Performer)
                #We will also stop the AI here from moving so we can do whatever we wanted to do...
                #Attempt 1 at this - clear the move queue
                Performer.Hunting.MoveQueue.clear()   
            else:
                self.ActionFailed(Performer, "they lost sight of the reindeer!")
        except:
            super().ActionComplete(Performer)

    def PerformAction(self, Performer):
        super().PerformAction(Performer)
        #Determine if a thing in a given search list is in our "view" - if not go to somewhere with better visibility (Hill)
        #If found, coninue, else fail!

        Closest = None
        ClosestDist = 999
        for i in Performer.World.Reindeer:
            D = Performer.ManhattanDistance(Performer.Location, i.Location)
            #If we can see a reindeer close enough..
            if  D <= Performer.MaxSearchDistance and D < ClosestDist:                
                Closest = i
                ClosestDist = D

        #If we have found something, we can consider this action complete and may move on with tracking of this...thing...
        if Closest != None:
            Performer.Hunting = Closest
            Closest.Hunter = Performer
            Performer.SetGoalLocation(Closest.Location)
    
        else:
            #If we are already on a hill, then we can consider there to be no reindeer close enough for us to find - and as such this action will fail, and we will increase the weight of this action...            
            if Performer.Location in Performer.World.HillCoords:
                self.ActionFailed(Performer)

            #else our action queue will expand a little - we will add a go to hill action to the front of the queue, followed by this...
            else:
                                                #We dont need effect tags - we already done all our planning...
                Performer.ActionQueue.insert(0, GoToType([], True, Performer.World.HillCoords))
                Performer.CurrentState = 2
                #Note how this action wont be done

                #Dont need to call action complete here, we will move off to the hills by ourselves...


#Build something, spending the correct resources
class Build(Action):


    def PerformAction(Performer):
        super().PerformAction(Performer)




#Kill what we were hunting. Remember death will place any resources we considered that AI carrying on the ground.
class Kill(Action):

    def PerformAction(self, Performer):
        super().PerformAction(Performer)
        #At some point would be very cool to make it so that if the AI were fatigued they could fail this...
        Performer.Hunting.Death()
        Performer.Hunting = None
        self.ActionComplete(Performer)

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
        Performer.Siida.Lavvu.append(Hut.Lavvu(IMGS.LavvuIMG, Performer.Location, Performer.Batch))

        self.ActionComplete(Performer)

    