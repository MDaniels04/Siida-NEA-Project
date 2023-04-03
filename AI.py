import Entity
import AStar
import IMGS
import Goal
import DesicionMaker as DM 
import Tag
import Action

#AI are entities with desicion making and pathfinding capabilities
class AI(Entity.Entity, AStar.AStar, DM.DesicionMaker):

    #Our parameters are as with entity
    def __init__(self, GivenRep, GivenWorld, SpawnLocation):

        #We are required to explicitly call both constructors as super will only call the first inherited class' functionality (entity)
        AStar.AStar.__init__(self)
        DM.DesicionMaker.__init__(self)

        #A mini Finite State Machine so we can make sure the Ai reaches the location required
        # 0 = IDLE STATE - the AI will get a new goal
        # 1 = GO TO STATE - If the AI doesn't have anything in the move queue, it will pathfind towards its goal location, else it will continue on its way
        # 2 = PERFORM ACTION - The AI performs the next action in the queue. If it has no more afterwards, then it will set itself back to idle...
        self.__CurrentState = 0

        #What actions are at this AIs disposal? iable to change over time....
        self.__AvailableActions = [

            #IDLE ACTIONS
            #Wander about
            Action.Wander([Tag.Tag("Wander")], True, "wander about", 1, GivenRemovesTags = [Tag.Tag("PackingAbility")])
        ]
       
        #The queue of actions that will be undertaken
        self.__ActionQueue = []

        #The world we inhabit.... this is very useful for our actions and deciding where to go...
        self.__World =  GivenWorld

        #What tags are currently active for this AI? used for
        self.__ActiveTags = []

        #What goal are we currently working to achieve?
        self.__ActiveGoal = Goal.Goal([], 0)

        #Are we in the process of "doing" an action? what?
        self.__ActiveAction = None

        #What cells are we due to move to as per our needed actions?
        self.__MoveQueue = []

        #The location we are aiming to move to...
        self.__GoalLocation = (0,0)

        #We will always want to auto spawn our AI
        super().__init__(GivenRep, SpawnLocation, GivenWorld._GetDrawBatch(), IMGS.People, True)  

    #Called in our finite state machine when our state is 1 to dictate what the state should be next based on if we have any actions we want to do...
    def __StateChangeAfterMovement(self):

        #The action we were doing will have been a movement actioin - so call its action complete here...
        try:
            self.__ActiveAction._ActionComplete(self)     
        except:
            #On exception we will have a none type for our active action (Because we failed the action earlier or for other reasons)
            #Hence we dont need to call action complete to set our active action to none...
            pass        
        #The movement will have been considered one action.
        #If we got any more to do, go back to the action state
        if len(self.__ActionQueue) > 0:
            self.__CurrentState = 2
        #Else back to idle!
        else:
            self.__CurrentState = 0

    #Our little FSM ran every day - based on our current state, it assigns our AI with something to do...
    def __FiniteStateMachine(self, NeededGoals = []):
       
        #First check is if a needed goal is higher priority than the one we are currently aiming to do, then we want to swap to this new goal 
        #(For example, if we were wandering around, and suddenly food supply was low, we would stop wandering and go get some food)
            
        #Are there any goals pending a task?
        bRequiredGoals = False
        
        #If we have some goals that need completing for the Siida

        #Should only be calling this block of code if we are residents, so we do not need to worry bout error checking vars for both AI
        if len(NeededGoals) > 0:
            bRequiredGoals = True
            if NeededGoals[0]._GetPriority() > self.__ActiveGoal._GetPriority():

                #Try incase our active action is none (i.e.: we aren't doing anything)
                try:
                                                 #A 0 priority goal is essentially a time filler - wandering - or pausing - something not worth other AI picking up...                               
                    if self.__ActiveAction._GetInterruptable() == True:
                        if self.__ActiveGoal._GetPriority() > 0: 
                            self._GetSiida().NeededGoals.append(self.__ActiveGoal)
                        self.__AssignNewGoal(NeededGoals[0])
                        self._GetSiida().TakeGoal()
                #so it will be interruptible
                except:
                        self.__AssignNewGoal(NeededGoals[0])
                        self._GetSiida().TakeGoal()
    
                    
            
        #Go through our states.

        #IDLE STATE - we go here when we don't have any goals and are looking for something to do...
        if self.__CurrentState == 0:            
            if bRequiredGoals:    
               self.__AssignNewGoal(NeededGoals[0])
               self._GetSiida().TakeGoal()
            else:
                    #Else wander
                    self.__AssignNewGoal(Goal.Goal([Tag.Tag("Wander")], " pass the time"))
        
        #MOVING STATE - We have been given a move queue and are ready to follow it...
        elif self.__CurrentState == 1:
    
                    if len(self.__MoveQueue) > 0:
                        self._SetSpriteLocation(self.__MoveQueue[0])
                        self.__MoveQueue.pop(0)
                    else: 
                        self.__StateChangeAfterMovement()
                        #Call again - if we have nowhere to move we want to go do something else...
                        self.__FiniteStateMachine(NeededGoals)
 
        #Else we would be in the action stage...
        else:
            #If we are not currently performing an action towards this goal...
            if self.__ActiveAction == None:
                if len(self.__ActionQueue) > 0:
                    self.__ActionQueue[0]._PerformAction(self)

                    #If an action fails, we may retry it then call this function again and perform it - then when we come back from that recursive call, we will have an empty action queue
                    #So this would give an error - hence the try except!
                    try:
                        self.__ActionQueue.pop(0)
                    except:
                        pass
                else:                 

                    #Remove the active tags we got from the final actions in our action queue so we can do that action tree again...
                    self.__ActiveTags = []
                    self.__CurrentState = 0
         
    #Update this entities statistics every day...
    def _DailyFunction(self, NeededGoals = []):

        #Call our FSm
        self.__FiniteStateMachine(NeededGoals)

        #If anyone is hunting us, and we move, we need to update where the hunter is going to
        #Try incase this is a none type
        if self._Hunter != None:
            if self._GetLocation() != self._Hunter.__GoalLocation:
                self._Hunter._SetGoalLocationToPathfind(self._GetLocation())

    #Set our goal location and change our state back to moving - its time to start hoofing it
    def _SetGoalLocationToPathfind(self, Given):
        self.__GoalLocation = Given
        self.__MoveQueue = []
        self.__CurrentState = 1
        self.__PathFindToLocation(Given)


    def __UnableToAchieveGoal(self):
 
        try:
            print(self._GetName(), " didn't manage to ", self.__ActiveGoal._GetGoalName())
        except:
            pass

        self.__CurrentState = 0
        self.__FiniteStateMachine()

    #We've been given a goal - all the priority stuff has already been dealt with. Simply make our adjacencies, then fin what's the closest
    def __AssignNewGoal(self, GivenGoal):

        self.__ActiveGoal = GivenGoal

        #We have a new goal, so are abandoning whatever we were doing...        
        self.__ActiveAction = None
        #We are now in the execution stage!
        self.__CurrentState = 2

        self._FormPlanningGraph(GivenGoal, self)
        #After we have iterated through our whole thing we want to add a final empty node we can class as our start node... 
        FinalEnds = []
        for EndIt in self._GetEndPoints():
                FinalEnds.append(EndIt[0])

        #Put a node on (0,0) - the closest to 0,0 will be the branch that has 
        #covered the least distance - and hence will be the shortest!
        self._AddNode(None, 0, [(0,0)])
        self._AddConnections(FinalEnds)

        #A* through it to find our best course of action!
        self.__ActionQueue = self._AStar(True, list(self._GetAdjacencies())[-1], (1,0), self._GetAdjacencies())  
        
        #Reset desicion making variables... 
        self._SetEndPoints([])
        self._SetAdjacencies({})
        self._SetRelativeCoords((0,0))
        self._Count = 0

        if self.__ActionQueue == False or len(self.__ActionQueue) < 1:
            self.__UnableToAchieveGoal()
        else:
            #Recursive call so we can begin the execution of our actions the same day we plan them (so there isn't years of standing around waiting for our AI to do something...)
            self.__FiniteStateMachine()


    #A utility function to fill this AI's move queue with the fastest path as got from the A* algorithm...
    def __PathFindToLocation(self, GivenLocation):
        if GivenLocation != self._GetLocation():
                                                                              
            self.__MoveQueue = self._AStar(False, self._GetLocation(), GivenLocation, self.__World)
   
            #Back to our FSM again to minimise the time our AI are standing around doing nothing
            #we do not know needed goals - but that should not be important as we should just be moving this recursion...
            self.__FiniteStateMachine([])

        if self.__MoveQueue == False:
            print("Unable to move there!")
            self._ActionFailed()

       
         
    #We did not have the required tags to perform an action, so this gets called....
    def _ActionFailed(self):
    
        #If we were moving we 

        #Failing an action will make us less likely to do it in the future...
        self.__AvailableActions[self.__AvailableActions.index(self.__ActiveAction)]._SetWeight(self.__ActiveAction._GetWeight() + self.__ActiveAction._FailureWeightOffset)

        #We now want to replan if we can
        self.__AssignNewGoal(self.__ActiveGoal)

        #Eventually maybe add functionality where fatigue influences being able to do it again?
       
            

    ######
    #GETTERS AND SETTERS
    ######

    def _GetCurrentState(self):
        return self.__CurrentState

    def _SetCurrentState(self, Given):
        self.__CurrentState = Given

    def _GetGoalLocation(self):
        return self.__GoalLocation

    #Specified to avoid confusion with _SetGoalLocationToPathfind
    def _SetGoalLocationSetter(self, Given):
        self.__GoalLocation = Given    

    def _GetActionQueue(self):
        return self.__ActionQueue

    def _SetActionQueue(self, Given):
        self.__ActionQueue = Given

    def _GetWorld(self):
        return self.__World

    def _GetAvailableActions(self):
        return self.__AvailableActions

    def _SetAvailableActions(self, Given):
        self.__AvailableActions = Given
    
    def _GetActiveTags(self):
        return self.__ActiveTags

    def _SetActiveTags(self, Given):
        self.__ActiveTags = Given

    def _GetActiveGoal(self):
        return self.__ActiveGoal

    def _SetActiveGoal(self, Given):
        self.__ActiveGoal = Given
   
    def _GetActiveAction(self):
        return self.__ActiveAction

    def _SetActiveAction(self, Given):
        self.__ActiveAction = Given

    def _GetMoveQueue(self):
        return self.__MoveQueue

    def _SetMoveQueue(self, Given):
        self.__MoveQueue = Given