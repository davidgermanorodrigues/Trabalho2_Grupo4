#!/usr/bin/python3

import numpy as np
import argparse
import cv2
import copy
import json

# Global variables
window_original = 'original'
window_mask = 'canvas'
window_segmentation = 'Segmentation'
global count

def main():

    # Leitura dos argumentos da linha de comandos
    parser = argparse.ArgumentParser(description='Definitions of test mode')
    parser.add_argument('-j', '--json', type=str, help='Full path to json file.')
    global args
    args = vars(parser.parse_args())

    # Leitura do ficheiro json com os limites para segmentação de cor
    with open(args.get('json')) as json_file:
        data = json.load(json_file)         #Carrega o ficheiro json para a variável data
        # print(data)
        # print(data['limits']['B']['max'])

        # #Vai buscar o valor da trackbar na imagem 'original'
        b_min = data['limits']['B']['min']
        g_min = data['limits']['G']['min']
        r_min = data['limits']['R']['min']
        b_max = data['limits']['B']['max']
        g_max = data['limits']['G']['max']
        r_max = data['limits']['R']['max']

        json_file.close()                           # Closing file

    ranges = {'b': {'min': b_min, 'max': b_max},        #Guarda os valores importados num dicionário chamado ranges
              'g': {'min': g_min, 'max': g_max},
              'r': {'min': r_min, 'max': r_max}}
    # print(ranges)

    # Setup inicial da captura de video
    capture = cv2.VideoCapture(0)

    cv2.namedWindow(window_original, cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow(window_segmentation, cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow(window_mask, cv2.WINDOW_AUTOSIZE)

    # Arrays para guardar coordenadas dos centróides
    center_X = []
    center_Y = []
    count = 0

    while True:

        _, image = capture.read()           # get an image from the camera
        height, width, _, = image.shape       # get dimensions of the image

        image_gui = copy.deepcopy(image)

        # Criação da máscara branca
        mask = np.ndarray(shape=(height, width), dtype=np.uint8)
        mask.fill(255)      #Totalmente branca

        # Criação da imagem processada
        mins = np.array([ranges['b']['min'], ranges['g']['min'], ranges['r']['min']])
        max = np.array([ranges['b']['max'], ranges['g']['max'], ranges['r']['max']])
        image_processed = cv2.inRange(image, mins, max)


        # Criação da máscara para isolar o objeto maior
        mask_largest = np.ndarray(shape=(height, width), dtype=np.uint8)
        mask_largest.fill(0)        #Totalmente preta


        if np.mean(image_processed) > 0:        # Verifica se existem objetos (>0)

            count += 1

            contours, hierarchy = cv2.findContours(image_processed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)
            largest_item = sorted_contours[0]                                                   # Vai buscar o objeto maior
            cv2.fillPoly(mask_largest, pts=[largest_item], color=(255, 255, 255))                # Faz o fill do objeto maior

            # Calcula as coordenadas do centróide e assinala-o
            M = cv2.moments(mask_largest)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            # cv2.circle(image, (cX, cY), 5, (0, 0, 255), 2)

            # Desenhar a verde na imagem original
            mask_largest = mask_largest.astype(np.bool)  # Temos de converter a mask_largest em bool para puder usá-la como 'filtro' na imagem original
            image[mask_largest] = (0, 255, 0)  # Pintamos de verde na imagem original

            # Desenha uma cruz vermelha no centróide
            dim_cross = 5
            cv2.line(image, (cX-dim_cross, cY-dim_cross), (cX+dim_cross, cY+dim_cross), (0, 0, 255), 2)
            cv2.line(image, (cX-dim_cross, cY+dim_cross), (cX+dim_cross, cY-dim_cross), (0, 0, 255), 2)

            #Desenha a linha na máscara branca
            center_X.append(cX)
            center_Y.append(cY)

            for i in center_X:
                print('Cx = ' + str(i))
            for i in center_Y:
                print('Cy = ' + str(i))


            # print(len(center_X))
            # print(center_X)
            # print(center_Y)

            # Verifica se existem argumentos suficientes nos arrays dos centróides para desenhar as linhas
            if len(center_X) >= 3:
                cv2.line(mask, (center_X[count-2], center_Y[count-2]), (center_X[count-1], center_Y[count-1]), (0, 0, 255), 2)

        key = cv2.waitKey(5)

        #Sai do programa
        if key == ord('q'):
            print('You pressed q, quitting.')
            break


        cv2.imshow(window_original, image)  # Mostra a imagem de video da webcam
        cv2.imshow(window_mask, mask)  # Mostra a imagem de video da webcam
        cv2.imshow(window_segmentation, image_processed)  # Mostra a janela com o video segmentado
        cv2.imshow('mask_largest', mask_largest.astype(np.uint8)*255)  # Mostra a imagem de video da webcam, temos de a converter de volta a unit8

    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()