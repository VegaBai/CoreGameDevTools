"""
require opencv

This small tool is built for batch process for Pixel Art Spawner in Core Game development.

1. Convert the picture to a indexed array
2. For each indexed color, do a matrix rectangle partition by always selecting the largest rectangle.
3. The final output is a rectangle list of the image. 
    {[color index], [col num of top-left corner of rect], [row num of top-left corner of rect], [horizontal length of rect], [vertical length of rect]}
4. Create the lua script that can be used in Pixel Art Spawner.
"""

import cv2 as cv
import numpy as np
import os
import sys
import math


PALETTE_NES = [
    "7c7c7cff",
    "0000fcff",#2
    "0000bcff",
    "4428bcff",#4
    "940084ff",
    "a80020ff",#6
    "a81000ff",
    "881400ff",#8
    "503000ff",
    "007800ff",#10
    "006800ff",
    "005800ff",
    "004058ff",
    "000000ff",#14
    
    
    "bcbcbcff",#15
    "4428bcff",
    "0058f8ff",#17
    "6844fcff",
    "d800ccff",
    "e40058ff",#20
    "f83800ff",
    "e45c10ff",
    "ac7c00ff",
    "00b800ff",#24
    "00a800ff",
    "00a844ff",
    "008888ff",
    "080808ff",#28
    
    "fcfcfcff",
    "3cbcfcff",#30
    "6888fcff",
    "9878f8ff",
    "f878f8ff",
    "f85898ff",#34
    "f87858ff",
    "fca044ff",
    "f8b800ff",
    "b8f818ff",#38
    "58d854ff",
    "58f898ff",
    "00e8d8ff",
    "7c7c7cff",#42
    
    "ffffffff",
    "a4e4fcff",
    "b8b8f8ff",#45
    "d8b8f8ff",
    "f8b8f8ff",
    "f8a4c0ff",#48
    "f0d0b0ff",
    "fce0a8ff",
    "f8d878ff",
    "d8f878ff",
    "b8f8b8ff",#53
    "b8f8d8ff",
    "00fcfcff",
    "d8d8d8ff",#56
    "0"
    ]

SAFETY_CHECK = 500

palette_nes_color = []
for k in PALETTE_NES:
    if k == "0":
        palette_nes_color.append((0, 0, 0, 0))
    else:
        palette_nes_color.append(tuple(int(k[i:i+2], 16) for i in (4, 2, 0, 6)))

def convert_one_img(img_path):
    img = cv.imread(img_path, cv.IMREAD_UNCHANGED)
    global img_name
    img_name = os.path.basename(img_path).split('.')[0]
    print(img_name)

    global w, h
    w = img.shape[0]
    h = img.shape[1]
    print("w=%d, h=%d"%(w,h))
    # w = 74
    # h = 60
    mat_size = (w, h)
    global mat_mask
    mat_mask = np.zeros(mat_size)
    img_colors = list()

    for i in range(0,w-1):
        for j in range(0,h-1):
            px = img[i, j]
            if px[3] >= 128:
                px_hex = "%02x%02x%02x%02x" %(px[2], px[1], px[0], px[3])
                try:
                    index_value = PALETTE_NES.index(px_hex)
                except:
                    closest_color = closest_colour(px)
                    closest_color_hex = "%02x%02x%02x%02x" %(closest_color[2], closest_color[1], closest_color[0], closest_color[3])
                    index_value = PALETTE_NES.index(closest_color_hex)
                mat_mask[i, j] = int(index_value)
                if index_value not in img_colors:
                    img_colors.append(index_value)
            else:
                mat_mask[i, j] = int(57)

    rect_list = get_bit_mask_by_color(mat_mask, img_colors)

    # file_name = 'txts/' + img_name+'.txt'
    # save_mask_mat(mat_mask, file_name)
    lua_img_name = 'Art' + img_name
    lua_file_name = 'luas/' + lua_img_name+'.lua'
    save_lua_script(rect_list, lua_file_name, lua_img_name, w, h)


def save_mask_mat(mat_mask, file_name):
    file1 = open(file_name, "w")
    print(len(mat_mask))
    for i in range(len(mat_mask)):
        file1.write("[")
        list_int = map(int, mat_mask[i])
        list_str = map(str, list_int)
        line_i = ",".join(list_str)
        file1.write(line_i)
        if i == len(mat_mask)-1:
            file1.write("]")
        else:
            file1.write("],\n")
    file1.close()


def save_lua_script(rect_list, file_name, img_name, w, h):
    file1 = open(file_name, "w")
    print(len(rect_list))
    file1.write("local _pixelArt = { -- " + img_name + "\n")
    for i in range(len(rect_list)):
        file1.write("{")
        list_int = map(int, rect_list[i])
        list_str = map(str, list_int)
        line_i = ",".join(list_str)
        file1.write(line_i)
        if i == len(rect_list)-1:
            file1.write("}\n")
        else:
            file1.write("},")
    file1.write("}\n")
    file1.write("_pixelArt._width = " + str(h) + "\n")
    file1.write("_pixelArt._height  = " + str(w) + "\n")
    file1.write("return _pixelArt")
    file1.close()


def closest_colour(selected_colour):
    # set the distance to be a reallly big number
    # initialise closest_colour to empty
    shortest_distance, closest_colour = sys.maxsize, None

    # iterate through all the colours
    # for each colour in the list, find the Euclidean distance to the one selected by the user
    global palette_nes_color
    for colour in palette_nes_color:
        # since your colours are in 3D space, perform the calculation in each respective space
        current_distance = math.sqrt(pow(colour[0] - selected_colour[0], 2) + pow(colour[1] - selected_colour[1], 2) + pow(colour[2] - selected_colour[2], 2))

        # unless you truly care about the exact length, then you don't need to perform the sqrt() operation.
        # it is a rather expensive one so you can just do this instead
        # current_distance = pow(colour.H - selected_colour.H, 2) + pow(colour.S - selected_colour.S, 2) + pow(colour.V - selected_colour.V, 2)

        # update the distance along with the corresponding colour
        if current_distance < shortest_distance:
            shortest_distance = current_distance
            closest_colour = colour

    return closest_colour


def get_bit_mask_by_color(mat_mask, img_colors):
    rect_list = list()
    for color in img_colors:
        color_mask = np.zeros((len(mat_mask), len(mat_mask[0])))
        color_mask.astype(int)
        for i in range(len(mat_mask)):
            for j in range(len(mat_mask[i])):
                if mat_mask[i][j] == color:
                    color_mask[i][j] = 1
        # print(color_mask)
        safety_check = 0
        while any(1 in x for x in color_mask):
            safety_check += 1
            if safety_check > SAFETY_CHECK:
                print("maybe dead lock")
                break

            index_left_top, w, h = maximal_rectangle(color_mask)
            # print("index left: {0}, w={1}, h={2}".format(str(index_left_top), str(w), str(h)))
            for i in range(index_left_top[1], index_left_top[1]+h):
                for j in range(index_left_top[0], index_left_top[0]+w):
                    color_mask[i][j] = 0
            # print(color_mask)
            

            rect_list.append([color, index_left_top[0], index_left_top[1], w, h])
    # print(rect_list)
    return rect_list


def maximal_rectangle(color_mask) -> int:
    if not color_mask.any():return 0
    m,n=len(color_mask),len(color_mask[0])
    # record the number of '1' above it
    pre=[0]*(n+1)
    res=0
    w = 0
    h = 0
    for i in range(m):
        for j in range(n):
            # record the number of '1' above it
            pre[j]=pre[j]+1 if color_mask[i][j]==1 else 0

        # stack
        stack=[-1]
        for k,num in enumerate(pre):
            while stack and pre[stack[-1]]>num:
                index=stack.pop()
                tmp_area = pre[index]*(k-stack[-1]-1)
                if tmp_area > res:
                    res = tmp_area
                    w = k-stack[-1]-1
                    h = pre[index]
                    # index_right_bottom = [i, j]
                    index_left_top = [k-w, i-h+1]
            stack.append(k)
        # print(pre)

    return index_left_top, w, h


for root, dirs, files in os.walk("indexed", topdown=False):
   for name in files:
    if name.endswith('.png'):
        convert_one_img(os.path.join(root, name))
        break

