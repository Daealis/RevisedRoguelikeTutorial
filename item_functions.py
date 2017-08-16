"""
Item Functions
----
Herein are all the different functions our items can have.
"""
import libtcodpy as libtcod

from components.ai import ConfusedMonster

from game_messages import Message

"""
Heal
Give the entity health back
"""


def heal(*args, **kwargs):
    entity = args[0]
    amount = kwargs.get('amount')

    results = []

    if entity.fighter.hp == entity.fighter.max_hp:
        results.append({'consumed': False, 'message': Message('You are already at full health', libtcod.yellow)})
    else:
        entity.fighter.heal(amount)
        results.append({'consumed': True, 'message': Message('Your wounds start to feel better!', libtcod.green)})

    return results


"""
Lightning Scroll
Targets the nearest entity with a fighter component 
on our characters Field of View and hits it with lightning
"""


def cast_lightning(*args, **kwargs):
    caster = args[0]
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    damage = kwargs.get('damage')
    maximum_range = kwargs.get('maximum_range')

    results = []

    target = None
    closest_distance = maximum_range + 1

    # Go through entities, find the nearest in fov that has a fighter component and zap it with damage
    for entity in entities:
        if entity.fighter and entity != caster and libtcod.map_is_in_fov(fov_map, entity.x, entity.y):
            distance = caster.distance_to(entity)

            if distance < closest_distance:
                target = entity
                closest_distance = distance

    if target:
        results.append({'consumed': True, 'target': target, 'message': Message(
            'A lighting bolt strikes the {0} with a loud thunder! The damage is {1}'.format(target.name, damage))})
        results.extend(target.fighter.take_damage(damage))
    else:
        results.append(
            {'consumed': False, 'target': None, 'message': Message('No enemy is close enough to strike.', libtcod.red)})

    return results


"""
Cast a fireball.
Targets a square picked out with a mouse click, explodes in target square and
damages everything around it, including the player.
"""


def cast_fireball(*args, **kwargs):
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    damage = kwargs.get('damage')
    radius = kwargs.get('radius')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')

    results = []

    # Require that the player see what they're trying to scorch
    if not libtcod.map_is_in_fov(fov_map, target_x, target_y):
        results.append({'consumed': False,
                        'message': Message('You cannot target a tile outside your field of view.', libtcod.yellow)})
        return results

    results.append({'consumed': True,
                    'message': Message('The fireball explodes, burning everything within {0} tiles!'.format(radius),
                                       libtcod.orange)})

    # Go through the entities and if it has a fighter component and it's close enough, burn it
    for entity in entities:
        if entity.distance(target_x, target_y) <= radius and entity.fighter:
            results.append({'message': Message('The {0} gets burned for {1} hit points.'.format(entity.name, damage),
                                               libtcod.orange)})
            results.extend(entity.fighter.take_damage(damage))

    return results


"""
Cast Confuse
Target an entity with a fighter component and 
cast confusion on it, resulting in its AI wandering in random patterns for 10 turns 
"""


def cast_confuse(*args, **kwargs):
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')

    results = []

    if not libtcod.map_is_in_fov(fov_map, target_x, target_y):
        results.append({'consumed': False,
                        'message': Message('You cannot target a tile outside your field of view.', libtcod.yellow)})
        return results

    # Find an entity that is under the mouse cursos
    for entity in entities:
        if entity.x == target_x and entity.y == target_y and entity.ai:
            # Make the entity confused for 10 turns
            confused_ai = ConfusedMonster(entity.ai, 10)

            confused_ai.owner = entity
            entity.ai = confused_ai

            results.append({'consumed': True, 'message': Message(
                'The eyes of the {0} look vacant, as he starts to stumble around!'.format(entity.name),
                libtcod.light_green)})

            break
    else:
        results.append(
            {'consumed': False, 'message': Message('There is no targetable enemy at that location.', libtcod.yellow)})

    return results
