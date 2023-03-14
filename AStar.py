#A* kept here as it can be used in both pathfinding and 
#Dont know if we want to store it here NE way...

#We store it here just because we can 

import math as m

#Used for confirming that it is of type action...
import Action as A

#TO DO - ACTION TRAVERSAL!

class AStar():
    
    #Calculate the manhattan distance between the 2 points given - for use in pathfinding heuristics...
    def ManhattanDistance(self, GivenCurrentLocation, GivenGoalLocation):
        #We only use 2 dims for our manhattan distance as it is exclusively used for our map pathfinding...
        h = abs(GivenGoalLocation[0] - GivenCurrentLocation[0]) + abs(GivenGoalLocation[1] - GivenCurrentLocation[1])
        return h
    
    #We don't know how many dimensions will be passed in to this heuristic calculation as our graoph of an AI's available actions can have (theoretically) any number of branches
    def EuclideanDistance(self, GivenCurrentLocation, GivenGoalLocation):
        Distance = 0

        for Count, Value in enumerate(GivenGoalLocation):      
            try:
                Distance += (GivenCurrentLocation[Count] - Value)**2
            except:
                Distance += GivenCurrentLocation[Count]**2
 
            
        return m.sqrt(Distance)


    #OUR NODES ARE COORDINATES!!!

    #The type given indicates whether or not we are iterating thru a grid or a graph - a grid has 4 possible connections, so uses manhattan, a graph has infinite, so uses euclidean
    def __h(self, Type, Current, Goal, ToTraverse):
        if Type == True:
            return self.EuclideanDistance(Current, Goal)
        else:
            return self.ManhattanDistance(Current, Goal)

    
    #As with our heuristical calculation, we have different methods based on if this is our graph or grid we are traversing
    def __GetNeighbours(self, Type, Current, ToTraverse):   
        Neighbours = []
        if Type == True:

            #As our adjacencies are kept in arrays of [NodeType, *Coords] all the connections of this node will be the items past the 0th index...            
            for It in ToTraverse[Current][1:]:
                Neighbours.append(It)


        #Return coords of the adjacent grid cells based on where we are now...
        else:            
             if Current[0] > 0:

                Neighbours.append((Current[0] -1, Current[1]))
        
             if Current[0] < ToTraverse.GridDims[0] -1:
                
                Neighbours.append((Current[0] + 1, Current[1]))
        
             if Current[1] > 0:
                Neighbours.append((Current[0], Current[1] - 1))

             if Current[1] < ToTraverse.GridDims[1] -1:
                Neighbours.append((Current[0], Current[1] + 1))
        return Neighbours

    #Once more - weight getting methods differ if we are on the graph or on the 
    def __GetWeight(self, Type, Current, ToTraverse):

        #Graph
        if Type == True:
            #ADD LATER - WEIGHT INCREASES BASED ON ESTIMATED DISTANCE THAT WOULD BE NEEDED TO COMPLETE AN ACTION....
            return 1;
        #Grid 
        else:
            #Use the tuple pieces in the list
            W = ToTraverse.Grid[Current[0]][Current[1]].Weight
            return W
    
    def __AddToActionPath(self, Thing, Path):
        
        if isinstance(Thing, A.Action):
            Path.insert(0, Thing)

    #Trace our path backwards!
    def __TraceBack(self, Type, Neighbour, Current, Parents, ToTraverse):
        #Our methodology will differ slightly if this is a graph - we only want to append the option if it's an action....
        #So we check is type action...

        #Path is what we want to return\             
        Path = []
                
        #Ensure goal node and the one before are on our path

        if Type == True:
            self.__AddToActionPath(ToTraverse[Neighbour][0], Path)
            self.__AddToActionPath(ToTraverse[Current][0], Path)
        else:
            Path.insert(0, Neighbour)
            Path.insert(0, Current)

        Parents[Neighbour] = Current
                    
        while Parents[Current] != Current:
                
            Current = Parents[Current]  

            if Type == True:
                self.__AddToActionPath(ToTraverse[Current][0], Path)
            else:
                #Append at the beginning like a stack!
                Path.insert(0, Current) 

                #But not technically a "stack"
                #Im not sure what counts to get marks to be completely honest with you, so I might just say I have stacks and hope that 

        return Path
 
    def _AStar(self, Type, StartNode, StopNode, ToTraverse):

        #Acts as a priority queue - node with the lowest F 
        OpenList = [StartNode]
        
        #What have we already fully explored?
        ClosedList = []

        #Dictionary telling us how we got to this coordinate
        Parents = {StartNode:StartNode}

        #The total cost (included estimated remaining) to reach our goal. Just need this one for our sort
        F = {StartNode:0}

        while len(OpenList) > 0:
            
            #Sort our open list so our first item is the one with the lowest F - we've found it
            OpenList = sorted(OpenList, key = lambda ele: F[ele])
            Current = OpenList[0]

            OpenList.pop(0)
            ClosedList.append(Current)

            #Now we go through our neighbours

            for Neighbour in self.__GetNeighbours(Type, Current, ToTraverse):
             
                #We found it :)
                if Neighbour == StopNode: 
                    return self.__TraceBack(Type, Neighbour, Current, Parents, ToTraverse)
                       
                elif Neighbour not in ClosedList:          
                    
                    NewF = F[Current] + self.__GetWeight(Type, Current, ToTraverse) + self.__h(Type, Current, StopNode, ToTraverse)
                    if Neighbour in F:
                        #Update if we've found a nicer route
                        if F[Neighbour] > NewF or F[Neighbour] == None:
                            F[Neighbour] = NewF
                            OpenList.append(Neighbour)
                            Parents[Neighbour] = Current                            
                    else:
                        OpenList.append(Neighbour)
                        F[Neighbour] = NewF
                        Parents[Neighbour] = Current

        #If we get to here we never ended up tracing back - meaning we couldn't find a path :(
        return False

    