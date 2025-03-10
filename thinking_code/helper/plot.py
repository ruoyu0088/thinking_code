import numpy as np
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.cm import tab20
from itertools import cycle


def plot_number_link_board(board, links=None, cells=None):
    h, w = board.shape
    fig, ax = plt.subplots(1, 1, figsize=(w * 0.4, h * 0.4))
    if links is not None and cells is not None:
        for (r1, c1, r2, c2), link in links.items():
            if link:
                ax.plot([c1, c2], [r1, r2], color=tab20.colors[cells[r1, c1]], lw=3)
    xs = []
    ys = []
    texts = []
    for (r, c), v in np.ndenumerate(board):
        xs.append(c)
        ys.append(r)
        texts.append(str(v))
    
    ax.scatter(xs, ys)
    for x, y, s in zip(xs, ys, texts):
        if s != "0":
            ax.text(x, y, s, ha='center', va='center', fontsize=12, 
                    bbox=dict(facecolor=tab20.colors[int(s)], edgecolor='black', boxstyle='round,pad=0.2'))
    
    ax.invert_yaxis()
    ax.axis('off')
    return fig, ax


def plot_slither_link_board(board, result=None):
    h, w = board.shape    

    fig, ax = plt.subplots(figsize=(w*0.3, h*0.3))
    ax.set_ylim(-0.1, h + 0.1)
    ax.set_xlim(-0.1, w + 0.1)
    ax.invert_yaxis()
    ax.set_aspect("equal")
    all_segments = []
    circuit_segments = []

    if result is not None:
        for (n1, n2), flag in result.items():
            if flag:
                r1, c1 = n1 // (w + 1), n1 % (w + 1)
                r2, c2 = n2 // (w + 1), n2 % (w + 1)                
                circuit_segments.append([(c1, r1), (c2, r2)])

    for r, c in np.ndindex(h + 1, w + 1):
        if r + 1 <= h:
            all_segments.append([(c, r), (c, r + 1)])
        if c + 1 <= w:
            all_segments.append([(c, r), (c + 1, r)])

    ax.add_collection(LineCollection(all_segments, color='gray', alpha=0.5))
    ax.add_collection(LineCollection(circuit_segments, color='green', linewidth=2))
    for (i, j), v in np.ndenumerate(board):
        if v != -1:
            ax.text(j + 0.5, i + 0.5, str(v), fontsize=12, va='center', ha='center')
    ax.autoscale_view()        
    ax.axis('off')
    return fig, ax

def plot_nonogram_board(puzzle, solution, font_size=12):
    solution = np.asarray(solution)
    nrow, ncol = solution.shape
    
    fig, ax = plt.subplots(figsize=(nrow * 0.2, ncol * 0.2))
    ax.set_aspect("equal")

    Y, X = np.ogrid[:nrow, :ncol]
    
    font = dict(fontsize=font_size)

    ax.set_yticks(Y.ravel() - 0.5)
    y_ticks = [" ".join(str(c) for c in item) for item in puzzle['rows']]
    ax.set_yticklabels(y_ticks, fontdict=font)

    ax.set_xticks(X.ravel() - 0.5)
    x_ticks = ["\n".join(str(c) for c in item) for item in puzzle['cols']]
    ax.set_xticklabels(x_ticks, fontdict=font)

    ax.set_xlim(-1, X.max())
    ax.set_ylim(-1, Y.max())

    ax.pcolormesh(X-0.5, Y-0.5, solution, vmin=0, vmax=1.5, 
                  cmap="gray_r", edgecolors="white", shading="auto")
    ax.invert_yaxis()
    for edge in ("right", "top"):
        ax.spines[edge].set_visible(False) 
    return fig, ax    

def plot_shikaku_board(board, rects=[], figsize=(6, 6)):
    height, width = board.shape
    Y, X = np.where(board > 0)
    V = board[Y, X]
    
    colors = cycle(tab20.colors)
    fig, ax = plt.subplots(figsize=figsize)
    for rect in rects:
        x, y, w, h = rect
        ax.add_patch(plt.Rectangle((x, y), w, h, facecolor=next(colors), edgecolor='black', alpha=0.5))
    
    for x, y, v in zip(X, Y, V):
        ax.text(x + 0.5, y + 0.5, str(v), fontsize=14, ha='center', va='center')
    
    y, x = np.mgrid[:height, :width]
    
    ax.scatter(x.ravel() + 0.5, y.ravel() + 0.5, s=1, marker='s')
    
    ax.set_xlim(0-0.1, width+0.1)
    ax.set_ylim(0-0.1, height+0.1)
    ax.invert_yaxis()
    ax.set_aspect('equal')
    ax.axis('off')
    return fig, ax