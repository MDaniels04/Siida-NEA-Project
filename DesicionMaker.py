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
        self.Adjacencies = {}
        
        #Where was the "coordinates" of the last node we added?
        self.RelativeCoords = (0,0)

        #Item 0 = the coordinates we found this end point at
        #Item 1 = the number node this was (used for calcing when we should connect it)
        self.EndPoints = []

        #cOunting which number node this is - used for end point calculations...
        self.Count = 0

    #This function works regressively, so we only want these backwqards connections...
    
    #Utility function for adding a new node to our adjacency lists
    #Relative coordinates is the coordinates (based on weight NOT 
    #I represents the "branch" of this node
    def AddNode(self, GivenNode, I, PreviousCoordinates, Weight = 0):
        
        #We should never call this without previous coordinates - not even as a rule should be physically impossible
        #As such we dont need to error check for that eventuallity 

        if len(PreviousCoordinates) > 1:
            #Ensured we will always have an array of coords
            self.RelativeCoords = []

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
                self.RelativeCoords.append(AvgIt / len(PreviousCoordinates))       

            #Tags dont have weight - hence why we pass in weight as 0, so we can override if it isnt a tag

        #If we have one thing then just set to that!s
        else:
            self.RelativeCoords = PreviousCoordinates[0]

        #Add weight so long as it isnt 0

        #We need to turn this into a list as we cant assign with tuples :(
        New = list(self.RelativeCoords)
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
        self.RelativeCoords = tuple(New)
        self.Adjacencies[self.RelativeCoords] = [GivenNode]    
                                  
    #Utility function for adding connections to an existing node
    def AddConnections(self,  Connections):

        #As with before, we need to ensure thats an array
        
        #Remember we won't be able to modify the relative coord once its set so we need to use this minimally if possible!    
        for ConnectionsIt in Connections:
            self.Adjacencies[self.RelativeCoords].append(ConnectionsIt)
    

    #util function for taking the end points (tuples of coords and a number representing the count) and returning the usable coordinates
    def GetEndPointCoords(self, ClusterLowerBound = 0):
        LinkPoints = []
        for EndIt in self.EndPoints:
        #If we drew this 
            if ClusterLowerBound <= EndIt[1]:
                LinkPoints.append(EndIt[0])
            self.EndPoints.remove(EndIt)
    
        return LinkPoints
                
    #Function for taking our goal and available actions, and drawing a set of adjacency lists for pathfinding through to discern a plan of action for our AI
    def FormPlanningGraph(self, GivenGoal, Performer, GoalConnect = (1,0), Branch = 0):
        
        try:
            self.Name = self.Name
        except:
            pass
        Weight = 0
        
        #Our goal object doesn't have a weight attribute so this is an error catch
        if GoalConnect != (1,0):
            Weight = GivenGoal.Weight
           
        #Add the goal to our adjacencies...
        #GivenGoal is the goal itself that we need to do...
        #Branch is the given "branch of the graph we are on" - which will change which axis we move the relative coords on
        #Goal connect is the connections we want to make - in this case, just the node behind us
        
        self.AddNode(GivenGoal, Branch, [GoalConnect], Weight) 
        self.Count += 1
    
        #Cluster lower bound necessary for discerning between which end points a tag should connect to...
        ClusterLowerBound = self.Count

        self.AddConnections([GoalConnect])
        
        #/////
        #Get our unmet prerequisite tags for achieving this goal, or any blocked tags we cannot have...
        #////

        #What have we yet to meet?
        UnmetTags = []
        for GoalIt in GivenGoal.Prereqs:
            #Have we found this tag?
            bFoundTag = False
            for ActiveIt in Performer.ActiveTags:
                
                if ActiveIt.TagName == GoalIt.TagName:
                    bFoundTag = True

            if bFoundTag == False:
                #Bug with python - this is should be defined but isnt....
                UnmetTags.append(Tag.Tag(GoalIt.TagName))
       
        #If this action is not performable at this time
        if len(UnmetTags) > 0:
            for UnmetIt in UnmetTags:   
                LinkPoints = []
                for EndIt in self.EndPoints:
                    #If we drew this 
                    if ClusterLowerBound <= EndIt[1]:
                        LinkPoints.append(EndIt[0])
                    self.EndPoints.remove(EndIt)
                    
                #Ensure we link with the action calling this 
                LinkPoints.append(self.RelativeCoords)
                self.AddNode(UnmetIt, Branch, LinkPoints, 1)
                self.AddConnections(LinkPoints)

                #Add connections to the "end points" (performable action s that came before this)
    
                #Set our tag location so all our actions have a place to connect to...
                TagLocation = self.RelativeCoords
                #Coordinates not working ... :/

                Branch = 0

                for ActionIt in Performer.AvailableActions:
                    for EffectIt in ActionIt.EffectTags:
                        #If this is what we need to solve rn...
                        if EffectIt.TagName == UnmetIt.TagName:
                                        
                            #Recursion around!    
                            self.FormPlanningGraph(ActionIt, Performer, TagLocation, Branch)
                            Branch += 1      
                            
        else:
            #Add to end points - if it links directly in to a prerequisite it will be popped instantly....
            #Count tacked on the back here to be paired with curent count to ensure that we connect to the right Count
            self.EndPoints.append((self.RelativeCoords, self.Count)) 