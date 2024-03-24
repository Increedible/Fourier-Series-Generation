import math
from svgpathtools import svg2paths

nrange = 250

dt = 1/(nrange * 2)

nmin = -nrange
nmax =  nrange
precisiondigits = nrange * 100

from svgpathtools import svg2paths
import numpy as np

paths, attributes = svg2paths("Ufo 2.svg")

def get_point_at_t(t: float):
    # Load paths and attributes from the SVG

    # Calculate total length of all paths to properly scale t
    total_length = sum(path.length() for path in paths)

    # Scale t to the total length
    t_scaled = t * total_length

    # Find the specific path and the local t for the scaled t
    length_covered = 0
    for path in paths:
        if length_covered + path.length() >= t_scaled:
            # Calculate local t for this path
            local_t = (t_scaled - length_covered) / path.length()
            # Return the point at local_t on this path
            point = path.point(local_t)
            return (point.real, -point.imag)
        length_covered += path.length()

    # If t = 1, return the last point of the last path
    if t == 1.0:
        point = paths[-1].point(1.0)
        return (point.real, -point.imag)

    # In case t is out of bounds or no paths are found
    return (0, 0)

def getF(t):
    #return (-t * 2 - 1, -t * 2 - 1)
    return get_point_at_t(t)


# print("[", end="")
# for i in range(nmin, nmax):
#     print(i, end=", ")
# print(nmax, end="]\n")

filename = 'output.txt'
with open(filename, 'w') as file:
    print("\n[", end="")
    for n in range(nmin, nmax + 1):
        vx = 0
        vy = 0
        for k in range(int(1/dt)):
            a,b = getF(k*dt)
            c = math.cos(-n*2*math.pi*k*dt)
            d = math.sin(-n*2*math.pi*k*dt)
            vx += a * c - b * d
            vy += b * c + a * d
        vx = round(vx * precisiondigits) / precisiondigits
        vy = round(vy * precisiondigits) / precisiondigits
        if n == 0:
            vx, vy = 0, 0
        if n == nmax:
            print(f"({vx}, {vy})", end="]")
        else:
            print(f"({vx}, {vy})", end=", ")
        file.write(f'{vx} {vy}\n')
