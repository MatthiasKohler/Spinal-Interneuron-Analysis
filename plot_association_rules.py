#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import re
import pandas as pd
from mpl_toolkits.axes_grid1.inset_locator import inset_axes


significance_level = 1 - ((1 - 0.05) ** (1 / 30))
print("significance_level", significance_level)

relabel = {'Skin-2':'Skin - In', 'Ia-2':'Ia - In', 'Ib-2':'Ib - In',
           'Skin1': 'Skin - Ex',  'Ia1':'Ia - Ex',  'Ib1':'Ib - Ex'}

bg_green = (0, 1, 94 / 255, 0.5)
bg_red = (1, 0, 0, 140 / 255)
bg_grey = (0, 0, 0, 0.1)

sides = ['top', 'right', 'bottom', 'left']
def hide_spines(ax):
    for s in sides:
        ax.spines[s].set_visible(False)


def set_spine_color(ax, color):
    for s in sides:
        ax.spines[s].set_color(color)


def set_spine_width(ax, lw):
    for s in sides:
        ax.spines[s].set_linewidth(lw)


def match(s):
    m = re.search('(.*) => (.*) p = ([0-9]*.[0-9]*)', s)
    return [m.group(1), m.group(2), m.group(3)]


def fixTable(table):
    table = table.loc[lambda r: r.Name != "Name", :]
    cols = table.apply(lambda r: pd.Series(match(r.Name), index = ['l', 'r', 'p']), axis = 1)
    table = table.join(cols)
    table.Value = pd.to_numeric(table.Value)
    table.freq = pd.to_numeric(table.freq)
    table.p = pd.to_numeric(table.p)
    return table


def get_transactions(table):
    return set(table.l)


def plot_table(table, ax):
    p = table.p.iloc[0]
    original = table[table.original == 'T'].Value.iloc[0]

    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0, 3000000])
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    set_spine_width(ax, 1.5)

    if p <= significance_level and original < table.Value.mean():
        ax.set_facecolor(bg_red)
        set_spine_color(ax, 'red')        
        ax.plot(table.Value, table.freq, color = 'black')        
        ax.axvline(x = original, color = 'grey')
    elif p <= significance_level and original > table.Value.mean():
        ax.set_facecolor(bg_green)
        set_spine_color(ax, 'green')
        ax.plot(table.Value, table.freq, color = 'black')
        ax.axvline(x = original, color = 'grey')
    else:
        ax.set_facecolor(bg_grey)        
        ax.plot(table.Value, table.freq, color = 'black')
        ax.axvline(x = original, color = 'grey') 
    
    total = table.freq.sum()
    smaller = table[table.Value < original].freq.sum()
    larger  = table[table.Value > original].freq.sum()

    return ax


def get_support(transactions, data):
    support = {}
    for t in transactions:
        support[t] = data[t].sum() / data.shape[0]
    return support


def plot_association_rules(rules, data):
    transactions = list(get_transactions(rules))

    support = get_support(transactions, data)
    transactions.sort(key = lambda t: support[t])
    labels = list(map(lambda t: relabel[t], transactions))

    composition_fig, composition = plt.subplots()
    plt.gcf().subplots_adjust(left=0.25)

    n_transactions = len(transactions)

    composition.set_xlim([0, n_transactions])
    composition.set_ylim([0, n_transactions])

    composition.set_xticks(np.arange(0.5, n_transactions + 0.5, 1.0))
    composition.set_xticklabels(labels, {'fontsize': 9.0})
    composition.set_yticks(np.arange(0.5, n_transactions + 0.5, 1.0))
    composition.set_yticklabels(labels, {'fontsize': 9.0})

    hide_spines(composition)

    height = width = str((100 / n_transactions) - 2) + "%"

    for l, i in zip(transactions, range(n_transactions)):
        for r, j in zip(transactions, range(n_transactions)):
            if l == r:
                continue
            table = rules[(rules.l == l) & (rules.r == r)]
            inset = inset_axes(composition, width=width, height = height, loc = 3, bbox_to_anchor=[i / n_transactions, j / n_transactions, 1, 1], 
                               bbox_transform = composition.transAxes)
            plot_table(table, inset)


    composition_fig.set_figheight(2.8)
    composition_fig.set_figwidth(4.9) 
    composition_fig.savefig('./plots_association_rules/AssociationRuleMatrix.pdf', dpi = 500)


def main():
    rule_file = "./results_association_rules/AssociationRules.csv"
    data_file  = "./data_synaptology/Synaptology_tidy_reduced.csv"

    data  = pd.read_csv(data_file, encoding = 'utf8')
    rules = pd.read_csv(rule_file, encoding = 'utf8')
    rules = fixTable(rules)


    plot_association_rules(rules, data)


if __name__ == "__main__":
    main()
