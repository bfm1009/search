# Usage example: python3 ps_visualizer.py dumps/outstanding_k2.csv

import sys
import pandas as pd
import numpy as np
import tkinter as tk
import matplotlib.pyplot as plt

SQUARE_SIZE = 1
CIRCLE_RADIUS = 2

class Node:
  def __init__(self, depth, expnum, goal):
    self.depth = depth
    self.expnum = expnum
    self.goal = goal == 1

def rgbaToHex(rgba):
    r = int(rgba[0] * 255)
    b = int(rgba[1] * 255)
    g = int(rgba[2] * 255)
    return f"#{r:02x}{g:02x}{b:02x}"

def drawCircle(canvas, x, y, r):
    x0 = x - r
    y0 = y - r
    x1 = x + r
    y1 = y + r
    canvas.create_oval(x0, y0, x1, y1, fill="black", outline="")

def draw(canvas, nodesByDepth, T):
    cmap = plt.cm.get_cmap("YlGnBu")

    for depthLevel in nodesByDepth:
        w = 0
        for node in depthLevel:
            # Find color of square
            relExpTime = node.expnum / T
            rgba = cmap(relExpTime)
            color = rgbaToHex(rgba)

            # Draw square
            h = node.depth
            x = w * SQUARE_SIZE
            y = h * SQUARE_SIZE
            canvas.create_rectangle(x, y, x + SQUARE_SIZE, y + SQUARE_SIZE, fill=color, outline="")
            w += 1

            # If node is a goal, draw circle
            if node.goal:
                drawCircle(canvas, x, y, CIRCLE_RADIUS)

def main():
    # Read in dump file from command line
    if len(sys.argv) != 2:
        print("Usage: python3 visualizer.py [dumpFile]")
        return
    dumpFile = sys.argv[1]
    fileName = dumpFile.split(".")[0]
    outputFile = f"{fileName}.ps"
    data = pd.read_csv(dumpFile)
    maxDepth = np.max(data.depth) + 1
    T = np.max(data.expnum)
    nodesByDepth = [[] for i in range(maxDepth)]
    maxNodesAtDepth = 0

    for i, row in data.iterrows(): # This works because data is ordered by expnum
        depth = row.depth
        expnum = row.expnum
        goal = row.goal
        node = Node(depth, expnum, goal)
        nodesByDepth[depth].append(node)

    for depthLevel in nodesByDepth:
        nodesAtDepth = len(depthLevel)
        if nodesAtDepth > maxNodesAtDepth:
            maxNodesAtDepth = nodesAtDepth
    
    # Create visual
    window = tk.Tk()
    canvasW = maxNodesAtDepth * SQUARE_SIZE
    canvasH = maxDepth * SQUARE_SIZE
    canvas = tk.Canvas(window, width=canvasW, height=canvasH)
    draw(canvas, nodesByDepth, T)

    # Output visual to ps file
    canvas.postscript(file=outputFile, colormode="color", width=canvasW, height=canvasH)

if __name__ == "__main__":    
    main()