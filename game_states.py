def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)


GameStates = enum(PLAYERS_TURN=1,
                  ENEMY_TURN=2,
                  PLAYER_DEAD=3)
