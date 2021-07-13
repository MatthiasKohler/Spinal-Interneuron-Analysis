sides_all = ['top', 'right', 'bottom', 'left']
sides = ['top', 'right']


def hide_spines(ax):
    for s in sides:
        ax.spines[s].set_visible(False)


def set_spine_color(ax, color):
    for s in sides:
        ax.spines[s].set_color(color)


def set_spine_width(ax, lw):
    for s in sides:
        ax.spines[s].set_linewidth(lw)
