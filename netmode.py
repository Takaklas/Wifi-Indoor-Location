import matplotlib.pyplot as plt

def plot_ergasthrio(ax):
    ax.hlines(y=0, xmin=0, xmax=4.5, linewidth=2, color='r')
    ax.hlines(y=16.5, xmin=0, xmax=4.5, linewidth=2, color='r')

    ax.hlines(y=14, xmin=-7.35, xmax=0, linewidth=2, color='r')
    ax.hlines(y=16.5, xmin=-7.35, xmax=1.65, linewidth=2, color='r')

    ax.hlines(y=11, xmin=2.3, xmax=4.5, linewidth=2, color='g')
    ax.hlines(y=12.4, xmin=1.65, xmax=4.5, linewidth=2, color='b')
    ax.hlines(y=14, xmin=1.65, xmax=4.5, linewidth=2, color='b')
    ax.vlines(x=1.65, ymin=12.4, ymax=14, linewidth=2, color='b')

    ax.vlines(x=0, ymin=0, ymax=14, linewidth=2, color='r')
    ax.vlines(x=2.3, ymin=0, ymax=16.5, linewidth=2, color='r')
    ax.vlines(x=4.5, ymin=0, ymax=16.5, linewidth=2, color='r')

    ax.vlines(x=-7.35, ymin=14, ymax=16.5, linewidth=2, color='r')

    ax.hlines(y=2.85, xmin=0, xmax=1.3, linewidth=2, color='g')
    ax.hlines(y=2.85+1.85, xmin=1.3, xmax=4.5, linewidth=2, color='r')
    ax.vlines(x=1.3, ymin=2.85, ymax=2.85+1.85, linewidth=2, color='r')
