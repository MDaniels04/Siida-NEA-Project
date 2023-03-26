import pyglet.clock as PC
#Our time manager houses all our necessary time functions - the day function, the tracking of time throughout the year (i.e.: the month) - 

#We do not factor in leap years!

class TimeManager():
    
    def __init__(self, Given__World):
        #What day number is this? (cumulative from the start of the simulation)
        self.DayNumber = 0
    
        #Passed in here as the world we want to affect on a day to day basis...
        self.__World = Given__World

        #Flavour text explaining more about today - is it a special sami holiday? Is there any information in particular we wish to begin
        self.__DayDictionary = {
        1: "Preparations shall begin for the migration out of the forest and into the mountains as the temperature begins to rise",
        236: "Today is Bar’debei-vâk’ko (St Bartholomew's day)",
        274: "With the threat of the harsh winter looming ever closer, preparations for migrating out of the mountains are beginning",
        335: "The frigid conditions and lack of sunlight force the Siida to begin their migration to the forests"}

        #If there are no messages about today in particular, we will get one of these
        self.__DefaultDayDictionary = {
        0: "Members of the Siida gather this evening to sing Joiks and tell tales of adventure across the island",
        1: "The residents play games of Sáhkku (A traditional Sami board game) in between tasks",
        2: "The Siida members aren't doing anything special today, aside from their tasks",
        3: "Residents spend the evening performing lihkadus (ecstasy dances)"
        }

    #Checks that need to be ran every 2 seconds - essentially think of this as our upate function...
    #given world is what we set our 
    #No real use for delta? Pyglet has to pass it in though...
    def Day(self, Delta):
        self.DayNumber += 1
        print("----------------------------------------------------------------")


        
        
        #What day of the year is this?
        DayOfYear = self.DayNumber % 365        

        if len(self.__World.Siida.SiidaResidents) < 1:
           PC.unschedule(self.Day)
           print("E V E R Y O N E I S D E A D")
           print("---------------------------")
           print("This Siida survived ", self.DayNumber, " days (", self.DayNumber // 365, " years, ", DayOfYear, " days)")

        else:

                                                                                 #Repeating values
            print(self.__DayDictionary.get(DayOfYear, self.__DefaultDayDictionary[DayOfYear % 4]))
            
            #All the AI Stuff
            self.__World.DailyFunction()
            print("----------------------------------------------------------------")
            print("Year number - ", (self.DayNumber // 365) + 1, "Day number - ", DayOfYear)
            print("Total days - ", self.DayNumber)
            print("Today it is ", self.__World.Weather.GlobalTemperature, " degrees!")


        #We now need to update the cells - dont worry its not hard      
                        
      

        #Goal assignment stuff
        
        #The general gist of how this works is we go through AI in our Siida, and assign the stack of goals to assign to them if there are any
        #The highest priority ones will supercede any others...

        #IF there are problems that need addressing
       #if len(self.__World.Siida.Problems) > 0:
        

        #For wild animals its a lot less set in stone - 