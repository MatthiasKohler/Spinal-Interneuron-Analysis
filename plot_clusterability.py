#!/usr/bin/env python3

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np

import plot_style


def config_fig_ax(fig, ax, width, height):
    plot_style.hide_spines(ax)

    fig.set_figheight(height)
    fig.set_figwidth(width)
    fig.tight_layout()


def plot_SigClust(width, height, filename):
    fig, ax = plt.subplots()
    data = pd.read_csv('results_clusterability/SigClust_Result_1.csv', encoding = 'utf8')
    sns.distplot(data['CI'], hist = False, color = 'black', ax = ax)
    ax.axvline(0.7140668, color = 'blue')
    ax.set_xlabel('Cluster Index')
    ax.set_ylabel('Density')
    config_fig_ax(fig, ax, width, height)
    fig.savefig('plots_clusterability/' + filename, dpi = 300, transparent = True)

    print("SigClust")
    print('Sample average cluster index', np.mean(data['CI']))
    print('Sample standard deviation cluster index', np.std(data['CI']))

def plot_GapStat(width, height, filename):
    fig, ax = plt.subplots()
    data = pd.read_csv('results_clusterability/GapStat_Result.csv', encoding = 'utf8')
    x = data['k']
    y = data['gap']
    ax.plot(x, y, color = 'black')
    ax.set_xlabel('Number of clusters')
    ax.set_ylabel('Gap')
    ax.set_xticks([1, 20, 40, 60])
    config_fig_ax(fig, ax, width, height)
    fig.savefig('plots_clusterability/' + filename, dpi = 300, transparent = True)


def main():
    plot_SigClust(3, 3, 'Sigclust_1:1.png')
    plot_GapStat(3, 3, 'GapStatistics_1:1.png')

    plot_SigClust(3, 1.5, 'Sigclust_1:2.png')
    plot_GapStat(3 * 1.3, 1.5 * 1.3, 'GapStatistics_1:2.png')


    plot_SigClust(3 * 1.3, 2 * 1.3, 'Sigclust_3:2.png')

if __name__ == "__main__":
    main()
