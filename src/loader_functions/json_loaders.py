import json

from entity import Entity
from game_messages import MessageLog
from game_states import GameStates
from game_time import Time
from map_objects.game_map import GameMap
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
    game_weather_json = data['game_weather']
    game_time_json = data['game_time']
    
    entities = [Entity.from_json(json_data=entity_json) for entity_json in entities_json]
    player = entities[player_index]
    game_map = GameMap.from_json(json_data=game_map_json)
    message_log = MessageLog.from_json(json_data=message_log_json)
    game_state = GameStates(game_state_json)
    game_weather = Weather.from_json(json_data=game_weather_json)
    game_time = Time.from_json(json_data=game_time_json)
    
    return player, entities, game_map, message_log, game_state, game_weather, game_time


def entity_test_dump(entities):
    data = {
        'entities': [entity.to_json() for entity in entities]
    }

    with open('saved_entities.json', 'w') as save_file:
        json.dump(data, save_file, indent=4)


def entities_test_load():
    with open('saved_entities.json') as save_file:
        data = json.load(save_file)
        
        entities_json = data['entities']
        
        entities = [Entity.from_json(json_data=entity) for entity in entities_json]
        
        return entities


def map_test_dump(game_map):
    data = {
        'game_map': game_map.to_json()
    }
    
    with open('saved_map.json', 'w') as save_file:
        json.dump(data, save_file, indent=4)


def map_test_load():
    with open('saved_map.json') as save_file:
        data = json.load(save_file)
        
        game_map_json = data['game_map']
        
        game_map = GameMap.from_json(json_data=game_map_json)
        
        return game_map


def weather_test_dump(game_weather):
    data = {
        'weather': game_weather.to_json()
    }

    with open('saved_weather.json', 'w') as save_file:
        json.dump(data, save_file, indent=4)


def weather_test_load():
    with open('saved_weather.json') as save_file:
        data = json.load(save_file)
        
        weather_json = data['weather']
        
        game_weather = Weather.from_json(json_data=weather_json)
        
        return game_weather


def time_test_dump(game_time):
    data = {
        'time': game_time.to_json()
    }

    with open('saved_time.json', 'w') as save_file:
        json.dump(data, save_file, indent=4)


def time_test_load():
    with open('saved_time.json') as save_file:
        data = json.load(save_file)
        
        time_json = data['time']
        
        game_time = Time.from_json(json_data=time_json)
        
        return game_time


def log_test_dump(message_log):
    data = {
        'message_log': message_log.to_json()
    }

    with open('saved_log.json', 'w') as save_file:
        json.dump(data, save_file, indent=4)


def log_test_load():
    with open('saved_log.json') as save_file:
        data = json.load(save_file)

        message_log_json = data['message_log']
        
        message_log = MessageLog.from_json(json_data=message_log_json)
    
        return message_log
