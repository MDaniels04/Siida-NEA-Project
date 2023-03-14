import random

#IMPORTANT NOTE - AS OUR MAP IS A LIST OF ROWS, Y IS TAKEN AS THE FIRST COORDINATE, AND X THE LATTER...

#Cellular automaton are objects with the ability to generate a map like shape on a given grid
class CellularAutomata():
           
    #Constructor
    #
    # GivenTargetDimensions[0] = grid Y height
    # GivenTargetDimensions[1] = grid X wifth
    #
    # DefaultGridFill = What to fill the grid with initially
    def __init__(self, GivenTargetDimensions, DefaultGridFill):
            
        #The grid in which we which to iterate over...
        self.Grid = []
            
        self.GridDims = GivenTargetDimensions
        self.GridDims = GivenTargetDimensions

        #Initialise our grid full of our desired initial fill
        for Y in range(GivenTargetDimensions[0]):
            NewRow = []
            for X in range(GivenTargetDimensions[1]):
                NewRow.append(DefaultGridFill)
            self.Grid.append(NewRow)

                
    #Assign points in the grid to be of correct type
    def AddNoiseToGrid(self, GivenNoise, GivenSurroundings, intSpawnChance):
        random.seed()

        for Y in range(self.GridDims[0]):
            for X in range(self.GridDims[1]):

                if self.Grid[Y][X] == GivenSurroundings:

                    intRand = random.randint(1,100)

                    if intRand > 100 - intSpawnChance:
                        self.Grid[Y][X] = GivenNoise

    #Iterate through our grid and compare it to 
    def RefineFeature(self, intPasses, givenCell, givenSurroundings, intGivenAdjRule, intGivenAdjNotRule):
          
        #Refinement gets better the more times we do it!
        for PassNumber in range(intPasses):
     
            #New grid after this pass
            arrNewGrid = []

            for YCount, YValue in enumerate(self.Grid):
             
                #New row in this grid
                arrNewRow = []
                for XCount, XValue in enumerate(YValue):
                                   
                    #How many of the noise type have we counted surrounding this
                    intSurroundingAmount = 0

                    #Have we checked all the surroundings at this location?
                    bChecked = False

                    #Change the point we start checking the surroundings from to avoid counting off the grid     
                    
                    SearchY = YCount
                    SearchX = XCount
                            
                    #If in top row, no surroundings above this                      
                    if YCount > 0:                 #           ---------       
                                                   #               X
                        SearchY -= 1

                  
                    #If in leftmost column, no need to check to the left of it
                    if XCount > 0:                 #               | 
                                                   #               |X
                        SearchX -= 1
                     
                    #For use 
                    InitialX = SearchX
                                  
                    #While we havent checked all the surroundings
                    while bChecked == False: 
                        
                        #If the surrounding cell we are comparing atm is of the given type, we increment our amount of surrounding cells
                        if self.Grid[SearchY][SearchX] == givenCell:
                            intSurroundingAmount += 1
                        
                        #If we've just looked at something from the end of the row
                        if SearchX > XCount or SearchX > self.GridDims[1] -2:
                            
                            #If we've just looked at something from the last
                            if SearchY > YCount or SearchY > self.GridDims[0] -2:
                            
                                bChecked = True
                            else:
                                
                                SearchY += 1
                                SearchX = InitialX
                        else:
                            SearchX += 1

                    #Now we tally up our surroundings and see if we can class this as a feature in the next iteration

                    #Might need to alter this; needs to be able to see if of same type - and same char...
                    if XValue ==  givenCell:
                        if intSurroundingAmount >= intGivenAdjRule:
                            arrNewRow.append(givenCell)
                        else:
                            arrNewRow.append(givenSurroundings)
                    else:
                        if intSurroundingAmount >= intGivenAdjNotRule:
                            arrNewRow.append(givenCell)
                        else:
                            arrNewRow.append(XValue)

                arrNewGrid.insert(YCount, arrNewRow)
            self.Grid = arrNewGrid