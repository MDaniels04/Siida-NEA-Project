'''
    IMPORTANT MESSAGES
    
    This project was a None Examined Assesment for an AQA A level Computer Science course. As such it was developed with the intent to fit the criterea for such projects. It will not be updated any further than release.

    For unkown reasons, after testing on a secondary device, there were errors with pyglet group constructors - 
    They were expecting the constructor OrderedGroup([int]) rather than as it is in documentation, and in this code Group(order=[int]). 
    If you get errors running this code, try changing this in the IMGS.py file.

            ORDER GROUPS
            0 - MAP
            1 - STRUCTURES
            2 - AI
            3 -  WEATHER ETC.
            
    Sometimes stuff overlap, we might need to fix that....

'''
import World as W
import SaveManager as S

#Handles pyglet initialisation
import pyglet 

import IMGS

#import pdb; pdb.set_trace()

#save stuff
Saver = S.SaveManager()

#Clear the console so all that save jazz isnt there
print("\033c", end='')

#REMEMBER MAP DIMS = 800 X 800 (1 TILE = 16X16 SIZE...

#Visible false to begin with so we can add bonus initialisation 
MainWindow = pyglet.window.Window(800, 800, caption="Siida Beta", visible=False,style=pyglet.window.Window.WINDOW_STYLE_DIALOG)

"""
Additional initialisation of our window will take place here!
"""

MainWindow.set_icon(IMGS.PersonIMG)
MainWindow.set_visible()

#The batch of sprites - liable to change every day...
MainBatch = pyglet.graphics.Batch()

#The world
#Time stuff also handle
World = W.World((50,50), MainBatch, Saver)

#Call the day function every x seconds...
pyglet.clock.schedule_interval(World.Time.Day, 0.1)

@MainWindow.event
def on_draw():
    MainWindow.clear()
    MainBatch.draw()

pyglet.app.run()

#Automatically save our world once the app has been closed
Saver.Save(World)

print("That's all folks!")