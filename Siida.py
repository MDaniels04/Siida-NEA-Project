'''

    MESSAGES AND SUCH

    
    The comments on this are an absoloute mess between over annotating, under annotating, and comments reffering to code that no longer exists. Sorry.
    Some important notes about drawing:

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


#Might decide to increment the time between "days" idk...
#Moved time between days to 3 seconds for understanding purposes
pyglet.clock.schedule_interval(World.Time.Day, 3)

@MainWindow.event
def on_draw():
    MainWindow.clear()
    MainBatch.draw()

pyglet.app.run()

#Automatically save our world once the app has been closed
Saver.Save(World)

print("That's all folks!")