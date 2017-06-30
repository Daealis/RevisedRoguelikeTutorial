import libtcodpy as libtcod

from entity import Entity
from input_handlers import handle_keys
from map_objects.game_map import GameMap
from render_functions import clear_all, render_all, load_customfont, player_tile


def main():
    screen_width = 50
    screen_height = 30
    map_width = 45
    map_height = 30


    colors = {
        'dark_wall': libtcod.Color(30, 30, 100),
        'dark_ground': libtcod.Color(80, 80, 160)
    }

    player = Entity(int(screen_width / 2), int(screen_height / 2), '@', libtcod.white, player_tile)
    npc = Entity(int(screen_width / 2 - 5), int(screen_height / 2), '@', libtcod.yellow,player_tile)
    entities = [npc, player]

    #libtcod.console_set_custom_font('prestige10x10_gs_tc.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)

    # The font has 32 chars in a row, and there's a total of 10 rows. Increase the "10" when you add new rows to the sample font file
    libtcod.console_set_custom_font('nethack16x16.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD, 32, 10)

    load_customfont()

    libtcod.console_init_root(screen_width, screen_height, 'libtcod tutorial revised', False)

    con = libtcod.console_new(screen_width, screen_height)

    game_map = GameMap(map_width, map_height)

    key = libtcod.Key()
    mouse = libtcod.Mouse()

    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)

        render_all(con, entities, game_map, screen_width, screen_height, colors)
        libtcod.console_flush()

        clear_all(con, entities)

        action = handle_keys(key)

        move = action.get('move')
        exit = action.get('exit')
        fullscreen = action.get('fullscreen')

        if move:
            dx, dy = move
            if not game_map.is_blocked(player.x + dx, player.y + dy):
                player.move(dx, dy)

        if exit:
            return True

        if fullscreen:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())


if __name__ == '__main__':
     main()
