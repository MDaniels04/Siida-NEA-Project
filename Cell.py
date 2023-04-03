import Entity as E
import IMGS
class Cell(E.Entity):
    #Add other stuff when necessary, void just for this instance of testing our map generator...
    
    #Given rep -> The image that we use as a sprite for this image
    def __init__(self, GivenRep, GivenWeight, GivenLocation, GivenBatch, GivenChrRep, GivenTemperatureModifier = 0):

       super().__init__(GivenRep, GivenLocation, GivenBatch, IMGS.Terrain)

       #How would this be represented as a character (for the purpose of compressio in saving and loading) 
       self.__ChrRep = GivenChrRep
        
       #Weight is simulated as a measure of difficulty to pass through a cell for one reason or another
       #Lower numbers better!
       self.__Weight = GivenWeight
    
       #A signed amount that being in this cell offsets the temperature by (e.g.: colder in mountains)
       self.__TemperatureModifier = GivenTemperatureModifier

       #Precipitation in this cell
       # 0 -> It is not Precipitating
       # 1 -> It is raining
       # 2 -> It is snowing
       self.__Precipitating = 0

    #Calculate the temperature in this cell
    def _GetTemperature(self, GlobalTemp):
        return GlobalTemp + (self.__Precipitating * -2) + self.__TemperatureModifier

    def _GetWeight(self):
        return self.__Weight

    ####
    #   GETTERS AND SETTERS
    ####
    def _GetChrRep(self):
        return self.__ChrRep

    def _GetPrecipitating(self):
        return self.__Precipitating
    
    def _SetPrecipitating(self, Given):
        self.__Precipitating = Given