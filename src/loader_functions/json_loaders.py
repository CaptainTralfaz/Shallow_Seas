import json

from entity import Entity
from game_messages import MessageLog
from game_states import GameStates
from map_objects.game_map import GameMap
from game_time import Time
from weather import Weather


def save_game(player, entities, game_map, message_log, game_state, game_weather, game_time):
    data = {
        'player_index': entities.index(player),
        'entities': [entity.to_json() for entity in entities],
        'game_map': game_map.to_json(),
        'message_log': message_log.to_json(),
        'game_state': game_state.value,
        'game_weather': game_weather.to_json(),
        'game_time': game_time.to_json()
    }
    
    with open('save_game.json', 'w') as save_file:
        json.dump(data, save_file, indent=4)
        

def load_game():
    with open('save_game.json') as save_file:
        data = json.load(save_file)

    player_index = data['player_index']
    entities_json = data['entities']
    game_map_json = data['game_map']
    message_log_json = data['message_log']
    game_state_json = data['game_state']
    game_weather_json = data['weather']
    game_time_json = data['game_time']

    entities = [Entity.from_json(entity_json) for entity_json in entities_json]
    player = entities[player_index]
    game_map = GameMap.from_json(game_map_json)
    message_log = MessageLog.from_json(message_log_json)
    game_state = GameStates(game_state_json)
    game_weather = Weather.from_json(game_weather_json)
    game_time = Time.from_json(game_time_json)

    return player, entities, game_map, message_log, game_state, game_weather, game_time
