import json

world_cup_str = """
[
    {
        "team_1": "France",
        "team_2": "Croatia",
        "game_type": "Final",
        "score" : [4, 2]
    },
    {
        "team_1": "Belgium",
        "team_2": "England",
        "game_type": "3rd/4th Playoff",
        "score" : [2, 0]
    }
]
"""
# Reading a JSON file
# convert json to list
world_cup_obj = json.loads(world_cup_str)

with open("hn_2014.json", "r") as file:
    hn = json.load(file)

# Deleting Dictionary Keys
def del_key(dict_, key):
    # create a copy so we don't
    # modify the original dict
    modified_dict = dict_.copy()
    del modified_dict[key]
    return modified_dict


hn_clean = []
for d in hn:
    new_d = del_key(d, "createdAtI")
    hn_clean.append(new_d)

# Writing List Comprehensions

# LOOP VERSION
#
# hn_clean = []
#
# for d in hn:
#     new_d = del_key(d, 'createdAtI')
#     hn_clean.append(new_d)

hn_clean = [del_key(d, 'createdAtI') for d in hn]

# Using List Comprehensions to Transform and Create Lists

urls = [d["url"] for d in hn_clean]

# Using List Comprehensions to Reduce a List

