import os
import tkinter as tk
from tkinter import filedialog
import numpy as np
import matplotlib.pyplot as plt
import json
import time
import csv
from matplotlib.colors import ListedColormap as colorm
from matplotlib.widgets import Button
import matplotlib.font_manager as fm

font_path = "/home/jumeys/Documents/Code/ConwaysGame/Conways_Game/Baskervville/Baskervville-VariableFont_wght.ttf"
custom_font = fm.FontProperties(fname=font_path)
root = tk.Tk()
root.withdraw()
target_dir = os.path.dirname(os.path.abspath(__file__))
selected_file = filedialog.askopenfilename(initialdir=target_dir, title="Select a file", filetypes=[("Text files", "*.json"), ("All files", "*.*")])
fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(8, 6))
ax_button = fig.add_axes([0.45, 0.05, 0.1, 0.05])
pause_button = Button(ax_button, 'Pause', color='lightgray', hovercolor='tomato')
with open(selected_file, "r") as file:
    data = json.load(file)

HEIGHT = data["height"] + 1
WIDTH = data["width"] + 1
REPRODUCE_ADJ = data["reproduce_adj"]
OVERPOP_TSH = data["overpop_tsh"]
UNDERPOP_TSH = data["underpop_tsh"]
DEAD_CELL_RADIUS = data["radius_generate"]
RADIUS_LIVE_CELL = data["radius_death"]

IMPORT_FROM_CSV = True
if IMPORT_FROM_CSV:
    selected_file = filedialog.askopenfilename(initialdir=target_dir, title="Select a file", filetypes=[("Text files", "*.csv"), ("All files", "*.*")])
    MAP = np.zeros((HEIGHT, WIDTH), dtype=bool)
    coords = np.loadtxt(selected_file, delimiter=',', dtype=int)
    MAP[coords[:, 0], coords[:, 1]] = True
else:
    MAP = np.zeros((HEIGHT, WIDTH), dtype=bool)

SEARCH_CELLS = np.zeros((HEIGHT, WIDTH), dtype=bool)
STORED_MAP = np.zeros((HEIGHT, WIDTH), dtype=bool)
DIFFERENTIAL_MAP = np.zeros((HEIGHT, WIDTH), dtype=bool)

PAUSED_STATE = True


CLK = 1




def cell_adjacencies(map, radius, y_coord, x_coord):
    global SEARCH_CELLS
    adjacent_cells = 0
    n_rows, n_cols = map.shape
    west_bound = max(0, x_coord-radius)
    east_bound = min(n_cols, x_coord + radius + 1)

    north_bound = max(0, y_coord-radius)
    south_bound = min(n_rows, y_coord + radius + 1)

    search_matrix = map[north_bound:south_bound, west_bound:east_bound]


    for row in search_matrix:
        for value in row:
            if value == True:
                adjacent_cells += 1

    if map[y_coord, x_coord] == True:
        adjacent_cells -= 1

    return adjacent_cells



def iterate_conway():
    global MAP, STORED_MAP, DIFFERENTIAL_MAP, SEARCH_CELLS
    map = MAP.copy()
    
    set_search_area()
    for (row, col), value in np.ndenumerate(MAP):
        #print(f"row, col: {row}, {col}\nValue: {value}")
        if SEARCH_CELLS[row, col] == True:
            if value == True:
                if (cell_adjacencies(MAP, RADIUS_LIVE_CELL, row, col) <= UNDERPOP_TSH) or (cell_adjacencies(MAP, RADIUS_LIVE_CELL, row, col) >= OVERPOP_TSH):
                    #print("Killed")
                    map[row, col] = False
            else:
                if cell_adjacencies(MAP, DEAD_CELL_RADIUS, row, col) == REPRODUCE_ADJ:
                    #print("Born")
                    map[row, col] = True
    STORED_MAP = np.copy(MAP)
    #print(STORED_MAP)
    MAP = np.copy(map)

def set_differential():
    global DIFFERENTIAL_MAP, STORED_MAP
    DIFFERENTIAL_MAP = np.zeros((HEIGHT, WIDTH), dtype=bool)
    for (row, col), value in np.ndenumerate(MAP):
        if value != STORED_MAP[row, col]:
            DIFFERENTIAL_MAP[row, col] = True

def set_search_area():
    global SEARCH_CELLS
    set_differential()
    SEARCH_CELLS = np.zeros((HEIGHT, WIDTH), dtype=bool)

    n_rows, n_cols = DIFFERENTIAL_MAP.shape
    if RADIUS_LIVE_CELL > DEAD_CELL_RADIUS:
        radius = RADIUS_LIVE_CELL
    else:
        radius = DEAD_CELL_RADIUS
    for (row, col), value in np.ndenumerate(DIFFERENTIAL_MAP):
        if value == True:
            west_bound = max(0, col-radius)
            east_bound = min(n_cols, col + radius + 1)

            north_bound = max(0, row-radius)
            south_bound = min(n_rows, row + radius + 1)
            SEARCH_CELLS[north_bound:south_bound, west_bound:east_bound] = True

def refresh_plots(plt1, plt2, plt3, plt4):
    global MAP, SEARCH_CELLS, DIFFERENTIAL_MAP, STORED_MAP
    plt1.set_data(MAP)
    plt2.set_data(SEARCH_CELLS)
    plt3.set_data(STORED_MAP)
    plt4.set_data(DIFFERENTIAL_MAP)

    for img in (plt1, plt2, plt3, plt4):
        img.set_clim(0, 1)

    fig.canvas.draw()
    plt.pause(0.01)


def pause_unpause(event):
    global PAUSED_STATE
    PAUSED_STATE = not PAUSED_STATE

def update():
    if not PAUSED_STATE:
        iterate_conway()
        refresh_plots(conway, searched_area, stored_conway, differential)
    return True

def grid_click(event):
    global MAP
    if not PAUSED_STATE or event.inaxes != axes[0, 0]:
        return

    col = int(event.xdata+0.5)
    row = int(event.ydata+0.5)

    MAP[row, col] = not MAP[row, col]

    conway.set_data(MAP)
    fig.canvas.draw_idle()

conway = axes[0, 0].imshow(MAP, cmap='binary')
axes[0, 0].grid()
axes[0, 0].set_xticks(np.arange(-0.5, WIDTH+1, 1))
axes[0, 0].set_yticks(np.arange(-0.5, HEIGHT+1, 1))
axes[0, 0].set_xlim(-0.5, WIDTH-0.5)
axes[0, 0].set_ylim(HEIGHT-0.5, -0.5)
axes[0, 0].set_title(label='Conway\'s Game of Life', fontproperties=custom_font, fontsize=18, fontweight='bold')
axes[0, 0].set_xticklabels([])
axes[0, 0].set_yticklabels([])

searched_area = axes[0,1].imshow(SEARCH_CELLS, cmap='binary')
axes[0, 1].grid()
axes[0, 1].set_xticks(np.arange(-0.5, WIDTH+1, 1))
axes[0, 1].set_yticks(np.arange(-0.5, HEIGHT+1, 1))
axes[0, 1].set_xlim(-0.5, WIDTH-0.5)
axes[0, 1].set_ylim(HEIGHT-0.5, -0.5)
axes[0, 1].set_title(label='Searched Arrays', fontproperties=custom_font, fontsize=18, fontweight='bold')
axes[0, 1].set_xticklabels([])
axes[0, 1].set_yticklabels([])

stored_conway = axes[1, 0].imshow(STORED_MAP, cmap='binary')
axes[1, 0].grid()
axes[1, 0].set_xticks(np.arange(-0.5, WIDTH+1, 1))
axes[1, 0].set_yticks(np.arange(-0.5, HEIGHT+1, 1))
axes[1, 0].set_xlim(-0.5, WIDTH-0.5)
axes[1, 0].set_ylim(HEIGHT-0.5, -0.5)
axes[1, 0].set_title(label='Stored Conway Iteration', fontproperties=custom_font, fontsize=18, fontweight='bold')
axes[1, 0].set_xticklabels([])
axes[1, 0].set_yticklabels([])

differential = axes[1, 1].imshow(DIFFERENTIAL_MAP, cmap='binary')
axes[1, 1].grid()
axes[1, 1].set_xticks(np.arange(-0.5, WIDTH+1, 1))
axes[1, 1].set_yticks(np.arange(-0.5, HEIGHT+1, 1))
axes[1, 1].set_xlim(-0.5, WIDTH-0.5)
axes[1, 1].set_ylim(HEIGHT-0.5, -0.5)
axes[1, 1].set_title(label='Differential Conway', fontproperties=custom_font, fontsize=18, fontweight='bold')
axes[1, 1].set_xticklabels([])
axes[1, 1].set_yticklabels([])


pause_button.on_clicked(pause_unpause)
fig.canvas.mpl_connect('button_press_event', grid_click)
timer = fig.canvas.new_timer(interval=CLK)
timer.add_callback(update)
timer.start()
plt.show()
