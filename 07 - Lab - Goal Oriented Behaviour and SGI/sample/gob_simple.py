'''Goal Oriented Behaviour

Created for COS30002 AI for Games, Lab,
by Clinton Woodward <cwoodward@swin.edu.au>

For class use only. Do not publically share or post this code without
permission.

Works with Python 3+

Simple decision approach.
* Choose the most pressing goal (highest insistence value)
* Find the action that fulfills this "goal" the most (ideally?, completely?)

Goal: Eat (initially = 4)
Goal: Sleep (initially = 3)

Action: get raw food (Eat -= 3)
Action: get snack (Eat -= 2)
Action: sleep in bed (Sleep -= 4)
Action: sleep on sofa (Sleep -= 2)


Notes:
* This version is simply based on dictionaries and functions.

'''

VERBOSE = True

# Global goals with initial values
goals = {
    'Eat': 4,
    'Sleep': 3,
}

# Global (read-only) actions and effects
actions = {
    'get raw food': { 'Eat': -3 },
    'get snack': { 'Eat': -2 },
    'sleep in bed': { 'Sleep': -4 },
    'sleep on sofa': { 'Sleep': -2 }
}


def apply_action(action):
    '''Change all goal values using this action. An action can change multiple
    goals (positive and negative side effects).
    Negative changes are limited to a minimum goal value of 0.
    '''
    for goal, change in actions[action].items():
        goals[goal] = max(goals[goal] + change, 0)


def action_utility(action, goal):
    '''Return the 'value' of using "action" to achieve "goal".

    For example::
        action_utility('get raw food', 'Eat')

    returns a number representing the effect that getting raw food has on our
    'Eat' goal. Larger (more positive) numbers mean the action is more
    beneficial.
    '''
    ### Simple version - the utility is the change to the specified goal

    if goal in actions[action]:
        # Is the goal affected by the specified action?
        return -actions[action][goal]
    else:
        # It isn't, so utility is zero.
        return 0

    ### Extension
    ###
    ###  - return a higher utility for actions that don't change our goal past zero
    ###  and/or
    ###  - take any other (positive or negative) effects of the action into account
    ###    (you will need to add some other effects to 'actions')


def choose_action():
    '''Return the best action to respond to the current most insistent goal.
    '''
    assert len(goals) > 0, 'Need at least one goal'
    assert len(actions) > 0, 'Need at least one action'

    # Find the most insistent goal - the 'Pythonic' way...
    best_goal, best_goal_value = max(goals.items(), key=lambda item: item[1])

    # ...or the non-Pythonic way. (This code is identical to the line above.)
    #best_goal = None
    #for key, value in goals.items():
    #    if best_goal is None or value > goals[best_goal]:
    #        best_goal = key

    if VERBOSE: print('BEST_GOAL:', best_goal, goals[best_goal])

    # Find the best (highest utility) action to take.
    # (Not the Pythonic way... but you can change it if you like / want to learn)
    best_action = None
    best_utility = None
    for key, value in actions.items():
        # Note, at this point:
        #  - "key" is the action as a string,
        #  - "value" is a dict of goal changes (see line 35)

        # Does this action change the "best goal" we need to change?
        if best_goal in value:

            # Do we currently have a "best action" to try? If not, use this one
            if best_action is None:
                pass
                ### 1. store the "key" as the current best_action
                ### ...
                ### 2. use the "action_utility" function to find the best_utility value of this best_action
                ### ...

            # Is this new action better than the current action?
            else:
                pass
                ### 1. use the "action_utility" function to find the utility value of this action
                ### ...
                ### 2. If it's the best action to take (utility > best_utility), keep it! (utility and action)
                ### ...

    # Return the "best action"
    return best_action


#==============================================================================

def print_actions():
    print('ACTIONS:')
    # for name, effects in list(actions.items()):
    #     print(" * [%s]: %s" % (name, str(effects)))
    for name, effects in actions.items():
        print(" * [%s]: %s" % (name, str(effects)))


def run_until_all_goals_zero():
    HR = '-'*40
    print_actions()
    print('>> Start <<')
    print(HR)
    running = True
    while running:
        print('GOALS:', goals)
        # What is the best action
        action = choose_action()
        print('BEST ACTION:', action)
        # Apply the best action
        apply_action(action)
        print('NEW GOALS:', goals)
        # Stop?
        if all(value == 0 for goal, value in goals.items()):
            running = False
        print(HR)
    # finished
    print('>> Done! <<')


if __name__ == '__main__':
    # print(actions)
    # print(actions.items())
    # for k, v in actions.items():
    #     print(k,v)
    # print_actions()

    run_until_all_goals_zero()
