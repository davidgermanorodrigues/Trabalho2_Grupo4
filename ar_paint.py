#!/usr/bin/python3

import numpy as np
import argparse
import cv2
import copy
import json
import time
import math

# Variáveis globais.
window_original = 'Original'
window_gui = 'GUI'
window_mask = 'Canvas'
window_segmentation = 'Segmentation'


def shake_prevention_dist(x, y, c, mask, color, thickness):
    pt1_X = x[0]
    pt1_Y = y[0]
    pt2_X = x[1]
    pt2_Y = y[1]

    D = math.sqrt((pt2_X - pt1_X)**2 + (pt2_Y - pt1_Y)**2)

    # print(D)
    if 3 < D < 50:
        cv2.line(mask, pt1=(pt1_X, pt1_Y), pt2=(pt2_X, pt2_Y), color=color, thickness=thickness)
        del x[0]
        del y[0]
        c -= 1
        return x, y, c
    else:
        del x[0:]
        del y[0:]
        c -= 2
        return x, y, c


def shake_prevention_3pts(x, y, c, mask, color, thickness):
    pt1_X = x[0]
    pt1_Y = y[0]
    pt2_X = x[1]
    pt2_Y = y[1]
    pt3_X = x[2]
    pt3_Y = y[2]

    d12 = math.sqrt((pt2_X - pt1_X)**2 + (pt2_Y - pt1_Y)**2)
    d13 = math.sqrt((pt3_X - pt1_X)**2 + (pt3_Y - pt1_Y)**2)
    d23 = math.sqrt((pt3_X - pt2_X)**2 + (pt3_Y - pt2_Y)**2)

    d = [d12, d13, d23]
    # print(D)
    if d[0] > 5 and d[1] > 5:
        if (d[0] - d[1] < 10 and d[2] < 20 and d[0] > d[1]) or (d[0] - d[1] < 10 and 20 < d[2] < 30 and d[0] > d[1]) or (d[0] > d[1] and d[1] < 30):
            cv2.line(mask, pt1=(pt1_X, pt1_Y), pt2=(pt3_X, pt3_Y), color=color, thickness=thickness)
            del x[0:1]
            del y[0:1]
            c -= 2
            return x, y, c
        elif (d[0] - d[1] < 10 and d[2] < 20 and d[0] < d[1]) or (d[0] - d[1] < 10 and 20 < d[2] < 30 and d[0] < d[1]) or (d[0] < d[1] and d[0] < 30):
            cv2.line(mask, pt1=(pt1_X, pt1_Y), pt2=(pt2_X, pt2_Y), color=color, thickness=thickness)
            del x[2]
            del x[0]
            del y[2]
            del y[0]
            c -= 2
            return x, y, c
        elif d[0] > 30 and 30 < d[1] < d[0] < 50:
            cv2.line(mask, pt1=(pt1_X, pt1_Y), pt2=(pt2_X, pt2_Y), color=color, thickness=thickness)
            del x[2]
            del x[0]
            del y[2]
            del y[0]
            c -= 2
            return x, y, c
        elif d[1] > 30 and 30 < d[0] < d[1] < 50:
            cv2.line(mask, pt1=(pt1_X, pt1_Y), pt2=(pt3_X, pt3_Y), color=color, thickness=thickness)
            del x[0:1]
            del y[0:1]
            c -= 2
            return x, y, c
        else:
            del x[0:]
            del y[0:]
            c -= 3
            return x, y, c
    else:
        del x[0:]
        del y[0:]
        c -= 3
        return x, y, c


def main():

    # Leitura dos argumentos da linha de comandos.
    parser = argparse.ArgumentParser(description='Definitions of test mode')
    parser.add_argument('-j', '--json', type=str, required=True, help='Full path to json file.',)
    parser.add_argument('-sh1', '--shake1', action='store_true', help='use_shake_detection option 1')
    parser.add_argument('-sh2', '--shake2', action='store_true', help='use_shake_detection option 2')
    args = vars(parser.parse_args())

    # Leitura do ficheiro json com os limites para segmentação de cor.
    with open(args.get('json')) as json_file:
        data = json.load(json_file)                     # Carrega o ficheiro json para a variável "data".

        # Vai buscar o valor da trackbar na imagem "original".
        b_min = data['limits']['B']['min']
        g_min = data['limits']['G']['min']
        r_min = data['limits']['R']['min']
        b_max = data['limits']['B']['max']
        g_max = data['limits']['G']['max']
        r_max = data['limits']['R']['max']

        json_file.close()                               # Fechar o ficheiro.

    ranges = {'b': {'min': b_min, 'max': b_max},        # Guarda os valores importados num dicionário chamado "ranges".
              'g': {'min': g_min, 'max': g_max},
              'r': {'min': r_min, 'max': r_max}}

    # Setup inicial da captura de video.
    capture = cv2.VideoCapture(0)

    cv2.namedWindow(window_original, cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow(window_gui, cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow(window_segmentation, cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow(window_mask, cv2.WINDOW_AUTOSIZE)

    # Arrays para guardar coordenadas dos centróides.
    center_X = []
    center_Y = []
    count = 0
    conta_rect = 0
    conta_circ = 0
    pencil_color = (0, 0, 0)
    pencil_thickness = 10
    Cx = 0
    Cy = 0

    _, image = capture.read()               # Obtém uma imagem da webcam.
    height, width, _, = image.shape         # Obtém as dimensões da imagem.
    # Criação da máscara branca.
    mask_white = np.zeros([height, width, 3], dtype=np.uint8)
    mask_white.fill(255)                    # Totalmente branca.

    flag_line = 0

    while True:
        _, image = capture.read()           # Obtém uma imagem da webcam.

        image_gui = copy.deepcopy(image)
        image = cv2.flip(image, 1)          # Espelhar a imagem da webcam.
        image_gui = cv2.flip(image_gui, 1)

        # Criação da imagem processada.
        mins = np.array([ranges['b']['min'], ranges['g']['min'], ranges['r']['min']])
        maxs = np.array([ranges['b']['max'], ranges['g']['max'], ranges['r']['max']])
        image_processed = cv2.inRange(image, mins, maxs)

        # Criação da máscara para isolar o objeto maior.
        mask_largest = np.ndarray(shape=(height, width), dtype=np.uint8)
        mask_largest.fill(0)                # Totalmente preta.

        if np.mean(image_processed) > 0:    # Verifica se existem objetos (>0).
            count += 1

            contours, hierarchy = cv2.findContours(image_processed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)
            largest_item = sorted_contours[0]                                       # Vai buscar o objeto maior.
            cv2.fillPoly(mask_largest, pts=[largest_item], color=(255, 255, 255))   # Faz o fill do objeto maior.

            # Calcula as coordenadas do centróide e assinala-o.
            M = cv2.moments(mask_largest)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])

            # Desenhar a verde na imagem original.
            mask_largest = mask_largest.astype(np.bool)     # Temos de converter a mask_largest em bool para puder usá-la como 'filtro' na imagem original.
            image[mask_largest] = (0, 255, 0)               # Pintamos de verde na imagem original.

            # Desenha uma cruz vermelha no centróide.
            dim_cross = 5
            cv2.line(image, pt1=(cX - dim_cross, cY - dim_cross), pt2=(cX + dim_cross, cY + dim_cross), color=(0, 0, 255), thickness=2)
            cv2.line(image, pt1=(cX - dim_cross, cY + dim_cross), pt2=(cX + dim_cross, cY - dim_cross), color=(0, 0, 255), thickness=2)

            # Desenha a linha na máscara branca.
            center_X.append(cX)
            center_Y.append(cY)

            if flag_line == 1:
                if args.get('shake1'):
                    print('Using use_shake_prevention_3pts.')
                    if len(center_X) >= 3 and len(center_Y) >= 3:
                        (center_X, center_Y, count) = shake_prevention_3pts(center_X, center_Y, count, mask_white, pencil_color, pencil_thickness)
                elif args.get('shake2'):
                    print('Using use_shake_prevention_dist')
                    if len(center_X) >= 2 and len(center_Y) >= 2:
                        (center_X, center_Y, count) = shake_prevention_dist(center_X, center_Y, count, mask_white, pencil_color, pencil_thickness)
                else:
                    # Verifica se existem argumentos suficientes nos arrays dos centróides para desenhar as linhas.
                    if len(center_X) >= 2:
                        cv2.line(mask_white, pt1=(center_X[count-2], center_Y[count-2]), pt2=(center_X[count-1], center_Y[count-1]), color=pencil_color, thickness=pencil_thickness)
                        if count >= 2:
                            del center_X[0]
                            del center_Y[0]
                            count -= 1

            flag_line = 1

        else:
            del center_X[0:]
            del center_Y[0:]
            c = 0
            flag_line = 0

        key = cv2.waitKey(1)

        # Pintar a preto.
        if key == ord('k'):
            pencil_color = (0, 0, 0)
            print('You pressed k, now you are painting in black.')

        # Pintar a vermelho.
        if key == ord('r'):
            pencil_color = (0, 0, 255)
            print('You pressed r, now you are painting in red.')

        # Pintar a verde.
        elif key == ord('g'):
            pencil_color = (0, 255, 0)
            print('You pressed g, now you are painting in green.')

        # Pintar a azul.
        elif key == ord('b'):
            pencil_color = (255, 0, 0)
            print('You pressed b, now you are painting in blue.')

        # Aumenta a espessura.
        elif key == ord('+'):
            pencil_thickness = pencil_thickness + 1
            print('You pressed +, now you are painting with ' + str(pencil_thickness) + ' pencil_thickness.')

        # Diminui a espessura.
        elif key == ord('-'):
            pencil_thickness = pencil_thickness - 1
            if pencil_thickness <= 1:
                pencil_thickness = 1
            print('You pressed -, now you are painting with ' + str(pencil_thickness) + ' pencil_thickness.')

        # Limpa a tela.
        elif key == ord('c'):
            mask_white.fill(255)      # Totalmente branca
            conta_rect = 0
            conta_circ = 0
            print('You pressed c, canvas is now cleared.')

        # Grava a tela.
        elif key == ord('w'):
            status = cv2.imwrite(time.strftime('drawing_%a_%b_%Y-%m-%d-%H:%M') + '.png', mask_white)
            print('You pressed w, canvas is now saved.')

        # Desenha círculos na tela (canvas).
        elif key == ord('o'):
            conta_circ += 1

            cent_atual = (center_X[len(center_X)-1] , center_Y[len(center_Y)-1])
            print(cent_atual)

            while True:
                _, image = capture.read()   # Obtém uma imagem da webcam.

                image = cv2.flip(image, 1)  # Espelhar a imagem da webcam.

                # Criação da imagem processada.
                mins = np.array([ranges['b']['min'], ranges['g']['min'], ranges['r']['min']])
                max = np.array([ranges['b']['max'], ranges['g']['max'], ranges['r']['max']])
                image_processed = cv2.inRange(image, mins, max)

                # Criação da máscara para isolar o objeto maior.
                mask_largest = np.ndarray(shape=(height, width), dtype=np.uint8)
                mask_largest.fill(0)                                                        # Totalmente preta.

                if np.mean(image_processed) > 0:                                            # Verifica se existem objetos (>0).

                    contours, hierarchy = cv2.findContours(image_processed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                    sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)
                    largest_item = sorted_contours[0]                                       # Vai buscar o objeto maior.
                    cv2.fillPoly(mask_largest, pts=[largest_item], color=(255, 255, 255))   # Faz o fill do objeto maior.

                    # Calcula as coordenadas do centróide e assinala-o.
                    M = cv2.moments(mask_largest)
                    cX1 = int(M["m10"] / M["m00"])
                    cY1 = int(M["m01"] / M["m00"])

                raio = int(math.sqrt((cent_atual[0] - cX1)**2 + (cent_atual[1] - cY1)**2))

                cv2.circle(image, (cent_atual[0], cent_atual[1]), raio, (255, 255, 0), -1)

                cv2.imshow(window_original, image)                  # Mostra a imagem de video da webcam.
                cv2.imshow(window_mask, mask_white)                 # Mostra a imagem de video da webcam.
                cv2.imshow(window_segmentation, image_processed)    # Mostra a janela com o video segmentado.

                key = cv2.waitKey(1)

                # É necessário clicar no 'o' novamente para sair da funcionalidade e gravar na tela branca (canvas).
                if key == ord('o'):
                    cv2.circle(mask_white, (cent_atual[0], cent_atual[1]), raio, (255, 255, 0), -1)
                    cv2.putText(mask_white, 'Circulo ' + str(conta_circ), (cent_atual[0]-70,cent_atual[1]), 1, cv2.FONT_HERSHEY_DUPLEX , (255, 0, 0), 2)
                    break

        # Desenha retângulos na tela (canvas).
        elif key == ord('t'):
            conta_rect += 1

            cent_atual = (center_X[len(center_X) - 1], center_Y[len(center_Y) - 1])
            print(cent_atual)

            while True:
                _, image = capture.read()   # Obtém uma imagem da webcam.

                image = cv2.flip(image, 1)  # Espelhar a imagem da webcam.

                # Criação da imagem processada.
                mins = np.array([ranges['b']['min'], ranges['g']['min'], ranges['r']['min']])
                max = np.array([ranges['b']['max'], ranges['g']['max'], ranges['r']['max']])
                image_processed = cv2.inRange(image, mins, max)

                # Criação da máscara para isolar o objeto maior.
                mask_largest = np.ndarray(shape=(height, width), dtype=np.uint8)
                mask_largest.fill(0)                                                        # Totalmente preta.

                if np.mean(image_processed) > 0:                                            # Verifica se existem objetos (>0).

                    contours, hierarchy = cv2.findContours(image_processed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                    sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)
                    largest_item = sorted_contours[0]                                       # Vai buscar o objeto maior.
                    cv2.fillPoly(mask_largest, pts=[largest_item], color=(255, 255, 255))   # Faz o fill do objeto maior.

                    # Calcula as coordenadas do centróide e assinala-o.
                    M = cv2.moments(mask_largest)
                    cX1 = int(M["m10"] / M["m00"])
                    cY1 = int(M["m01"] / M["m00"])

                cv2.rectangle(image, (cent_atual[0], cent_atual[1]), (cX1, cY1), (255, 0, 255), -1)

                cv2.imshow(window_original, image)                  # Mostra a imagem de video da webcam.
                cv2.imshow(window_mask, mask_white)                 # Mostra a imagem de video da webcam.
                cv2.imshow(window_segmentation, image_processed)    # Mostra a janela com o video segmentado.

                key = cv2.waitKey(1)

                # É necessário clicar no 't' novamente para sair da funcionalidade e gravar na tela branca (canvas).
                if key == ord('t'):
                    cv2.rectangle(mask_white, (cent_atual[0], cent_atual[1]), (cX1, cY1), (255, 0, 255), -1)
                    if conta_rect % 2 == 0:
                        cv2.putText(mask_white, 'Rectangulo ' + str(conta_rect), (cX1, cY1), 1, cv2.FONT_HERSHEY_DUPLEX , (255, 255, 0), 2)
                    else:
                        cv2.putText(mask_white, 'Rectangulo ' + str(conta_rect), (cX1, cY1-50), 1, cv2.FONT_HERSHEY_DUPLEX, (255, 255, 0), 2)
                    break

        # Sai do programa.
        elif key == ord('q'):
            print('You pressed q, quitting.')
            break

        # Desenhar as linhas no video stream.
        lower = np.array([1, 1, 1], dtype="uint8")
        upper = np.array([255, 255, 255], dtype="uint8")
        mask_gui = cv2.inRange(mask_white, lower, upper)
        mask_gui = cv2.bitwise_not(mask_gui)
        cv2.add(mask_white, (0, 0, 0, 0), dst=image_gui, mask=mask_gui)

        cv2.imshow(window_original, image)                              # Mostra a imagem de video da webcam.
        cv2.imshow(window_gui, image_gui)                               # Mostra a imagem de video da webcam.
        cv2.imshow(window_mask, mask_white)                             # Mostra a imagem de video da webcam.
        cv2.imshow(window_segmentation, image_processed)                # Mostra a janela com o video segmentado.
        cv2.imshow('mask_largest', mask_largest.astype(np.uint8)*255)   # Mostra a imagem de video da webcam, temos de a converter de volta a unit8.

    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
