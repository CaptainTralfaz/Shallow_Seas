rowboat = {"name": "rowboat",
           "type": "ship",
           "size": 0,
           "masts": None,
           "max_speed": 1,
           "view": 3,
           "hull_points": 5,
           "max_crew": 5,
           "propulsion": {
               "row": 1
           }
}

sloop = {"name": "sloop",
         "type": "ship",
         "size": 1,
         "masts": 1,
         "max_speed": 2,
         "view": 4,
         "hull_hp": 15,
         "max_crew": 15,
         "weapon_slots": "1F1A",
         "propulsion": {
             "row": 1,
             "wind": 1,
         },
}

red_dragon = {"name": "red_dragon",
              "type": "creature",
              "size": 3,
              "max_speed": 3,
              "view": 8,
              "body_hp": 20,
              "wing_hp": 10,
              "weapons": {
                  "fire_breath": {
                      "range": 3,
                      "direction": "front",
                      "damage": 5,
                      "effect": "fire"
                  },
                  "claw": {
                      "range": 0,
                      "damage": 3
                  },
              },
              "propulsion": {
                  "fly": 1,
                  "wind": 1,
              },
}

tower = {"name": "tower",
         "type": "structure",
         "size": 3,
         "view": 6,
         "structure_hp": 20,
         "weapons": {
             "ballista": {
                 "range": 6,
                 "weapon_hp": 5,
             },
         },
}