#!/usr/bin/python3

import copy
import json
import pprint

import cv2
import numpy as np

# Global variables
window_name = 'original'
window_control = 'controls'
file_name = 'limits.json'
flag_save = 0

def instruction(h, w):
    global image
    # Text
    int_text = ['Instructions:', 'Mouse L-Button: Select color', 'Mouse R-Button: Reverse Selection',
                'Key C: Clear Selection',
                'Key W: Write on limits.json file', 'Key Q: Quit']

    # font
    font = cv2.FONT_HERSHEY_DUPLEX
    # org
    org = (0, 30)

    # fontScale
    fontScale = 1

    # Black color in BGR
    color = (0, 0, 0)

    # Line thickness of 2 px
    thickness = 1

    for i in range(len(int_text)):
        image = cv2.putText(image, int_text[i], org, font, fontScale, color, thickness, cv2.LINE_AA)
        lst = list(org)
        lst[1] = lst[1] + 30
        org = tuple(lst)

def onTrackbar(threshold):
    pass


def mouseRGB(event, x, y, flags, param):  # Funcionalidade Eye Dropper
    # Global variables
    global image, data, flag_save
    global b_min, g_min, r_min, b_max, g_max, r_max
    global colorsB, colorsG, colorsR

    if event == cv2.EVENT_LBUTTONDOWN:
        colors = image[y, x]
        green_mask = [0, 255, 0]
        if (colors != green_mask).all():
            colorsB.append(image[y, x, 0])
            colorsG.append(image[y, x, 1])
            colorsR.append(image[y, x, 2])

        # print("Red: ", image[y, x, 0])
        # print("Green: ", image[y, x, 1])
        # print("Blue: ", image[y, x, 2])
        # print("BRG Format: ", colors)

        # Escolhe os valores minimos e maximos na trackbar
        b_min = cv2.setTrackbarPos('trackbar_min_b', window_control, min(colorsB))
        g_min = cv2.setTrackbarPos('trackbar_min_g', window_control, min(colorsG))
        r_min = cv2.setTrackbarPos('trackbar_min_r', window_control, min(colorsR))
        b_max = cv2.setTrackbarPos('trackbar_max_b', window_control, max(colorsB))
        g_max = cv2.setTrackbarPos('trackbar_max_g', window_control, max(colorsG))
        r_max = cv2.setTrackbarPos('trackbar_max_r', window_control, max(colorsR))
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
        if len(colorsB) > 1:
            colorsB.pop()
            colorsG.pop()
            colorsR.pop()
            b_min = cv2.setTrackbarPos('trackbar_min_b', window_control, min(colorsB))
            g_min = cv2.setTrackbarPos('trackbar_min_g', window_control, min(colorsG))
            r_min = cv2.setTrackbarPos('trackbar_min_r', window_control, min(colorsR))
            b_max = cv2.setTrackbarPos('trackbar_max_b', window_control, max(colorsB))
            g_max = cv2.setTrackbarPos('trackbar_max_g', window_control, max(colorsG))
            r_max = cv2.setTrackbarPos('trackbar_max_r', window_control, max(colorsR))
        else:
            colorsB = []
            colorsG = []
            colorsR = []
            b_min = cv2.setTrackbarPos('trackbar_min_b', window_control, 0)
            g_min = cv2.setTrackbarPos('trackbar_min_g', window_control, 0)
            r_min = cv2.setTrackbarPos('trackbar_min_r', window_control, 0)
            b_max = cv2.setTrackbarPos('trackbar_max_b', window_control, 0)
            g_max = cv2.setTrackbarPos('trackbar_max_g', window_control, 0)
            r_max = cv2.setTrackbarPos('trackbar_max_r', window_control, 0)

        # Escolhe os valores minimos e maximos na trackbar



def main():
    # Global variables
    global image, data, flag_save
    global b_min, g_min, r_min, b_max, g_max, r_max
    global colorsB, colorsG, colorsR
    colorsB = []
    colorsG = []
    colorsR = []

    # initial setup
    slider_max = 255
    b_min = 0
    g_min = 0
    r_min = 0
    b_max = 0
    g_max = 0
    r_max = 0

    capture = cv2.VideoCapture(0)

    # Criação das janelas
    cv2.namedWindow(window_control, cv2.WINDOW_AUTOSIZE)
    mat = np.zeros((10,1000), dtype=np.uint8)
    cv2.imshow(window_control, mat)
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback(window_name, mouseRGB)

    # Criação das trackbars
    cv2.createTrackbar('trackbar_min_r', window_control, r_min, slider_max, onTrackbar)
    cv2.createTrackbar('trackbar_min_g', window_control, g_min, slider_max, onTrackbar)
    cv2.createTrackbar('trackbar_min_b', window_control, b_min, slider_max, onTrackbar)
    cv2.createTrackbar('trackbar_max_r', window_control, r_max, slider_max, onTrackbar)
    cv2.createTrackbar('trackbar_max_g', window_control, g_max, slider_max, onTrackbar)
    cv2.createTrackbar('trackbar_max_b', window_control, b_max, slider_max, onTrackbar)

    while True:

        _, image = capture.read()  # get an image from the camera
        image = cv2.flip(image, 1)  # Espelhar a imagem da webcam.
        height, width, _, = image.shape  # get dimensions of the image

        image_gui = copy.deepcopy(image)

        # Vai buscar o valor da trackbar na imagem 'original'
        b_min = cv2.getTrackbarPos('trackbar_min_b', window_control)
        g_min = cv2.getTrackbarPos('trackbar_min_g', window_control)
        r_min = cv2.getTrackbarPos('trackbar_min_r', window_control)
        b_max = cv2.getTrackbarPos('trackbar_max_b', window_control)
        g_max = cv2.getTrackbarPos('trackbar_max_g', window_control)
        r_max = cv2.getTrackbarPos('trackbar_max_r', window_control)

        # Dicionário com as ranges
        ranges = {'b': {'min': b_min, 'max': b_max},
                  'g': {'min': g_min, 'max': g_max},
                  'r': {'min': r_min, 'max': r_max}}

        # Arruma tudo em numpy arrays
        mins = np.array([ranges['b']['min'], ranges['g']['min'], ranges['r']['min']])
        maxs = np.array([ranges['b']['max'], ranges['g']['max'], ranges['r']['max']])

        # Faz a máscara
        image_processed = cv2.inRange(image_gui, mins, maxs)
        # Desenhar a verde na imagem original.
        mask = image_processed.astype(
            np.bool)  # Converter a mask_largest em bool para puder usá-la como 'filtro' na imagem original.
        image[mask] = (0, 255, 0)  # Pintar zonas escolhidas de verde

        try:
            M = cv2.moments(image_processed)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            dim_cross = 5
            cv2.line(image, pt1=(cX - dim_cross, cY - dim_cross), pt2=(cX + dim_cross, cY + dim_cross),
                     color=(0, 0, 255), thickness=2)
            cv2.line(image, pt1=(cX - dim_cross, cY + dim_cross), pt2=(cX + dim_cross, cY - dim_cross),
                     color=(0, 0, 255), thickness=2)
        except:
            pass

        instruction(height, width)

        # Mostra a imagem
        cv2.imshow(window_name, image)

        key = cv2.waitKey(1)

        if key == ord('w'):  # guarda os valores das trackbars no ficheiro limits.json na mesma pasta do programa

            data = {'limits': {'B': {'max': ranges['b']['max'], 'min': ranges['b']['min']},
                               'G': {'max': ranges['g']['max'], 'min': ranges['g']['min']},
                               'R': {'max': ranges['r']['max'], 'min': ranges['r']['min']}, }}

            with open(file_name, 'w') as file_handle:
                print('You pressed w, writing color limits to file ' + file_name)
                json.dump(data, file_handle)

                pp = pprint.PrettyPrinter(indent=1)  # Set the dictionary initial indentation.
                pp.pprint(data)  # Print with pretty print

                file_handle.close()
                flag_save = 1

        if key == ord('c'):
            colorsB = []
            colorsG = []
            colorsR = []
            b_min = cv2.setTrackbarPos('trackbar_min_b', window_control, 0)
            g_min = cv2.setTrackbarPos('trackbar_min_g', window_control, 0)
            r_min = cv2.setTrackbarPos('trackbar_min_r', window_control, 0)
            b_max = cv2.setTrackbarPos('trackbar_max_b', window_control, 0)
            g_max = cv2.setTrackbarPos('trackbar_max_g', window_control, 0)
            r_max = cv2.setTrackbarPos('trackbar_max_r', window_control, 0)
        if key == ord('q'):  # sai do programa e não guarda
            if flag_save == 0:
                print('You pressed q, quitting without saving values.')
                break
            else:
                print('You pressed q, a limits.json file was created during session, quitting...')
                break

    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
