#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors
import pandas as pd
import sys

from mpl_toolkits.axes_grid1.inset_locator import inset_axes

sides = ['top', 'right', 'bottom', 'left']

def hide_spines(ax):
    for s in sides:
        ax.spines[s].set_visible(False)

cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["black", "whitesmoke"])

def plot_table(data, ax):
    hide_spines(ax)
    ax.imshow(np.array(data.values).T, cmap = cmap)
    labels = data.head()
    #ax.set_yticks(np.arange(len(labels) + 1))
    ax.set_yticks([])
    ax.set_yticklabels(labels)
    ax.set_ylim([-1.0, 6.0])
    ax.set_xticks([])
    return ax

usage = """plot_binary_data.py Input.csv Output"""

def main():
    try:
        data_file = sys.argv[1]
        if len(sys.argv) < 3:
            plot_file = data_file + '.png'
        else:
            plot_file = sys.argv[2]
    except:
        print(usage)
        return

    data = pd.read_csv(data_file, encoding = 'utf8')
    data = data.drop(['ID'], axis = 1)

    fig, ax = plt.subplots()
    plot_table(data, ax)
    plt.savefig(plot_file, transparacy = True, bbox_inches='tight', dpi = 300)


if __name__ == "__main__":
    main()
