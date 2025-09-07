# FourierTransform
A public Python repo that uses SvgPathTools and PyGame to create and visualize a Fourier series to draw out any svg.

**Usage**

1. Generate your svg, the paths should be minimal and connected. Imagine trying to draw it on paper without remove your pencil from the paper, so if you choose to add anything disconnected from the rest (like eyes on a smiley) the vectors will draw a line to it.
2. Use "Generate Vectors.py" to generate the vectors for this, and change the name of the svg file within the document to your svg file name. Also, change the 'nrange' variable, which will generate (nrange * 2) + 1 vectors (so for nrange = 250 that will generate 501 vectors). This will output an array which you could paste directly into the "Visualise Vectors.py", but right now it just uses the outputted 'output.txt' that also contains this information.
3. Run the "Visualise Vectors.py", within the program the bottom right slider equals to the amount of miliseconds for a full rotation of the first vector to complete ('unit').

**Alternate Usage**
1. Think of what you want to render.
2. Run the program on any .svg
3. Draw your shape (by clicking and holding mouse 1) and let the program do the magic!
