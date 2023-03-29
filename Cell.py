import Entity as E
import IMGS

class Cell(E.Entity):
    #Add other stuff when necessary, void just for this instance of testing our map generator...
    
    #Given rep -> The image that we use as a sprite for this image
    def __init__(self, GivenRep, GivenWeight, GivenLocation, GivenBatch, GivenChrRep, GivenTemperatureModifier = 0):

       super().__init__(GivenRep, GivenLocation, GivenBatch, IMGS.Terrain)

       #How would this be represented as a character (for the purpose of compressio in saving and loading) 
       self._ChrRep = GivenChrRep
        
       #Weight is simulated as a measure of difficulty to pass through a cell for one reason or another
       #Lower numbers better!
       self._Weight = GivenWeight
    
       #A signed amount that being in this cell offsets the temperature by (e.g.: colder in mountains)
       self.__TemperatureModifier = GivenTemperatureModifier

       #Precipitation in this cell
       # 0 -> It is not precipitating
       # 1 -> It is raining
       # 2 -> It is snowing
       self.Precipitating = 0

       self.ResourcesInCell = {

            "FoodSupply":0,

            "WoodSupply":0
}

    #Calculate the temperature in this cell
    def GetTemperature(self, GlobalTemp):
        return GlobalTemp + (self.Precipitating * -2) + self.__TemperatureModifier
