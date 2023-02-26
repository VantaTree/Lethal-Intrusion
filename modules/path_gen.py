import pytmx
import os
import csv

SAVE_PATH = "data/map_paths"
READ_PATH = "data/maps"
SOLID_BLOCKS = (1, 2, 3, 4)
EMPTY_BLOCKS = (0,)

def generate_path(map_name:str):

    tmx_data = pytmx.TiledMap(F"{READ_PATH}/{map_name}.tmx")

    collision_layer = tmx_data.get_layer_by_name("collision")
    coll_data = collision_layer.data

    for tileset in tmx_data.tilesets:
        if tileset.name == "collision":
            coll_firstgid = tileset.firstgid
            break

    path_data = [ [0]*collision_layer.width for _ in range(collision_layer.height) ]
    end_nodes = set()

    for y in range(collision_layer.height-1):
        for x in range(collision_layer.width):
            cell = tmx_data.tiledgidmap[coll_data[y][x]] - coll_firstgid

            if cell not in EMPTY_BLOCKS: continue
            if tmx_data.tiledgidmap[coll_data[y+1][x]] - coll_firstgid in EMPTY_BLOCKS: continue

            path_data[y][x] = 1

            for i in range(2):
                try:
                    if tmx_data.tiledgidmap[coll_data[y+i][x+1]] - coll_firstgid not in EMPTY_BLOCKS:
                        break
                except IndexError: pass
            else:
                try:
                    path_data[y][x+1]
                    end_nodes.add((x+1, y))
                except IndexError: pass

            for i in range(2):
                try:
                    if tmx_data.tiledgidmap[coll_data[y+i][x-1]] - coll_firstgid not in EMPTY_BLOCKS:
                        break
                except IndexError: pass
            else:
                try:
                    path_data[y][x-1]
                    end_nodes.add((x-1, y))
                except IndexError: pass

    for x, y in end_nodes:
        for iy in range(y, collision_layer.height):
            if tmx_data.tiledgidmap[coll_data[iy][x]]  - coll_firstgid not in EMPTY_BLOCKS:break
            path_data[iy][x] = 1
            

    with open(F'{SAVE_PATH}/{map_name}.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerows(path_data)

def generate_all_path():

    for file in os.listdir(READ_PATH):

        if not file.endswith(".tmx") or file == "template.tmx": continue

        generate_path(file[:-4])

generate_all_path()
