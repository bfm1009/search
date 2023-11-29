import sys
import pandas as pd
import numpy as np
import tkinter as tk
import matplotlib.pyplot as plt

SQUARE_SIZE = 2
WIDTH_IN_SQUARES = 600
HEIGHT_IN_SQUARES = 200

# Global variables
data = None
nodesAtDepth = None
T = None
window = None
canvas = None
squareIds = [[0 for w in range(WIDTH_IN_SQUARES)] for h in range(HEIGHT_IN_SQUARES)]
lastTime = -1
cmap = plt.cm.get_cmap("YlOrRd")

def rgbaToHex(rgba):
    r = int(rgba[0] * 255)
    b = int(rgba[1] * 255)
    g = int(rgba[2] * 255)
    return f"#{r:02x}{g:02x}{b:02x}"

def update(time):
    global lastTime

    time = int(time)
    inc = 1 if time >= lastTime else -1

    # Visualize or un-visualize data since last visualization time
    dataAtTime = data[(data.expnum > lastTime) & (data.expnum <= time)] if time >= lastTime else data[(data.expnum <= lastTime) & (data.expnum > time)]

    for i, row in dataAtTime.iterrows():
        # Get color of square
        color = None
        if time >= lastTime:
            relExpTime = row.expnum / T
            rgba = cmap(relExpTime)
            color = rgbaToHex(rgba)
        else:
            color = "white"

        # Get position of square and recolor it
        depth = int(row.depth)
        if inc == -1: nodesAtDepth[depth] += inc
        w = nodesAtDepth[depth]
        h = depth
        if (w < WIDTH_IN_SQUARES and h < HEIGHT_IN_SQUARES):
            canvas.itemconfig(squareIds[h][w], fill=color)
        if inc == 1: nodesAtDepth[depth] += inc
    
    lastTime = time

def main():
    global data, nodesAtDepth, T, window, canvas

    # Read in dump file from command line
    if len(sys.argv) != 2:
        print("Usage: python3 visualizer.py [dumpFile]")
        return
    dumpFile = sys.argv[1]
    data = pd.read_csv(dumpFile)
    maxDepth = np.max(data.depth)
    nodesAtDepth = [0 for i in range(maxDepth + 1)]
    T = np.max(data.expnum)
    
    # Create visualization window
    window = tk.Tk()
    canvas = tk.Canvas(window, width=WIDTH_IN_SQUARES * SQUARE_SIZE, height=HEIGHT_IN_SQUARES * SQUARE_SIZE)
    canvas.pack()
    slider = tk.Scale(window, from_=0, to=T, orient=tk.HORIZONTAL, length=WIDTH_IN_SQUARES * SQUARE_SIZE, command=update)
    slider.pack()
    
    for h in range(HEIGHT_IN_SQUARES):
        for w in range(WIDTH_IN_SQUARES):
            x = w * SQUARE_SIZE
            y = h * SQUARE_SIZE
            sqrId = canvas.create_rectangle(x, y, x + SQUARE_SIZE, y + SQUARE_SIZE, fill="white", outline="")
            squareIds[h][w] = sqrId

    update(0)
    window.mainloop()

if __name__ == "__main__":    
    main()