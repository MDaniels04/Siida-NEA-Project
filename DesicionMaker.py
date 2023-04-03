#A desicion maker utilises tags and actions in order to achieve a goal - using GOAP...

import Action
import Tag

#A class used as a component responsible for the formation and execution of plans for AI
class DesicionMaker():

    def __init__(self):

        #Collection of the adjacency lists representing the possible paths we could take towards solving an action
        #Dictionary representation of such as this makes accessing it again trhough A* much easier...
        # Adjacency is a list
        # Item 0 = action itself (i.e.: what we want to do)
        # Item 1+ = coords we link to 
        # Key = "coord" of node...
        self.__Adjacencies = {}
        
        #Where was the "coordinates" of the last node we added?
        self.__RelativeCoords = (0,0)

        #Item 0 = the coordinates we found this end point at
        #Item 1 = the number node this was (used for calcing when we should connect it)
        self.__EndPoints = []

        #cOunting which number node this is - used for end point calculations...
        self._Count = 0

    #This function works regressively, so we only want these backwqards connections...
    
    #Utility function for adding a new node to our adjacency lists
    #Relative coordinates is the coordinates (based on weight NOT 
    #I represents the "branch" of this node
    def _AddNode(self, GivenNode, I, PreviousCoordinates, Weight = 0):
        
        #We should never call this without previous coordinates - not even as a rule should be physically impossible
        #As such we dont need to error check for that eventuallity 

        if len(PreviousCoordinates) > 1:
            #Ensured we will always have an array of coords
            self.__RelativeCoords = []

            #Because tuples dont suppourt item assignment (REALLY irritating), we are instead going to create avg as a list...
            avg = []

            #Keep in mind previous coordinates is an array of tuples....
            for PrevIt in PreviousCoordinates:

                #so iterating through each tuple....
                #
                #Should iterate through each value of the tuple            

                #We don't know what the size of our tuples may be....
                for CoordC, CoordV in enumerate(PrevIt):
                    if len(avg) -1 < CoordC:
                        avg.append(CoordV)
                    else:                     
                        avg[CoordC] += CoordV
                     
            #We take the average of the incoming previous coordinates and make our relative coord that, 
            #+ add connections to the given coordinates 
            
            for AvgIt in avg:
                self.__RelativeCoords.append(AvgIt / len(PreviousCoordinates))       

            #Tags dont have weight - hence why we pass in weight as 0, so we can override if it isnt a tag

        #If we have one thing then just set to that!s
        else:
            self.__RelativeCoords = PreviousCoordinates[0]

        #Add weight so long as it isnt 0

        #We need to turn this into a list as we cant assign with tuples :(
        New = list(self.__RelativeCoords)
        if Weight > 0:
            if len(New) - 1 < I:
                #For the difference we want to append  0 till we get the branch we want
                #This is necessary for the pretend distance between nodes being correct still...
                while len(New) - 1 < I:
                    New.append(0)
                    New.append(Weight)

            else:
               New[I] += Weight

        #Tuples are unhashable in our dictionary - so we convert you back into a a tuple..
        self.__RelativeCoords = tuple(New)
        self.__Adjacencies[self.__RelativeCoords] = [GivenNode]    
                                  
    #Utility function for adding connections to an existing node
    def _AddConnections(self,  Connections):

        #As with before, we need to ensure thats an array
        
        #Remember we won't be able to modify the relative coord once its set so we need to use this minimally if possible!    
        for ConnectionsIt in Connections:
            self.__Adjacencies[self.__RelativeCoords].append(ConnectionsIt)
                
    #Function for taking our goal and available actions, and drawing a set of adjacency lists for pathfinding through to discern a plan of action for our AI
    def _FormPlanningGraph(self, GivenGoal, Performer, GoalConnect = (1,0), GivenBranch = 0):
        
        Weight = 0
        
        #Our goal object doesn't have a weight attribute so this is an error catch
        if GoalConnect != (1,0):
            Weight = GivenGoal._GetWeight()

        #DEBUG CHANGE
        else:
            pass
           
        #Add the goal to our adjacencies...
        #GivenGoal is the goal itself that we need to do...
        #Branch is the given "branch of the graph we are on" - which will change which axis we move the relative coords on
        #Goal connect is the connections we want to make - in this case, just the node behind us
        
        self._AddNode(GivenGoal, GivenBranch, [GoalConnect], Weight) 
        self._Count += 1
    
        #Cluster lower bound necessary for discerning between which end points a tag should connect to...
        ClusterLowerBound = self._Count

        self._AddConnections([GoalConnect])

        #Get our unmet prerequisite tags for achieving this goal, or any blocked tags we cannot have...

        #What have we yet to meet?
        UnmetTags = []
        for GoalIt in GivenGoal._GetPrereqs():
            #Have we found this tag?
            bFoundTag = False
            for ActiveIt in Performer._GetActiveTags():
                
                if ActiveIt._GetTagName() == GoalIt._GetTagName():
                    bFoundTag = True

            if bFoundTag == False:
                #Bug with python - this is should be defined but isnt....
                UnmetTags.append(Tag.Tag(GoalIt._GetTagName()))
       
        #If this action is not performable at this time
        if len(UnmetTags) > 0:
            for UnmetIt in UnmetTags:   
                Branch = GivenBranch
                LinkPoints = []
                for EndIt in self.__EndPoints:
                    #If we drew this 
                    if ClusterLowerBound <= EndIt[1]:
                        LinkPoints.append(EndIt[0])
                        self.__EndPoints.remove(EndIt)
                    
                #Ensure we link with the action calling this if we aren't already doing so
                if self.__RelativeCoords not in LinkPoints:
                    LinkPoints.append(self.__RelativeCoords)
                self._AddNode(UnmetIt, Branch, LinkPoints, 1)
                self._AddConnections(LinkPoints)

                #Add connections to the "end points" (performable action s that came before this)
    
                #Set our tag location so all our actions have a place to connect to...
                TagLocation = self.__RelativeCoords

                for ActionIt in Performer._GetAvailableActions():
                    for EffectIt in ActionIt._GetEffectTags():
                        #If this is what we need to solve rn...
                        if EffectIt._GetTagName() == UnmetIt._GetTagName():
                                        
                            #Recursion!
                            self._FormPlanningGraph(ActionIt, Performer, TagLocation, Branch)
                            Branch += 1      
                            
        else:
            #Add to end points - if it links directly in to a prerequisite it will be popped instantly....
            #_Count tacked on the back here to be paired with curent count to ensure that we connect to the right _Count
            self.__EndPoints.append((self.__RelativeCoords, self._Count)) 



###
#GETTERS AND SETTERS
###

    def _GetAdjacencies(self):
        return self.__Adjacencies
    
    def _SetAdjacencies(self, Given):
        self.__Adjacencies = Given

    def _SetRelativeCoords(self, Given):
        self.__RelativeCoords = Given

    def _GetEndPoints(self):
        return self.__EndPoints

    def _SetEndPoints(self, Given):
        self.__EndPoints = Given