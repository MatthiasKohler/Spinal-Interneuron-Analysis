#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import re
import pandas as pd

import plot_style

def plot_table(table, filename):
    original_value = table[table.original == "T"].Value.values[0]

    fig, ax = plt.subplots()
    fig.set_figheight(2.5)
    fig.set_figwidth(3.5)
    ax.plot(table.Value, table.freq, color = "black")
    ax.axvline(x = original_value, color = 'blue', linestyle = '-')
    ax.set_xlabel('Number of Loops')
    ax.set_ylabel('Number of Samples')

    plot_style.hide_spines(ax)
   
    fig.tight_layout()
    fig.savefig('./plots_loops/' + filename + '.pdf', dpi = 300)

ExEx_table = pd.read_csv("./results_loops/ExEx.csv", encoding = 'utf8')

plot_table(ExEx_table, "ExEx")
