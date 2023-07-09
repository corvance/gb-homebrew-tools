# maketileset.py
# Corvance 05-07-2023

import argparse
from PIL import Image
from itertools import islice
import sys
import os
import struct 

parser = argparse.ArgumentParser(
    prog="maketileset",
    description="Tool to create a Game Boy tileset from a given image, removing duplicate tiles.",
)

parser.add_argument('-i', '--image', help="Path to the image file.", required=True, dest="img_path", metavar="IMAGE PATH")
parser.add_argument('-f', '--format', help="Output format. Binary = b, RGBDS Assembly = a. Default is binary.", dest="out_format", choices=["b", "a"], default="b", metavar="OUTPUT FORMAT")
args = parser.parse_args()

img = Image.open(args.img_path)

if img.width % 8 != 0 or img.height % 8 != 0:
    print("ERR: Image dimensions are not multiples of 8; cannot split into tiles.")
    exit()

img = img.convert("P", palette=Image.ADAPTIVE, colors=4)

tiles = []
for i in range(0, img.height, 8):
    for j in range(0, img.width, 8):
        tiles.append(list(img.crop((j, i, j + 8, i + 8)).getdata()))

for tile in tiles:
    for i in range(0, len(tile)):
        tile[i] = 3 - tile[i]

if args.out_format == "b":
    dest = open(os.path.splitext(args.img_path)[0] + ".2bpp", "wb")
else:
    dest = open(os.path.splitext(args.img_path)[0] + ".asm", "w")
        
for tile in [list(tupl) for tupl in {tuple(item) for item in tiles }]:
    if args.out_format == "a":
        dest.write("db ")
    for row in [tile[x:x+8] for x in range(0, len(tile), 8)]:
        tile_bytes = [0, 0]
        for color in range(0, len(row)):
            tile_bytes[0] |= ((row[color] & 0b01) << (7 - color)) 
            tile_bytes[1] |= (((row[color] & 0b10) >> 1) << (7 - color))
            
        if args.out_format == "b":
            dest.write(struct.pack('2B', *tile_bytes))
        else:
            dest.write(("$%0.2X" % tile_bytes[0]) + " " + ("$%0.2X" % tile_bytes[1]) + " ")
            
    if args.out_format == "a":
        dest.write("\n")
