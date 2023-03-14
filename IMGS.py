import pyglet.resource as PR
import pyglet.graphics as PG



#This is just our resource stuff - decided to put it all in a seperate file because that's a little bit neater...
CoastIMG = PR.image("Temp art/OceanNew.png")
LandIMG = PR.image("Temp art/Land Temp.png")
HillIMG = PR.image("Temp art/Hill Temp.png")
MountainIMG = PR.image("Temp art/Mountain Temp.png")
TreeIMG = PR.image("Temp art/Tree Temp.png")
PersonIMG = PR.image("Temp art/Person Temp.png")
CloudIMG = PR.image("Temp art/Cloud.png")
ReindeerIMG = PR.image("Temp art/Reindeer Temp.png")
LavvuIMG = PR.image("Temp art/Lavvu.png")

Terrain = PG.OrderedGroup(0)
People = PG.OrderedGroup(1)
Weather = PG.OrderedGroup(3)