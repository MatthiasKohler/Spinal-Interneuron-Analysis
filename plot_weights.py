#!/usr/bin/env python3

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import scipy
from scipy.stats import kde
import seaborn as sns
import matplotlib.colors
import random as rnd
sns.set_style("white")


def plot_2d_contour(ax, x, y, x_label, y_label):
    x = np.abs(x)
    y = np.abs(y)
    if x_label == 'Ia - In' and y_label == 'Ib - In':
        print(x, y)
    ax.set_aspect(1)
    
    xsign = -1 if all(x <= 0) else 1
    ysign = -1 if all(y <= 0) else 1
    ax.set_xlim([- xsign * 0.5, xsign * 11])
    ax.set_ylim([- ysign * 0.5, ysign * 11])

    #ax.set_xticks([0, 5, xsign * 10])
    #ax.set_yticks([0, 5, ysign * 10])
    ax.axhline(0, color = 'black', linewidth = 1, alpha = 0.2)
    ax.axvline(0, color = 'black', linewidth = 1, alpha = 0.2)
    ax.axhline(10, color = 'black', linewidth = 1, alpha = 0.2)
    ax.axvline(10, color = 'black', linewidth = 1, alpha = 0.2)
    ax.set_yticklabels([])
    ax.set_xticklabels([])


    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["white", "red"])

    sns.kdeplot(x, y, cmap = cmap, shade = True, shade_lowest = False, ax = ax)

    min_rnd = -0.5
    max_rnd = 0.5
    #dist = rnd.uniform(0, max_rnd)
    offset = lambda v : v if v == 0 else v + np.random.uniform(min_rnd, max_rnd)
    for a, b in zip(x,y):
        ax.scatter(offset(a), offset(b), s = 3, color = 'C0')

    sns.despine()
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    #Set axis labels after plotting, otherwise kdeplot will overwrite them.
    ax.set_xlabel(x_label, labelpad = -6, fontsize = 9)
    ax.set_ylabel(y_label, labelpad = -6, fontsize = 9)

def plot_all_2d_contour(data, output):
    plt.gcf().subplots_adjust(bottom=0.30)
    plt.gcf().subplots_adjust(left=0.25)

    xy = [('Ia1',  'Ia-2',  'Ia - Ex', 'Ia - In'),
      ('Ib1',  'Ib-2',  'Ib - Ex', 'Ib - In'),
      ('Ia1',  'Ib1',   'Ia - Ex', 'Ib - Ex'),
      ('Ia-2', 'Ib-2',  'Ia - In', 'Ib - In'),
      ('Ia1',  'Skin1', 'Ia - Ex', 'Skin - Ex'),
      ('Ib1',  'Skin1', 'Ib - Ex', 'Skin - Ex')]
      #('Skin1', 'Skin-2', 'Skin - Ex', 'Skin - In')]


    for x, y, x_label, y_label in xy:
        fig, ax = plt.subplots()
        fig.set_figheight(1.7)
        fig.set_figwidth(1.7) 

        plot_2d_contour(ax, data[x] / 10, data[y] / 10, x_label, y_label)
        
        fig.tight_layout()
        fig.savefig(output + x + '_' + y + '.png', dpi = 300, transparent = True)


def plot_weight_distribution(data, output):
    weights_In = []
    weights_Ex = []
    inputs = ['Skin', 'Ia', 'Ib']

    for c in data.columns:
        if not any(map(lambda i: i in c, inputs)):
            continue
        for index, row in data.iterrows():
            w = row[c] / 10
            if w < 0:
                weights_In.append(w)
            elif w > 0:
                weights_Ex.append(w)

    bw = 0.5
    
    fig = plt.figure(figsize=(3,3),dpi=300)
    ax = fig.add_subplot(111)
    
    sns.kdeplot(weights_Ex, ax = ax, shade=False, color="black",   bw = bw, clip = (0.0, 10.0))
    sns.kdeplot(weights_In, ax = ax, shade=False, color="red", bw = bw, clip = (-10.0, 0.0))
    
    min_rnd = 0.0
    max_rnd = 0.1
    for w in weights_In:
        ax.scatter(w + np.random.uniform(-0.5, 0.5), np.random.uniform(min_rnd, max_rnd), s = 2, color = "red") 
    for w in weights_Ex:
        ax.scatter(w + np.random.uniform(-0.5, 0.5), np.random.uniform(min_rnd, max_rnd), s = 2, color = "black") 

    
    sns.despine()
    ax.set_xlabel('Weight [mV]')
    ax.set_ylabel('Density')
    fig.set_figheight(1.5)
    fig.set_figwidth(3)
    fig.tight_layout()
    fig.savefig(output + 'Weight_Distribution.png', dpi = 300, bbox_inches='tight', transparent = True) 

    print("Number of ex weights", len(weights_Ex))
    print("Number of in weights", len(weights_In))

def plot_depths(data, output):
    data = pd.read_csv("./data_synaptology/Synaptology_tidy.csv", encoding = 'utf8')
    fig, ax = plt.subplots()
    fig.set_figheight(6)
    fig.set_figwidth(0.2) 
    plt.gcf().subplots_adjust(bottom=0.30)
    plt.gcf().subplots_adjust(left=0.25)
   
    ax.set_ylim([4.5, 0.6])
    ax.set_xlim([-0.6, 0.6])

    #ax.set_yticklabels([])
    ax.set_xticklabels([])

    ax.spines['bottom'].set_visible(False)
    #ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)


    depths = list(data['Depth'])
    depths.sort()
    print(depths)

    ticks = [0.6, min(depths), 3.31, max(depths), max(depths) + 0.2]
    ax.set_yticks(ticks)
    ax.set_yticklabels([str(x) for x in ticks][0: -1], fontsize = 9)
    
    min_rnd = -0.5
    max_rnd = 0.5
    offset = lambda v : v if v == 0 else v + np.random.uniform(min_rnd, max_rnd)
    offsets =  [np.random.uniform(min_rnd, max_rnd) for x in depths]

    ax.scatter(offsets, depths, s = 1)
    fig.savefig(output + 'Depths.png', dpi = 300, bbox_inches='tight', transparent = True) 
    

def main():
    #dataFile = "../TidyData/tidyDataWeighted.csv"
    data = pd.read_csv("./data_synaptology/Synaptology_HQ_tidy.csv", encoding = 'utf8')
    output = "./plots_weights/"

    plot_weight_distribution(data, output)
    plot_all_2d_contour(data,output)
    plot_depths(data, output)


if __name__ == "__main__":
    main()
