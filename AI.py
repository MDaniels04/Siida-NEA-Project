import Entity
import AStar
import IMGS
import Goal
import DesicionMaker as DM 
import Tag
import Action

#AI are entities with the ability to choose a sequence of actions to complete a goal...

class AI(Entity.Entity, AStar.AStar, DM.DesicionMaker):

 
    #Overload of entity aloows for option of sprite creation and spawning in the constructor - disabled by default so the
    def __init__(self, GivenRep, GivenWorld, SpawnLocation):

        #Really annoyingly, we need to explicitly call constructors here as super seems to only call the entity constructor

        AStar.AStar.__init__(self)
        #Really weirldy this constructor is called twice but if only called once we get issues referencing variables in it...
        DM.DesicionMaker.__init__(self)

        #A mini Finite State Machine so we can make sure the Ai reaches the location required
        # 0 = IDLE STATE - the AI will get a new goal
        # 1 = GO TO STATE - If the AI doesn't have anything in the move queue, it will pathfind towards its goal location, else it will continue on its way
        # 2 = PERFORM ACTION - The AI performs the next action in the queue. If it has no more afterwards, then it will set itself back to idle...
        self.CurrentState = 0

        #What actions are at this AIs disposal? iable to change over time....
        self.AvailableActions = [

            #IDLE ACTIONS
            #Wander about
            Action.Wander([Tag.Tag("Wander")], True, "wander about", 1)

        ]
       
        #The queue of actions that will be undertaken
        self.ActionQueue = []

        #The world we inhabit.... this is very useful for our actions and deciding where to go...
        self.World =  GivenWorld

        #What tags are currently active for this AI? used for
        self.ActiveTags = []

        #What goal are we currently working to achieve?
        self.ActiveGoal = Goal.Goal([], 0)

        #Are we in the process of "doing" an action? what?
        self.ActiveAction = None

        #What's the maximum MANHATTAN DISTANCE that we can spot things we are searching for away from?
        #TEMP HIGHER WE NEED TO SORT OUT ALL THESE VALUES...
        self.MaxSearchDistance = 10

        #What cells are we due to move to as per our needed actions?
        self.MoveQueue = []

        #Are any AI hunting us down? 
        self.Hunter = None

        #Are we hunting any AI down?
        self.Hunting = None

        #The location we are aiming to move to...
        self.GoalLocation = ()

        #What resouces does this AI grant? For example a reindeer has a personal food value of [ITS GONNA CHANGE IN BALANCE, IMAGINE THE CORRECT VALUE HERE - THX]
        self.PersonalResource = {

            "FoodSupply":0
        }

        #We will always want to auto spawn our AI
        super().__init__(GivenRep, SpawnLocation, GivenWorld.DrawBatch, IMGS.People, True)  

    #Called in our finite state machine when our state is 1 to dictate what the state should be next based on if we have any actions we want to do...
    def StateChangeAfterMovement(self):

        #The action we were doing will have been a movement actioin - so call its action complete here...
        self.ActiveAction.ActionComplete(self)             
        #The movement will have been considered one action.
        #If we got any more to do, go back to the action state
        if len(self.ActionQueue) > 0:
            self.CurrentState = 2
        #Else back to idle!
        else:
            self.CurrentState = 0

    #Our little FSM ran every day - based on our current state, it assigns our AI with something to do...
    def __FiniteStateMachine(self, NeededGoals = []):
       
        #First check is if a needed goal is higher priority than the one we are currently aiming to do, then we want to swap to this new goal 
        #(For example, if we were wandering around, and suddenly food supply was low, we would stop wandering and go get some food)
            
        #Are there any goals pending a task?
        bRequiredGoals = False
        
        #If we have some goals that need completing for the Siida
        if len(NeededGoals) > 0:
            bRequiredGoals = True
            if NeededGoals[0].Priority > self.ActiveGoal.Priority:
               try:                                                     #A 0 priority goal is essentially a time filler - wandering - or pausing - something not worth other AI picking up...                               
                    if self.ActiveAction.Interruptable == True and self.ActiveGoal.Priority > 0:
                        try:    
                            self.Siida.NeededGoals.append(self.ActiveGoal)

                        #In the exception case (reindeer) there isn't anything to give the needed goal back to - so just drop it
                        except:
                            pass
                    self.AssignNewGoal(NeededGoals[0])
                    self.Siida.TakeGoal()
            
               #If we don't have an active goal we will want to take the needed goal anyway....                                     
               except:
                    self.AssignNewGoal(NeededGoals[0])
                    self.Siida.TakeGoal()
      
        #Go through our states.

        #IDLE STATE - we go here when we don't have any goals and are looking for something to do...
        if self.CurrentState == 0:            
            if bRequiredGoals:    
               self.AssignNewGoal(NeededGoals[0])
            else:
                    pass
                    #Else idle around - have a wonder, have a chill...
                    self.AssignNewGoal(Goal.Goal([Tag.Tag("Wander")], " pass the time"))
        
        #MOVING STATE - We have been given a move queue and are ready to follow it...
        elif self.CurrentState == 1:
    
                    if len(self.MoveQueue) > 0:
                        self.SetSpriteLocation(self.MoveQueue[0])
                        self.MoveQueue.pop(0)
                    else: 
                        self.StateChangeAfterMovement()
                        #Call again - if we have nowhere to move we want to go do something else...
                        self.__FiniteStateMachine(NeededGoals)
 
        #Else we would be in the action stage...
        else:
            #If we are not currently performing an action towards this goal...
            if self.ActiveAction == None:
                if len(self.ActionQueue) > 0:
                    self.ActionQueue[0].PerformAction(self)
                    self.ActionQueue.pop(0)
                else:                 
                    self.CurrentState = 0
         
    #Update this entities statistics every day...
    def DailyFunction(self, NeededGoals = []):

        #STATISTICAL UPDATES - Our temperature, 
        #Finite state machine stuff (in this function)
        self.__FiniteStateMachine(NeededGoals)


        #If anyone is hunting us, and where we are now is "visible" to them, and we are not in the location we were, then we want to update their location they aim to reach...
        try:          
            if self.Location != self.Hunter.GoalLocation:
                print("Movement?")
                self.Hunter.SetGoalLocation(self.Location)
        except:
            pass

    #Set our goal location and change our state back to moving - its time to start hoofing it
    def SetGoalLocation(self, Given):
        self.GoalLocation = Given
        self.MoveQueue = []
        self.CurrentState = 1
        self.PathFindToLocation(Given)
        #We call our FSM again so we can get moving the same "day" we called whatever action telling us to hoof it...

    #Function allowing differing functionality between AI - what happens when we can't formulate a plan between goals...
    def UnableToAchieveGoal(self):
        
        #This is the reindeer functionality - overloaded over in resident
        #We just idle I suppose...
        print(self.Name, " didn't manage to ", self.ActiveGoal.GoalName)
        self.CurrentState = 0
        self.__FiniteStateMachine()

    #Functionality for killing the sprite, ensuring that our sprite is deleted as pyglet has documented cases of sprites not dissapearing when their container is deleted
    def Death(self):


        #ADD FUNCTIONALITY TO REAPPEND TO NEEDED GOALS SHOULD WE HAVE BEEN CARRYING SOMETHING OUT FOR THE SIIDA - LIKE IF WE WERE SENT TO GRAB FOOD AND DIED, THEN WE WANT TO READD THAT TO WHAT NEEDS TO BE DONE...
        

        #The resources we were carrying, and now our personal resources can be considered on this tile. ADD MARK FUNCTIONALITY FOR PERSONAL RESOURCE OF FELLOW HUMANS SO CANNABALISM IS A LAST RESORT...
        self.World.Grid[self.Location[1]][self.Location[0]].ResourcesInCell 

        #Ensure our sprite is gone - pyglet sometimes might leave the sprite if we just delete the object
        self.Sprite.delete()
        del self

    #We've been given a goal - all the priority stuff has already been dealt with. Simply make our adjacencies, then fin what's the closest
    def AssignNewGoal(self, GivenGoal):

        self.ActiveGoal = GivenGoal

        #We have a new goal, so are abandoning whatever we were doing...        
        self.ActiveAction = None
        #We are now in the execution stage!
        self.CurrentState = 2

        self.FormPlanningGraph(GivenGoal, self)
        #After we have iterated through our whole thing we want to add a final empty node we can class as our start node... 

        FinalEnds = []
        for EndIt in self.EndPoints:
                FinalEnds.append(EndIt[0])

        #Put a node on (0,0) - the closest to 0,0 will be the branch that has 
        #covered the least distance - and hence will be the shortest!
        self.AddNode(None, 0, [(0,0)])
        self.AddConnections(FinalEnds)

        #A* through it to find our best course of action!
        self.ActionQueue = self._AStar(True, list(self.Adjacencies)[-1], (1,0), self.Adjacencies)  
        
        #Reset desicion making variables... 
        self.EndPoints = []
        self.Adjacencies = {}
        self.RelativeCoords = (0,0)
        self.Count = 0

        if self.ActionQueue == False or len(self.ActionQueue) < 1:
            self.UnableToAchieveGoal()
        else:
            #Recursive call so we can begin the execution of our actions the same day we plan them (so there isn't years of standing around waiting for our AI to do something...)
            self.__FiniteStateMachine()


    #A utility function to fill this AI's move queue with the fastest path as got from the A* algorithm...
    def PathFindToLocation(self, GivenLocation):
    
        if GivenLocation != self.Location:
                                                                              
            self.MoveQueue = self._AStar(False, self.Location, GivenLocation, self.World)


        if self.MoveQueue == False:
            print("Unable to move there!")
            self.ActionFailed()

       
         
    #We did not have the required tags to perform an action, so this gets called....
    def ActionFailed(self):

        #Failing an action will make us less likely to do it in the future...
        self.AvailableActions[self.AvailableActions.index(self.ActiveAction)].Weight += 5

        #We now want to replan if we can
        self.AssignNewGoal(self.ActiveGoal)

        #Eventually maybe add functionality where fatigue influences being able to do it again?
       
            