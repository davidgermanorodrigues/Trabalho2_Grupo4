#!/usr/bin/python3

import numpy as np
import argparse
import cv2
import copy
import json

# Global variables
window_name = 'original'
file_name = 'limits.json'
global image_gray
slider_max = 255
trackbar_pos = 0


def onTrackbar():
    pass


def main():

    # initial setup
    capture = cv2.VideoCapture(0)

    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)

    #Dicionário com as ranges
    ranges = {'b':{'min': 0, 'max': 40},
              'g': {'min': 50, 'max': 256},
              'r': {'min': 0, 'max': 40}}

    #Criação das trackbars
    cv2.createTrackbar('trackbar_min_r', window_name, 0, slider_max, onTrackbar)
    cv2.createTrackbar('trackbar_min_g', window_name, 0, slider_max, onTrackbar)
    cv2.createTrackbar('trackbar_min_b', window_name, 0, slider_max, onTrackbar)
    cv2.createTrackbar('trackbar_max_r', window_name, 0, slider_max, onTrackbar)
    cv2.createTrackbar('trackbar_max_g', window_name, 0, slider_max, onTrackbar)
    cv2.createTrackbar('trackbar_max_b', window_name, 0, slider_max, onTrackbar)

    while True:

        _, image = capture.read()  # get an image from the camera

        height,width,_, = image.shape       # get dimensions of the image

        image_gui = copy.deepcopy(image)

        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        #Vai buscar o valor da trackbar na imagem 'original'
        ranges['b']['min'] = cv2.getTrackbarPos('trackbar_min_b', window_name)
        ranges['g']['min'] = cv2.getTrackbarPos('trackbar_min_g', window_name)
        ranges['r']['min'] = cv2.getTrackbarPos('trackbar_min_r', window_name)
        ranges['b']['max'] = cv2.getTrackbarPos('trackbar_max_b', window_name)
        ranges['g']['max'] = cv2.getTrackbarPos('trackbar_max_g', window_name)
        ranges['r']['max'] = cv2.getTrackbarPos('trackbar_max_r', window_name)

        #Arruma tudo em numpy arrays
        mins = np.array([ranges['b']['min'], ranges['g']['min'], ranges['r']['min']])
        maxs = np.array([ranges['b']['max'], ranges['g']['max'], ranges['r']['max']])

        # Faz a máscara
        mask = cv2.inRange(image_gui, mins, maxs)

        # Mostra a imagem
        cv2.imshow(window_name, image)
        cv2.imshow('mask', mask)

        key = cv2.waitKey(5)

        if key == ord('q'):  # q for quit:

            data = {'limits': {'B': {'max': ranges['b']['max'], 'min': ranges['b']['min']},
                               'G': {'max': ranges['g']['max'], 'min': ranges['g']['min']},
                               'R': {'max': ranges['r']['max'], 'min': ranges['r']['min']}, }}

            with open(file_name, 'w') as file_handle:
                print('writing dictionary data to file ' + file_name)
                json.dump(data, file_handle)
            print('You pressed q, aborting.')
            break

    cv2.destroyAllWindows()
if __name__ == '__main__':
    main()