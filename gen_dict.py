#temporary only for making more dict keys in create_world in func.py
import json

#change these values
p_1 = [26, 35, 28, 16] # boven
p_2 = [19, 21, 34] # rechts
p_3 = [23, 26, 19] # onder
p_4 = [5] # links
tile_convert = 25

try:
    add_to_json = eval(input("add to json???"))
except Exception as e:
    print(e)
    add_to_json = False

#start of script
if p_1 != [] and p_2 != [] and p_3 != [] and p_4 != []:

    output_dict = {}

    for a in p_1:
        for b in p_2:
            for c in p_3:
                for d in p_4:
                    output_dict[f"{a}-{b}-{c}-{d}"] = tile_convert


    print(output_dict)

    if add_to_json:
        with open("convert_tiles.json") as f:
            convert_tiles_dict = json.load(f)
            convert_tiles_dict.update(output_dict) # add the output dict keys to the current ones
        with open("convert_tiles.json", "w") as f:
            json.dump(convert_tiles_dict, f)        


