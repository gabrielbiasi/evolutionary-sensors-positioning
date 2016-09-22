#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Universidade Federal de Minas Gerais
Departamento de Ciência da Computação
Programa de Pós-Graduação em Ciência da Computação

Feito por Gabriel de Biasi, 2016672212.
"""
import os, sys, re
import matplotlib.pyplot as plt

def line_to_list(string):
    return [float(x) for x in re.findall(r'[+-]?\d+', string)]

def on_key(event):
    if event.key == 'escape':
        exit()

if __name__ == '__main__':

    # Teste de parâmetro.
    if len(sys.argv) != 2:
        print 'fail'
        exit()

    figura = plt.figure()

    s_x = []
    s_y = []
    r_x = []
    r_y = []
    p = []
    GRID = 999

    with open(sys.argv[1], 'r') as handle:
        for line in handle:
            qq = line_to_list(line)
            if qq[0] == -999:
                GRID = int(qq[1])
            else:
                s_x.append(int(qq[0]))
                s_y.append(int(qq[1]))
                r_x.append(int(qq[2]))
                r_y.append(int(qq[3]))
                p.append(int(qq[4]))

    figura.canvas.set_window_title(u'Redes sem Fio')
    figura.canvas.mpl_connect('key_press_event', on_key)

    plt.subplot(111)
    # Lines
    for i in range(len(s_x)):
        plt.plot([s_x[i],r_x[i]], [s_y[i],r_y[i]], 'k--')

    # Points
    y = 0
    for i,j in zip(s_x, s_y):
        plt.plot(i, j, 'r^', markersize=10)
        plt.gca().annotate('%.1fdBm' % p[y], xy=(i, j), xycoords='data', xytext=(-15, -20), textcoords='offset points')
        y += 1

    for i,j in zip(r_x, r_y):
        plt.plot(i, j, 'go', markersize=10)


    plt.ylim(-GRID*1.2, GRID*1.2)
    plt.xlim(-GRID*1.2, GRID*1.2)

    plt.grid(False)
    plt.draw()

    plt.show()



