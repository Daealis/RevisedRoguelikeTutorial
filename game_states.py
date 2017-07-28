#Python 2.7 doesn't have an Enum, so we make our own
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)


GameStates = enum(PLAYERS_TURN=1,
                  ENEMY_TURN=2,
                  PLAYER_DEAD=3,
                  SHOW_INVENTORY=4,
                  DROP_INVENTORY=5,
                  TARGETING=6)
