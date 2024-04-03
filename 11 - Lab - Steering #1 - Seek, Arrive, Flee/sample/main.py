'''Autonomous Agent Movement: Seek, Arrive and Flee

Created for COS30002 AI for Games, Lab,
by  Clinton Woodward <cwoodward@swin.edu.au>
    James Bonner <jbonner@swin.edu.au>

For class use only. Do not publically share or post this code without
permission.

Notes:
* If you want to respond to a key press, see the on_key_press function.
* The world contains the agents. In the main loop we tell the world
  to update() and then render(), which then tells each of the agents
  it has.

Updated 
 - 2019-03-17
 - 2024-04-03
'''
import pyglet
#importing graphics for side-effects - it creates the egi and window module objects. 
#This is the closest python has to a global variable and it's completely gross
import graphics
#game has to take another approach to exporting a global variable
#the game object is importable, but only contains the game object if it's being imported after the game object has been created below
import game

if __name__ == '__main__':
	game.game = game.Game()
	pyglet.clock.schedule_interval(game.game.update, 1/60.)
	pyglet.app.run()
