'''
    MESSAGES ABOUT THE CODE

    Please ensure you have read the Readme.md file in this repository before continuing. Cheers - Morgz <3
    ------------------------------------------------------------------------------------------------------
    This code is the code for my AQA A Level computer science NEA project.

    While the simulation as it is may not do much impressive, I believe the systems implemented give the ability to modularly and easily add more "actions" for the AI to perform.
    I may add more of these if I have time after exams, but this depends on other projects throughout the summer.

'''
import World as W
import SaveManager as S

#Imports pyglet - our library for graphics etc.
import pyglet 

import IMGS
Saver = S.SaveManager()

#Clear the console so the text printed for handling saves is not present
print("\033c", end='')

#Initilaise our window
#Visible is set to false so we can do some additional initialisation before the window is shown
MainWindow = pyglet.window.Window(800, 800, caption="Siida Beta", visible=False,style=pyglet.window.Window.WINDOW_STYLE_DIALOG)

#Set the icon to an image of a resident
MainWindow.set_icon(IMGS.PersonIMG)

MainWindow.set_visible()

#Our sprite batch - all the sprites that are shown each day appear here
MainBatch = pyglet.graphics.Batch()

#The world initialised here - handles initialisation of all aspects of the simulation
World = W.World((50,50), MainBatch, Saver)

#Schedule the "day" function to be called every x seconds
pyglet.clock.schedule_interval(World.Time.Day, 10)

@MainWindow.event
def on_draw():
    MainWindow.clear()
    MainBatch.draw()

pyglet.app.run()

#Automatically save our world once the app has been closed
Saver.Save(World)
print("That's all folks!")