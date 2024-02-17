# Three state machine example ... bad code included.

# variables
tired = 0
hunger = 0

states = ['sleeping','awake','eating']
current_state = 'sleeping'

alive = True
running = True
max_limit = 100
game_time = 0

while running and alive:
    game_time += 1

    # Sleeping: reduced tired, hunger still increases
    if current_state is 'sleeping':
        # Do things for this state
        print("Zzzzzz")
        tired -= 1
        hunger += 1
        # Check for change state
        if tired < 5:
            current_state = 'awake'

    # Awake: does nothing interesting. gets hunugry. gets tired
    elif current_state is 'awake':
        # Do things for this state
        print("Bored.... BORED! ...")
        tired += 1
        hunger += 1
        # Check for change state
        if hunger > 7:
            current_state = 'eating'
        if tired > 16:
            current_state = 'sleeping'
            
    # Eating: reduces hunger, still gets tired
    elif current_state is 'eating':
        # Do things for this state
        print("Num, num, num...")
        tired += 1
        hunger -= 1
        # Check for change state
        if hunger < 8:
            current_state = 'awake'
            
    # check for broken ... :(
    else:
        print("AH! BROKEN .... how did you get here?")
        die() # not a real function - just breaks things! :)

    if hunger > 20:
        alive = False
        
    # Check for end of game time
    if game_time > max_limit:
        running = False

print('-- The End --')


    
