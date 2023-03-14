import Entity as E
import IMGS

class Cell(E.Entity):
    #Add other stuff when necessary, void just for this instance of testing our map generator...
    
    #Given rep -> The image that we use as a sprite for this image
    def __init__(self, GivenRep, GivenWeight, GivenLocation, GivenBatch, GivenChrRep, GivenTemperatureModifier = 0):

       super().__init__(GivenRep, GivenLocation, GivenBatch, IMGS.Terrain)

         
       #How would this be represented as a character (for the purpose of compressio in saving and loading) 
       self.ChrRep = GivenChrRep
        
       #Weight is simulated as a measure of difficulty to pass through a cell for one reason or another
       #Lower numbers better!
       self.Weight = GivenWeight

       #The weight we default back to, as weight may change depening on the climate in the cell
       self.DefaultWeight = GivenWeight
    
       #A signed amount that being in this cell offsets the temperature by (e.g.: colder in mountains)
       self.TemperatureModifier = GivenTemperatureModifier

       #Is it precipitating in this tile
       self.bPrecipitating = False

       #Amount of snow currently in the cell - used for calculations for sprites to display and weight differences, as well as whether or not to class it as blocked
       self.SnowInCell = 0

       #Keeping track of the entities currently in this cell - including structures...
       self.EntitiesInCell = []
       self.ResourcesInCell = {

            "FoodSupply":0,

            "WoodSupply":0
}
