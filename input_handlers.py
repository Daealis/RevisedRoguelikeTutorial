"""
Input Handlers
----
Housed here are all the input handlers, one for each game state.
"""
import libtcodpy as libtcod

from game_states import GameStates


def handle_keys(key, game_state):
    if game_state == GameStates.PLAYERS_TURN:
        return handle_player_turn_keys(key)
    elif game_state == GameStates.PLAYER_DEAD:
        return handle_player_dead_keys(key)
    elif game_state == GameStates.TARGETING:
        return handle_targeting_keys(key)
    elif game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        return handle_inventory_keys(key)
    elif game_state == GameStates.LEVEL_UP:
        return handle_level_up_menu(key)
    elif game_state == GameStates.CHARACTER_SCREEN:
        return handle_character_screen(key)

    return {}


def handle_player_turn_keys(key):
    # Movement keys
    key_char = chr(key.c)

    if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8:
        return {'move': (0, -1)}
    elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2:
        return {'move': (0, 1)}
    elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
        return {'move': (-1, 0)}
    elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
        return {'move': (1, 0)}
    elif key_char == 'y' or key.vk == libtcod.KEY_KP7:
        return {'move': (-1, -1)}
    elif key_char == 'u' or key.vk == libtcod.KEY_KP9:
        return {'move': (1, -1)}
    elif key_char == 'b' or key.vk == libtcod.KEY_KP1:
        return {'move': (-1, 1)}
    elif key_char == 'n' or key.vk == libtcod.KEY_KP3:
        return {'move': (1, 1)}
    elif key.vk == libtcod.KEY_SPACE or key.vk == libtcod.KEY_KP5:
        return {'wait': True}

    # Pickup items
    if key_char == 'g':
        return {'pickup': True}

    # Open the inventory screen
    elif key_char == 'i':
        return {'show_inventory': True}

    # Open inventory for item dropping
    elif key_char == 'd':
        return {'drop_inventory': True}

    # Show the character screen
    elif key_char == 'c':
        return {'show_character_screen': True}

    # Take the stairs to the next level
    elif key.vk == libtcod.KEY_ENTER:
        return {'take_stairs': True}

    # Alt+Enter: Toggle full screen on / off
    if key.vk == libtcod.KEY_ENTER and key.lalt:
        return {'fullscreen': True}

    # Exit the game with esc
    elif key.vk == libtcod.KEY_ESCAPE:
        return {'exit': True}

    # No key was pressed
    return {}


# Since targeting is done by mouse, the only key needed is for cancelling the targeting
def handle_targeting_keys(key):
    if key.vk == libtcod.KEY_ESCAPE:
        return {'exit': True}

    return {}


# When you die, you can still check your character screen, inventory, toggle fullscreen and exit the game.
def handle_player_dead_keys(key):
    key_char = chr(key.c)

    if key_char == 'i':
        return {'show_inventory': True}

    elif key_char == 'c':
        return {'show_character_screen': True}

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        # Alt+Enter: toggle full screen
        return {'fullscreen': True}
    elif key.vk == libtcod.KEY_ESCAPE:
        # Exit the menu
        return {'exit': True}

    return {}


def handle_inventory_keys(key):
    # Simple transform from a keycode to an integer by deducing the first alphabet in ASCII from the code
    index = key.c - ord('a')

    if index >= 0:
        return {'inventory_index': index}

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        # Alt+Enter: toggle full screen
        return {'fullscreen': True}
    elif key.vk == libtcod.KEY_ESCAPE:
        # Exit the menu
        return {'exit': True}

    return {}


# Main menu with its options of New game, Load game and exit
def handle_main_menu(key):
    key_char = chr(key.c)

    if key_char == 'a':
        return {'new_game': True}
    elif key_char == 'b':
        return {'load_game': True}
    elif key_char == 'c' or key.vk == libtcod.KEY_ESCAPE:
        return {'exit': True}

    return {}


# Level up menu with a choice of our stats available
def handle_level_up_menu(key):
    if key:
        key_char = chr(key.c)

        if key_char == 'a':
            return {'level_up': 'hp'}
        elif key_char == 'b':
            return {'level_up': 'str'}
        elif key_char == 'c':
            return {'level_up': 'def'}

    return {}


def handle_character_screen(key):
    if key.vk == libtcod.KEY_ESCAPE:
        return {'exit': True}

    return {}


# Use the built-in mouse system in Libtcod and get the mouse coordinates and clicks
def handle_mouse(mouse):
    (x, y) = (mouse.cx, mouse.cy)

    if mouse.lbutton_pressed:
        return {'left_click': (x, y)}
    elif mouse.rbutton_pressed:
        return {'right_click': (x, y)}

    return {}
