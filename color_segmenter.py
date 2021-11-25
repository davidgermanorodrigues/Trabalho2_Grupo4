#!/usr/bin/python3

import numpy as np
import argparse
import cv2
import copy
import json
import pprint

def onTrackbar(threshold):
    pass

def main():
    # Global variables
    window_name = 'original'
    file_name = 'limits.json'
    global image_gray
    global image, data
    global b_min, g_min, r_min, b_max, g_max, r_max
    global colorsB, colorsG, colorsR
    colorsB = []
    colorsG = []
    colorsR = []

    # Funcionalidade Eye Dropper
    def mouseRGB(event, x, y, flags, param):
        # Global variables
        global image, data
        global b_min, g_min, r_min, b_max, g_max, r_max
        global colorsB, colorsG, colorsR


        if event == cv2.EVENT_LBUTTONDOWN:
            colorsB.append(image[y, x, 0])
            colorsG.append(image[y, x, 1])
            colorsR.append(image[y, x, 2])
            colors = image[y, x]
            print("Red: ", image[y, x, 0])
            print("Green: ", image[y, x, 1])
            print("Blue: ", image[y, x, 2])
            print("BRG Format: ", colors)

            # Escolhe os valores minimos e maximos na trackbar
            b_min = cv2.setTrackbarPos('trackbar_min_b', window_name, min(colorsB))
            g_min = cv2.setTrackbarPos('trackbar_min_g', window_name, min(colorsG))
            r_min = cv2.setTrackbarPos('trackbar_min_r', window_name, min(colorsR))
            b_max = cv2.setTrackbarPos('trackbar_max_b', window_name, max(colorsB))
            g_max = cv2.setTrackbarPos('trackbar_max_g', window_name, max(colorsG))
            r_max = cv2.setTrackbarPos('trackbar_max_r', window_name, max(colorsR))
            # data = {'limits': {'B': {'max': int(colorsB + 30), 'min': int(colorsB - 30)},
            #                    'G': {'max': int(colorsG + 30), 'min': int(colorsG - 30)},
            #                    'R': {'max': int(colorsR + 30), 'min': int(colorsB - 30)}, }}
            #
            # with open(file_name, 'w') as file_handle:
            #     print('You pressed left mouse button, writing color limits to file ' + file_name)
            #     json.dump(data, file_handle)
            #
            #     pp = pprint.PrettyPrinter(indent=1)      # Set the dictionary initial indentation.
            #     pp.pprint(data)                          # Print with pretty print
            #     file_handle.close()

        # Reset da Função
        if event == cv2.EVENT_RBUTTONDOWN:
            colorsB = []
            colorsG = []
            colorsR = []
            b_min = cv2.setTrackbarPos('trackbar_min_b', window_name, 0)
            g_min = cv2.setTrackbarPos('trackbar_min_g', window_name, 0)
            r_min = cv2.setTrackbarPos('trackbar_min_r', window_name, 0)
            b_max = cv2.setTrackbarPos('trackbar_max_b', window_name, 0)
            g_max = cv2.setTrackbarPos('trackbar_max_g', window_name, 0)
            r_max = cv2.setTrackbarPos('trackbar_max_r', window_name, 0)

    # initial setup
    slider_max = 255
    b_min = 0
    g_min = 0
    r_min = 0
    b_max = 0
    g_max = 0
    r_max = 0

    capture = cv2.VideoCapture(0)


    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback(window_name,mouseRGB)

    #Criação das trackbars
    cv2.createTrackbar('trackbar_min_r', window_name, r_min, slider_max, onTrackbar)
    cv2.createTrackbar('trackbar_min_g', window_name, g_min, slider_max, onTrackbar)
    cv2.createTrackbar('trackbar_min_b', window_name, b_min, slider_max, onTrackbar)
    cv2.createTrackbar('trackbar_max_r', window_name, r_max, slider_max, onTrackbar)
    cv2.createTrackbar('trackbar_max_g', window_name, g_max, slider_max, onTrackbar)
    cv2.createTrackbar('trackbar_max_b', window_name, b_max, slider_max, onTrackbar)


    while True:

        _, image = capture.read()  # get an image from the camera

        height,width,_, = image.shape       # get dimensions of the image

        image_gui = copy.deepcopy(image)

        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        #Vai buscar o valor da trackbar na imagem 'original'
        b_min = cv2.getTrackbarPos('trackbar_min_b', window_name)
        g_min = cv2.getTrackbarPos('trackbar_min_g', window_name)
        r_min = cv2.getTrackbarPos('trackbar_min_r', window_name)
        b_max = cv2.getTrackbarPos('trackbar_max_b', window_name)
        g_max = cv2.getTrackbarPos('trackbar_max_g', window_name)
        r_max = cv2.getTrackbarPos('trackbar_max_r', window_name)

        # Dicionário com as ranges
        ranges = {'b': {'min': b_min, 'max': b_max},
                  'g': {'min': g_min, 'max': g_max},
                  'r': {'min': r_min, 'max': r_max}}

        # Arruma tudo em numpy arrays
        mins = np.array([ranges['b']['min'], ranges['g']['min'], ranges['r']['min']])
        maxs = np.array([ranges['b']['max'], ranges['g']['max'], ranges['r']['max']])

        # Faz a máscara
        image_processed = cv2.inRange(image_gui, mins, maxs)

        # Mostra a imagem
        cv2.imshow(window_name, image)
        cv2.imshow('mask', image_processed)

        key = cv2.waitKey(1)

        if key == ord('w'):  # guarda os valores das trackbars no ficheiro limits.json na mesma pasta do programa

            data = {'limits': {'B': {'max': ranges['b']['max'], 'min': ranges['b']['min']},
                               'G': {'max': ranges['g']['max'], 'min': ranges['g']['min']},
                               'R': {'max': ranges['r']['max'], 'min': ranges['r']['min']}, }}

            with open(file_name, 'w') as file_handle:
                print('You pressed w, writing color limits to file ' + file_name)
                json.dump(data, file_handle)

                pp = pprint.PrettyPrinter(indent=1)      # Set the dictionary initial indentation.
                pp.pprint(data)                          # Print with pretty print

                file_handle.close()

        if key == ord('q'):  # sai do programa e não guarda
            print('You pressed q, quitting without saving values.')
            break

    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
