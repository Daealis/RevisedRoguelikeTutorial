import libtcodpy as libtcod

from components.fighter import Fighter
from components.inventory import Inventory
from death_functions import kill_player, kill_monster
from entity import Entity, get_blocking_entities_at_location
from fov_functions import initialize_fov, recompute_fov
from game_messages import Message, MessageLog
from game_states import GameStates
from input_handlers import handle_keys, handle_mouse
from map_objects.game_map import GameMap
from render_functions import clear_all, render_all, RenderOrder


def main():
    screen_width = 100
    screen_height = 70

    map_width = 80
    map_height = 63

    # The UI with Health, mouseover info and combat log
    bar_width = 20
    panel_height = 7
    panel_y = screen_height - panel_height

    message_x = bar_width + 2
    message_width = screen_width - bar_width - 2
    message_height = panel_height - 1

    # Definitions for the map
    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    # For libtcod to calculate the FOV
    fov_algorithm = 0
    fov_light_walls = True
    fov_radius = 10

    # Definitions for what can spawn in the rooms
    max_monsters_per_room = 3
    max_items_per_room = 2

    # Define the colors we'll be using
    colors = {
        'dark_wall': libtcod.Color(10, 10, 5),
        'dark_ground': libtcod.Color(10, 30, 10),
        'light_wall': libtcod.Color(50, 50, 20),
        'light_ground': libtcod.Color(30, 70, 30)
    }

    # Initialize the player character
    fighter_component = Fighter(hp=30, defense=2, power=5)
    inventory_component = Inventory(26)

    player = Entity(0, 0, '@', libtcod.white, 'Player', blocks=True, render_order=RenderOrder.ACTOR,
                    fighter=fighter_component, inventory=inventory_component)

    # Add our player to a list of all the entities
    entities = [player]

    # Setup libtcod and initialize the panels on the screen
    libtcod.console_set_custom_font('prestige10x10_gs_tc.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)

    libtcod.console_init_root(screen_width, screen_height, 'libtcod tutorial revised', False)

    con = libtcod.console_new(screen_width, screen_height)
    panel = libtcod.console_new(screen_width, panel_height)

    # Prepare the game map
    game_map = GameMap(map_width, map_height)
    game_map.make_map(max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities,
                      max_monsters_per_room, max_items_per_room)

    # Calculate the Fog of War on the map
    fov_recompute = True
    fov_map = initialize_fov(game_map)

    # Initialize the combat log
    message_log = MessageLog(message_x, message_width, message_height)

    # Set variables to receive both keypresses and mouse movements
    key = libtcod.Key()
    mouse = libtcod.Mouse()

    game_state = GameStates.PLAYERS_TURN
    previous_game_state = game_state

    targeting_item = None

    # The Main game loop
    while not libtcod.console_is_window_closed():
        # If wait until a key is pressed
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, fov_radius, fov_light_walls, fov_algorithm)

        render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, message_log, screen_width,
                   screen_height, bar_width, panel_height, panel_y, mouse, colors, game_state)

        fov_recompute = False
        libtcod.console_flush()

        clear_all(con, entities)

        # Define actions
        action = handle_keys(key, game_state)
        mouse_action = handle_mouse(mouse)

        move = action.get('move')
        wait = action.get('wait')
        pickup = action.get('pickup')
        show_inventory = action.get('show_inventory')
        drop_inventory = action.get('drop_inventory')
        inventory_index = action.get('inventory_index')
        exit = action.get('exit')
        fullscreen = action.get('fullscreen')

        left_click = mouse_action.get('left_click')
        right_click = mouse_action.get('right_click')

        player_turn_results = []

        # Move the player character
        if move and game_state == GameStates.PLAYERS_TURN:
            dx, dy = move
            destination_x = player.x + dx
            destination_y = player.y + dy

            if not game_map.is_blocked(destination_x, destination_y):
                target = get_blocking_entities_at_location(entities, destination_x, destination_y)

                # If the square contained an enemy, attack it
                if target:
                    attack_results = player.fighter.attack(target)
                    player_turn_results.extend(attack_results)
                # Otherwise, move into the square and recalculate Field of Vision
                else:
                    player.move(dx, dy)

                    fov_recompute = True
                game_state = GameStates.ENEMY_TURN

        # If the player told to pick up an item
        elif pickup and game_state == GameStates.PLAYERS_TURN:
            for entity in entities:
                # If there is an item at the coordinates, try to add it to inventory. If full, it'll fail
                if entity.item and entity.x == player.x and entity.y == player.y:
                    pickup_results = player.inventory.add_item(entity)
                    player_turn_results.extend(pickup_results)

                    break
            else:
                message_log.add_message(Message('There is nothing here to pick up.', libtcod.yellow))
        # If the player hits wait, move straight to the enemy turn
        elif wait and game_state == GameStates.PLAYERS_TURN:
            game_state = GameStates.ENEMY_TURN

        # Inventory handling

        # Show the inventory
        if show_inventory:
            previous_game_state = game_state
            game_state = GameStates.SHOW_INVENTORY

        # Show the drop inventory
        if drop_inventory:
            previous_game_state = game_state
            game_state = GameStates.DROP_INVENTORY

        # Select an item from the inventory
        if inventory_index is not None and previous_game_state != GameStates.PLAYER_DEAD and inventory_index < len(
                player.inventory.items):
            item = player.inventory.items[inventory_index]

            if game_state == GameStates.SHOW_INVENTORY:
                player_turn_results.extend(player.inventory.use(item, entities=entities, fov_map=fov_map))
            elif game_state == GameStates.DROP_INVENTORY:
                player_turn_results.extend(player.inventory.drop_item(item))

        """
        Targeting mode
        Left-click on mouse sets target coordinates and uses the item
        Right-click cancels targeting
        
        """
        if game_state == GameStates.TARGETING:
            if left_click:
                target_x, target_y = left_click

                item_use_results = player.inventory.use(targeting_item, entities=entities, fov_map=fov_map,
                                                        target_x=target_x, target_y=target_y)
                player_turn_results.extend(item_use_results)
            elif right_click:
                player_turn_results.append({'targeting_cancelled': True})

        if exit:
            if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
                game_state = previous_game_state
            elif game_state == GameStates.TARGETING:
                player_turn_results.append({'targeting_cancelled': True})
            else:
                return True

        if fullscreen:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

        # Process the results from player turn
        for player_turn_result in player_turn_results:
            dead_entity = player_turn_result.get('dead')
            item_added = player_turn_result.get('item_added')
            item_consumed = player_turn_result.get('consumed')
            item_dropped = player_turn_result.get('item_dropped')
            message = player_turn_result.get('message')
            targeting = player_turn_result.get('targeting')
            targeting_cancelled = player_turn_result.get('targeting_cancelled')

            # If there's a message, add to log
            if message:
                message_log.add_message(message)

            #Player cancels targeting
            if targeting_cancelled:
                game_state = previous_game_state

                message_log.add_message(Message('Targeting cancelled'))

            # If something died, put a message to the log and if it was the player, react accordingly
            if dead_entity:
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity)
                else:
                    message = kill_monster(dead_entity)

                message_log.add_message(message)

            # Item requires targeting
            if targeting:
                previous_game_state = GameStates.PLAYERS_TURN
                game_state = GameStates.TARGETING

                targeting_item = targeting

                message_log.add_message(targeting_item.item.targeting_message)
            # If the player picked up an item, remove it from the world
            if item_added:
                entities.remove(item_added)

                game_state = GameStates.ENEMY_TURN

            # If player used an item, switch to enemy turn
            if item_consumed:
                game_state = GameStates.ENEMY_TURN

            # If an item was dropped, add it to the game world
            if item_dropped:
                entities.append(item_dropped)

                game_state = GameStates.ENEMY_TURN

        # The enemy turn starts here
        if game_state == GameStates.ENEMY_TURN:
            # Go through all entities in the list
            for entity in entities:
                # If it has an AI, make a move
                if entity.ai:
                    enemy_turn_results = entity.ai.take_turn(player, fov_map, game_map, entities)

                    # Handle all the messages from entities
                    for enemy_turn_result in enemy_turn_results:
                        message = enemy_turn_result.get('message')
                        dead_entity = enemy_turn_result.get('dead')

                        # If there's a message, log it
                        if message:
                            message_log.add_message(message)

                        # If something died, make that happen
                        if dead_entity:
                            if dead_entity == player:
                                message, game_state = kill_player(dead_entity)
                            else:
                                message = kill_monster(dead_entity)

                            message_log.add_message(message)

                            if game_state == GameStates.PLAYER_DEAD:
                                break

                    if game_state == GameStates.PLAYER_DEAD:
                        break

            else:
                game_state = GameStates.PLAYERS_TURN


if __name__ == '__main__':
    main()
