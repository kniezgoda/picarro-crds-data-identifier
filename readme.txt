This program requires the following non-standard Python packages:   
-matplotlib   
-pandas   
-numpy   
-pylab   
-tkinter/Tkinter (python 3.x/python2.x)
-scipy   
If these packages are not yet on your computer, it is suggested that you use Anaconda to install them. [This](http://conda.pydata.org/docs/_downloads/conda-cheatsheet.pdf) cheat sheet was extremely helpful for me in installing and working with Anaconda, and should include everything you need to know. After the Anaconda install, create a conda environment with:

conda create --name python27 python=2.7 anaconda

This will create a virual python environment on your computer with the Python 2.7 build and all the necessary packages needed to run this program. This may take a while. Activate this program by typing:

source activate python27 (mac, linux)  
activate python27 (windows)

Finally, run the program by typing in:

python PicCRDS_DIA.py
