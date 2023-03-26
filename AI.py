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
        self._CurrentState = 0

        #What actions are at this AIs disposal? iable to change over time....
        self._AvailableActions = [

            #IDLE ACTIONS
            #Wander about
            Action.Wander([Tag.Tag("Wander")], True, "wander about", 1, GivenRemovesTags = [Tag.Tag("PackingAbility")])
        ]
       
        #The queue of actions that will be undertaken
        self._ActionQueue = []

        #The world we inhabit.... this is very useful for our actions and deciding where to go...
        self._World =  GivenWorld

        #What tags are currently active for this AI? used for
        self._ActiveTags = []

        #What goal are we currently working to achieve?
        self._ActiveGoal = Goal.Goal([], 0)

        #Are we in the process of "doing" an action? what?
        self._ActiveAction = None

        #What cells are we due to move to as per our needed actions?
        self._MoveQueue = []

        #The location we are aiming to move to...
        self._GoalLocation = (0,0)

        #We will always want to auto spawn our AI
        super().__init__(GivenRep, SpawnLocation, GivenWorld.DrawBatch, IMGS.People, True)  

    #Called in our finite state machine when our state is 1 to dictate what the state should be next based on if we have any actions we want to do...
    def __StateChangeAfterMovement(self):

        #The action we were doing will have been a movement actioin - so call its action complete here...
        try:
            self._ActiveAction.ActionComplete(self)     
        except:
            #On exception we will have a none type for our active action (Because we failed the action earlier or for other reasons)
            #Hence we dont need to call action complete to set our active action to none...
            pass        
        #The movement will have been considered one action.
        #If we got any more to do, go back to the action state
        if len(self._ActionQueue) > 0:
            self._CurrentState = 2
        #Else back to idle!
        else:
            self._CurrentState = 0

    #Our little FSM ran every day - based on our current state, it assigns our AI with something to do...
    def __FiniteStateMachine(self, NeededGoals = []):
       
        #First check is if a needed goal is higher priority than the one we are currently aiming to do, then we want to swap to this new goal 
        #(For example, if we were wandering around, and suddenly food supply was low, we would stop wandering and go get some food)
            
        #Are there any goals pending a task?
        bRequiredGoals = False
        
        #If we have some goals that need completing for the Siida
        if len(NeededGoals) > 0:
            bRequiredGoals = True
            if NeededGoals[0]._Priority > self._ActiveGoal._Priority:

                #Try incase our active action is none (i.e.: we aren't doing anything)
                try:
                                                 #A 0 priority goal is essentially a time filler - wandering - or pausing - something not worth other AI picking up...                               
                    if self._ActiveAction._bInterruptable == True:
                        if self._ActiveGoal._Priority > 0: 
                            self.Siida.NeededGoals.append(self._ActiveGoal)
                        self.AssignNewGoal(NeededGoals[0])
                        self.Siida.TakeGoal()
                #so it will be interruptible
                except:
                        self.AssignNewGoal(NeededGoals[0])
                        self.Siida.TakeGoal()
    
                    
            
        #Go through our states.

        #IDLE STATE - we go here when we don't have any goals and are looking for something to do...
        if self._CurrentState == 0:            
            if bRequiredGoals:    
               self.AssignNewGoal(NeededGoals[0])
               self.Siida.TakeGoal()
            else:
                    #Else wander
                    self.AssignNewGoal(Goal.Goal([Tag.Tag("Wander")], " pass the time"))
        
        #MOVING STATE - We have been given a move queue and are ready to follow it...
        elif self._CurrentState == 1:
    
                    if len(self._MoveQueue) > 0:
                        self.SetSpriteLocation(self._MoveQueue[0])
                        self._MoveQueue.pop(0)
                    else: 
                        self.__StateChangeAfterMovement()
                        #Call again - if we have nowhere to move we want to go do something else...
                        self.__FiniteStateMachine(NeededGoals)
 
        #Else we would be in the action stage...
        else:
            #If we are not currently performing an action towards this goal...
            if self._ActiveAction == None:
                if len(self._ActionQueue) > 0:
                    Temp = self._ActionQueue[0]
                    self._ActionQueue[0].PerformAction(self)

                    #If an action fails, we may retry it then call this function again and perform it - then when we come back from that recursive call, we will have an empty action queue
                    #So this would give an error - hence the try except!
                    try:
                        self._ActionQueue.pop(0)
                    except:
                        pass
                else:                 
                    self._CurrentState = 0
         
    #Update this entities statistics every day...
    def DailyFunction(self, NeededGoals = []):

        #Call our FSm
        self.__FiniteStateMachine(NeededGoals)

        #If anyone is hunting us, and we move, we need to update where the hunter is going to
        #Try incase this is a none type
        if self._Hunter != None:
            if self.Location != self._Hunter._GoalLocation:
                self._Hunter.SetGoalLocation(self.Location)

    #Set our goal location and change our state back to moving - its time to start hoofing it
    def SetGoalLocation(self, Given):
        self._GoalLocation = Given
        self._MoveQueue = []
        self._CurrentState = 1
        self._PathFindToLocation(Given)

    #Function allowing differing functionality between AI - what happens when we can't formulate a plan between goals...
    def UnableToAchieveGoal(self):
  
        try:
            print(self.Name, " didn't manage to ", self._ActiveGoal.GoalName)
        except:
            pass
        self._CurrentState = 0
        self.__FiniteStateMachine()

    #We've been given a goal - all the priority stuff has already been dealt with. Simply make our adjacencies, then fin what's the closest
    def AssignNewGoal(self, GivenGoal):

        self._ActiveGoal = GivenGoal

        #We have a new goal, so are abandoning whatever we were doing...        
        self._ActiveAction = None
        #We are now in the execution stage!
        self._CurrentState = 2

        self._FormPlanningGraph(GivenGoal, self)
        #After we have iterated through our whole thing we want to add a final empty node we can class as our start node... 
        FinalEnds = []
        for EndIt in self._EndPoints:
                FinalEnds.append(EndIt[0])

        #Put a node on (0,0) - the closest to 0,0 will be the branch that has 
        #covered the least distance - and hence will be the shortest!
        self._AddNode(None, 0, [(0,0)])
        self._AddConnections(FinalEnds)

        #A* through it to find our best course of action!
        self._ActionQueue = self._AStar(True, list(self._Adjacencies)[-1], (1,0), self._Adjacencies)  
        
        #Reset desicion making variables... 
        self._EndPoints = []
        self._Adjacencies = {}
        self._RelativeCoords = (0,0)
        self._Count = 0

        if self._ActionQueue == False or len(self._ActionQueue) < 1:
            self.UnableToAchieveGoal()
        else:
            #Recursive call so we can begin the execution of our actions the same day we plan them (so there isn't years of standing around waiting for our AI to do something...)
            self.__FiniteStateMachine()


    #A utility function to fill this AI's move queue with the fastest path as got from the A* algorithm...
    def _PathFindToLocation(self, GivenLocation):
        if GivenLocation != self.Location:
                                                                              
            self._MoveQueue = self._AStar(False, self.Location, GivenLocation, self._World)
   
            #Back to our FSM again to minimise the time our AI are standing around doing nothing
            #we do not know needed goals - but that should not be important as we should just be moving this recursion...
            self.__FiniteStateMachine([])

        if self._MoveQueue == False:
            print("Unable to move there!")
            self._ActionFailed()

       
         
    #We did not have the required tags to perform an action, so this gets called....
    def _ActionFailed(self):
    
        #If we were moving we 

        #Failing an action will make us less likely to do it in the future...
        self._AvailableActions[self._AvailableActions.index(self._ActiveAction)]._Weight += self._ActiveAction._FailureWeightOffset

        #We now want to replan if we can
        self.AssignNewGoal(self._ActiveGoal)

        #Eventually maybe add functionality where fatigue influences being able to do it again?
       
            