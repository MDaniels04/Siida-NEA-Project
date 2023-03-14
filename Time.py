
#Our time manager houses all our necessary time functions - the day function, the tracking of time throughout the year (i.e.: the month) - 

class TimeManager():
    
    def __init__(self, GivenWorld):
        #What day number is this? (cumulative from the start of the simulation)
        self.DayNumber = 0
    
        #Passed in here as the world we want to affect on a day to day basis...
        self.World = GivenWorld

    #Checks that need to be ran every 2 seconds - essentially think of this as our upate function...
    #given world is what we set our 
    #No real use for delta? Pyglet has to pass it in though...
    def Day(self, Delta):
        self.DayNumber += 1
            
        self.World.DailyFunction()
        print("----------------------------------------------------------------")
        print("Day number - ", self.DayNumber)
        print("Today it is ", self.World.Weather.GlobalTemperature, " degrees!")

        #We now need to update the cells - dont worry its not hard      
                        
      

        #Goal assignment stuff
        
        #The general gist of how this works is we go through AI in our Siida, and assign the stack of goals to assign to them if there are any
        #The highest priority ones will supercede any others...

        #IF there are problems that need addressing
       #if len(self.World.Siida.Problems) > 0:
        

        #For wild animals its a lot less set in stone - 