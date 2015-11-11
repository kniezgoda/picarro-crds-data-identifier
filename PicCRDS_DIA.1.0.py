#!/usr/bin/env python

'''
PicCRDS_DIA: Picarro Cavity Ring-down Spectrometer Data Identifier Algorithm
Version 1.0
Finished September 17, 2015
Author: Kyle Niezgoda
kniezgoda@ntu.edu.sg (work)
kniezgo@gmail.com (personal)


The following non-standard python packages are required to run this program:

matplotlib, pandas, numpy, pylab, tkinter/Tkinter, scipy

All of the above packages can be downloaded by installing Anaconda for Python.


This app is optimized for use on Mac operating systems, but will work on Windows and Linux as well.
Some slight changes in GUI aesthetics will occur, but the data calibration and identification methods do not change.

App is currently not available for python version 3.x on Windows using the Anaconda installer, as the way Anaconda 
accesses Windows Tcl/Tk software is distrupting some of the printing procedures in the code. 
Windows users are encouraged to install Python version 2.x in order to use this software. 


Data files from the CRDS must be exported to csv.
See the SOP word document for more info on how to properly 
export data from the CRDS so that this program can use it.

Please first consult the SOP word file for help with code errors.
If this fails, please contact me (Kyle Niezgoda) at kniezgoda@ntu.edu.sg
'''

import matplotlib, sys, re, os
if sys.version_info[0] < 3:
    vers=2
    print("Using python version 2.x")
else:
    vers=3
    print("Using python version 3.x")

matplotlib.use('TkAgg')
import pandas as pd
import numpy as np
from pylab import *
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
if vers == 2:
    from Tkinter import *
    import tkFileDialog as filedialog
elif vers == 3:
    from tkinter import *
    import tkinter.filedialog as filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.backends.backend_pdf import PdfPages
from os.path import expanduser
from math import *
from scipy import stats
import time

home=os.path.expanduser("~")
std_data = ''

class FirstWidget:
    def __init__(self, parent):
        self.FirstTk = parent
        self.FirstTk.title("Choose files and set variables")

        self.Frame1 = Frame(self.FirstTk,bd=2,relief=GROOVE)
        self.Frame1.pack(pady=2,fill=X)

        self.Frame2 = Frame(self.FirstTk,bd=2,relief=GROOVE)
        self.Frame2.pack(pady=2,fill=X)

        self.Frame3 = Frame(self.FirstTk,bd=2,relief=GROOVE)
        self.Frame3.pack(pady=2,fill=X)
        self.Frame3_avgby = Frame(self.Frame3)
        self.Frame3_avgby.pack(anchor='w')
        self.Frame3_memeff = Frame(self.Frame3)
        self.Frame3_memeff.pack(anchor='w')
        # self.Frame3_timediff = Frame(self.Frame3)
        # self.Frame3_timediff.pack(anchor='w')

        self.Frame4 = Frame(self.FirstTk)
        self.Frame4.pack(pady=2,fill=X)

        ###Frame 1
        #left side:
        self.Frame1_left = Frame(self.Frame1)
        self.Frame1_left.pack(side='left', fill=Y)
        self.cd_button = Button(self.Frame1_left,text='Set Working Directory', command=self.OnCdButtonClick,height=1)
        self.cd_button.pack(anchor='w',pady=5)

        self.filechoose_frame1_left = Frame(self.Frame1_left)
        self.filechoose_frame1_left.pack(pady=20,fill=X)
        self.filechoose_button = Button(self.filechoose_frame1_left,text="Choose Input file", command=self.OnFilechooseClick,height=1)
        self.filechoose_button.pack(anchor='center')
        self.filechoose_delete_button = Button(self.filechoose_frame1_left, text='Remove entries', command=self.DeleteFiles)
        self.filechoose_delete_button.pack(anchor='center')

        self.fileout_label = Label(self.Frame1_left,text='File output name:',height=1)
        self.fileout_label.pack(side='bottom',pady=4,anchor='center')

        #right side
        self.Frame1_right = Frame(self.Frame1)
        self.Frame1_right.pack(side='left', fill=X)
        self.cd_label = Text(self.Frame1_right,height=1,bd=2,relief=RIDGE)
        self.cd_label.insert(END,'Please set the working directory')
        self.cd_label.pack(anchor='center')

        self.filechoose_frame1_right = Frame(self.Frame1_right)
        self.filechoose_frame1_right.pack(pady=5)
        self.filechoose_text1 = Text(self.filechoose_frame1_right,height=1,bd=2,relief=RIDGE)
        self.filechoose_text1.pack(anchor='center')
        self.filechoose_text1.insert(END, 'Input File 1')
        self.filechoose_text2 = Text(self.filechoose_frame1_right,height=1,bd=2,relief=RIDGE)
        self.filechoose_text2.pack(anchor='center')
        self.filechoose_text2.insert(END, 'Input File 2 (optional)')
        self.filechoose_text3 = Text(self.filechoose_frame1_right,height=1,bd=2,relief=RIDGE)
        self.filechoose_text3.pack(anchor='center')
        self.filechoose_text3.insert(END, 'Input File 3 (optional)')

        self.fileout_text = Text(self.Frame1_right,height=1,bd=2,relief=SUNKEN)
        self.fileout_text.pack(side='bottom',anchor='center')



        ###Frame 2:
        #left side
        self.Frame2_left = Frame(self.Frame2)
        self.Frame2_left.pack(side=LEFT,fill=Y)
        self.std_button = Button(self.Frame2_left,text='Choose Calibration Standards', command=self.OnStdButtonClick)
        self.std_button.pack(pady=4)

        self.standard_method_frame = Frame(self.Frame2_left)
        self.standard_method_frame.pack(pady=10)
        self.standard_method = StringVar()
        self.standard_method.trace('w', self.standard_method_varchange)
        self.std_useDefault_checkbutton = Radiobutton(self.standard_method_frame,text='Set/use default standards', variable=self.standard_method, value='def')
        self.std_useDefault_checkbutton.pack(anchor='w')
        self.or_label = Label(self.standard_method_frame,text='---OR---')
        self.or_label.pack(anchor='center')
        self.std_maninput_checkbutton = Radiobutton(self.standard_method_frame,text='Manual Standard Entry', variable=self.standard_method, value='man')
        self.std_maninput_checkbutton.pack(anchor='w')

        #right side
        self.Frame2_right = Frame(self.Frame2)
        self.Frame2_right.pack(side=LEFT,fill=BOTH)
        self.stddata_text = Text(self.Frame2_right,height=1,bd=2,relief=RIDGE)
        self.stddata_text.pack(anchor='n')

        self.useDefault_text_Frame = Frame(self.Frame2_right)
        self.useDefault_text_Frame.pack(pady = 25)
        self.scrollbar = Scrollbar(self.useDefault_text_Frame, orient=HORIZONTAL)
        self.useDefault_text = Text(self.useDefault_text_Frame,height=1, wrap=NONE, xscrollcommand=self.scrollbar.set)
        self.useDefault_text.pack(anchor='n',expand=YES)
        self.useDefault_text.insert(END, 'Choose this box to set your default standards file to the file choosen above.')
        if os.path.isfile(home+'/.default_standard_data_PICARROALG.txt'):
            f = open(home+'/.default_standard_data_PICARROALG.txt', 'r')
            path = f.read()
            self.useDefault_text.delete(1.0, END)
            self.useDefault_text.insert(END, 'Default file is set to '+path)
        self.scrollbar.pack(fill=X,anchor='n')
        self.scrollbar.config(command=self.useDefault_text.xview)
        #cancel button
        self.Frame2_cancel = Frame(self.Frame2)
        self.Frame2_cancel.pack(side=RIGHT,fill=Y)
        self.cancel_button = Button(self.Frame2_cancel, text='Remove', command=self.RemoveStdData,height=1)
        self.cancel_button.pack(pady=4)



        ###FRAME3
        self.avgby_label = Label(self.Frame3_avgby,text="Average By Value:")
        self.avgby_label.pack(side=LEFT,anchor='s')
        self.avgby_scale = Scale(self.Frame3_avgby,from_=2,to=60,orient=HORIZONTAL)
        self.avgby_scale.set(30)
        self.avgby_scale.pack(side=LEFT)
        self.use_avgby = IntVar()
        self.avgby_button = Checkbutton(self.Frame3_avgby, text='Disable average-by', variable=self.use_avgby)
        self.avgby_button.pack(side=LEFT, anchor='s')
        self.memeffval_label = Label(self.Frame3_memeff,text="Memory Effect Value:")
        self.memeffval_label.pack(side=LEFT,anchor='s')
        self.memeffval_scale = Scale(self.Frame3_memeff,from_=0,to=2,orient=HORIZONTAL,resolution=.05)
        self.memeffval_scale.set(.75)
        self.memeffval_scale.pack(side=LEFT)
        # self.timediff_label = Label(self.Frame3_timediff,text="Starting hour:")
        # self.timediff_label.pack(side=LEFT,anchor='s')
        # self.timediff_scale = Scale(self.Frame3_timediff,from_=0,to=23,orient=HORIZONTAL)
        # self.timediff_scale.set(8)
        # self.timediff_scale.pack(side=LEFT)

        ###FRAME4
        self.run_button = Button(self.Frame4,text="Run",command=self.run, width=5)
        self.run_button.pack(side=LEFT,padx=3)
        self.cancel_button = Button(self.Frame4,text="Cancel",command=sys.exit, width=5)
        self.cancel_button.pack(side=LEFT,padx=3)

    ###instructions for clicking the CD button
    def OnCdButtonClick(self):
        global dir_
        global cd_label
        self.cd_label.grid_forget()
        ###user enters new directory
        dir_=filedialog.askdirectory()+'/'
        if dir_ != '':
            os.chdir(dir_)
            self.cd_label.delete(1.0, END)
            self.cd_label.insert(END, dir_)
        else:
            self.cd_label.delete(1.0, END)
            self.cd_label.insert(END, os.getcwd())

    ###instructions for clicking the filechoose button
    def OnFilechooseClick(self):
        dlg=filedialog.Open()
        #assign the path name of the selected file to temp
        temp = dlg.show()
        if temp is '':
            return None
        #assign the file name only to hold
        hold=re.split('/',temp)
        hold=hold[len(hold)-1]
        #insert text to the next avaiable input text box 
        if self.filechoose_text1.get("1.0",'end-1c').split(" ")[0] == "Input":
            self.filechoose_text1.delete(1.0, END)
            self.filechoose_text1.insert(END, hold)
            global fi1
            fi1=temp
        elif self.filechoose_text2.get("1.0",'end-1c').split(" ")[0] == "Input":
            self.filechoose_text2.delete(1.0, END)
            self.filechoose_text2.insert(END, hold)
            global fi2
            fi2=temp
        elif self.filechoose_text3.get("1.0",'end-1c').split(" ")[0] == "Input":
            self.filechoose_text3.delete(1.0, END)
            self.filechoose_text3.insert(END, hold)
            global fi3
            fi3=temp
        else:
            print("All available file slots are taken. Remove input files using the 'Remove entries' button before selecting new files.")

    def DeleteFiles(self):
        if not self.filechoose_text3.get("1.0",'end-1c').split(" ")[0] == "Input":
            self.filechoose_text3.delete(1.0, END)
            self.filechoose_text3.insert(END, 'Input file 3 (optional)')
        elif not self.filechoose_text2.get("1.0",'end-1c').split(" ")[0] == "Input":
            self.filechoose_text2.delete(1.0, END)
            self.filechoose_text2.insert(END, 'Input file 2 (optional)')
        elif not self.filechoose_text1.get("1.0",'end-1c').split(" ")[0] == "Input":
            self.filechoose_text1.delete(1.0, END)
            self.filechoose_text1.insert(END, 'Input file 1')
        else:
            print('All files have been removed.')

    def OnStdButtonClick(self):
        dlg=filedialog.Open()
        global std_data
        std_data=dlg.show()
        ###get the name of the file only
        hold=re.split('/',std_data)
        hold=hold[len(hold)-1]
        ###create a label showing the new file name
        if not hold == '':
            self.stddata_text.delete(1.0, END)
            self.stddata_text.insert(END, hold)
            if self.standard_method.get() == 'def':
                self.useDefault_text.delete(1.0, END)
                self.useDefault_text.insert(END, 'Default file will be set to '+hold)

    def standard_method_varchange(self, *args):
        global std_data
        if self.standard_method.get() == 'man':
            std_data = ''
            self.useDefault_text.delete(1.0, END)
            self.stddata_text.delete(1.0, END)
        if self.standard_method.get() == 'def':
            if std_data == '':
                if os.path.isfile(home+'/.default_standard_data_PICARROALG.txt'):
                    f = open(home+'/.default_standard_data_PICARROALG.txt', 'r')
                    path = f.read()
                    self.useDefault_text.delete(1.0, END)
                    self.useDefault_text.insert(END, 'Default file is set to '+path)
                if not os.path.isfile(home+'/.default_standard_data_PICARROALG.txt'):
                    self.useDefault_text.delete(1.0, END)
                    self.useDefault_text.insert(END, 'Default file will be set to the file choosen above')
            if not std_data == '':
                hold=re.split('/',std_data)
                hold=hold[len(hold)-1]
                self.useDefault_text.delete(1.0, END)
                self.useDefault_text.insert(END, 'Default file will be set to '+hold)
                    
    def RemoveStdData(self):
        global std_data
        std_data = ''
        self.stddata_text.delete(1.0, END)
        if standard_method.get() == 'def':
            self.useDefault_text.delete(1.0, END)
            if os.path.isfile(home+'/.default_standard_data_PICARROALG.txt'):
                f = open(home+'/.default_standard_data_PICARROALG.txt', 'r')
                path = f.read()
                self.useDefault_text.insert(END, 'Default file is set to '+path)
            if not os.path.isfile(home+'/.default_standard_data_PICARROALG.txt'):
                    self.useDefault_text.insert(END, 'Default file will be set to the file choosen above')

    ###instructions on clicking the run button:
    def run(self):  
        global fo, std_data, use
        #set the name for the output file and the standard data
        fo=self.fileout_text.get(1.0,END)[:-1]
        if std_data == '':
            if self.standard_method.get() == 'man':
                None
            if self.standard_method.get() == 'def':
                #if the default text file does not exist yet print an error and exit the program
                if not os.path.isfile(home+'/.default_standard_data_PICARROALG.txt'):
                    print('ERROR: Default file ~/.default_standard_data_PICARROALG.txt does not exist \n \
                    Please choose a standard data file first, then use the "Set default standards" option.')
                    sys.exit()
                #if the text files exists, read the text from the file as the path to the standard data
                if os.path.isfile(home+'/.default_standard_data_PICARROALG.txt'):
                    f = open(home+'/.default_standard_data_PICARROALG.txt', 'r')
                    std_data = f.read()
        if not std_data == '':
            if self.standard_method.get() == 'def':
                #write the path to the standard data as the first line in the text file
                f = open(home+'/.default_standard_data_PICARROALG.txt', 'w')
                f.write(std_data)
            else:
                None
        
        #set how many files will be used
        if not self.filechoose_text3.get("1.0",'end-1c').split(" ")[0] == "Input":
            use=2
        elif not self.filechoose_text2.get("1.0",'end-1c').split(" ")[0] == "Input":
            use=1
        else:
            use=0

        #determine whether or not data will be averaged
        global useavgby
        useavgby = self.use_avgby.get()
        if useavgby == 1:
            useavgby = False
        else:
            useavgby = True
        print(useavgby)

        #set file input name, avgby value, memory effect value, and start hour
        filename=self.filechoose_text1.get("1.0",'end-1c')
        if filename.split(" ")[0] == 'Input':
            print('Please select at least one file')
        else:
            global fi
            if use==0:
                fi=[fi1]
            if use==1:
                fi=[fi1, fi2]
            if use==2:
                fi=[fi1, fi2, fi3]
            global avgby
            avgby=self.avgby_scale.get()
            global memeffval
            memeffval=self.memeffval_scale.get()
            # global starthour
            # starthour=self.timediff_scale.get()

            self.FirstTk.destroy()

#manual standard entry class
class ManualStdEntryWidget:
    def __init__(self, parent):
        self.ManInput = parent
        self.ManInput.title("Set standard data manually")

        self.frame1 = Frame(self.ManInput,bd=2,relief=GROOVE)
        self.frame1.grid(row=0,column=0,padx=3)
        self.frame2 = Frame(self.ManInput,bd=2,relief=GROOVE)
        self.frame2.grid(row=0,column=1,padx=3)
        self.frame3 = Frame(self.ManInput,bd=2,relief=GROOVE)
        self.frame3.grid(row=0,column=2,padx=3)
        self.button_frame = Frame(self.ManInput)
        self.button_frame.grid(row=1,column=1,)

        self.std_label = Label(self.frame1, text='Enter standard names below separated by commas')
        self.std_label.grid(row=0,column=0)
        v1=StringVar()
        self.std_entry = Entry(self.frame1,borderwidth=2,relief=SUNKEN,textvariable=v1)
        self.std_entry.grid(row=1,column=0)

        self.d18O_label = Label(self.frame2, text='Enter true delta-18O values below separated by commas')
        self.d18O_label.grid(row=0,column=0)
        v2=StringVar()
        self.d18O_entry = Entry(self.frame2,borderwidth=2,relief=SUNKEN,textvariable=v2)
        self.d18O_entry.grid(row=1,column=0)

        self.dD_label = Label(self.frame3, text='Enter true delta-deuterium values below separated by commas')
        self.dD_label.grid(row=0,column=0)
        v3=StringVar()
        self.dD_entry = Entry(self.frame3,borderwidth=2,relief=SUNKEN,textvariable=v3)
        self.dD_entry.grid(row=1,column=0)

        self.std_enter_button = Button(self.button_frame,text='Enter',command=lambda: self.EnterStds(Standards=v1,true_d18O=v2,true_dD=v3))
        self.std_enter_button.grid(row=0,column=0,columnspan=1,padx=3)
        self.cancel_button = Button(self.button_frame,text='Cancel',command=self.ManInput.destroy)
        self.cancel_button.grid(row=0,column=1,columnspan=1,padx=3)

    def EnterStds(self, Standards, true_d18O, true_dD):
        global standards, d18O, dD, std
        standards=pd.Series(re.split(",",Standards.get()), dtype='object')
        standards=list(map(str.strip, standards))
        d18O=pd.Series(re.split(",",true_d18O.get()), dtype='float64')
        dD=pd.Series(re.split(",",true_dD.get()), dtype='float64')
        std = pd.DataFrame({'standard' : standards, 'real.d18O' : d18O, 'real.D_H' : dD})
        self.ManInput.destroy()

class FigureWidget:
    def __init__(self, parent, fig):
        self.FigureRoot = parent
        self.FigureRoot.title("Time Series Plot")
        self.canvas = FigureCanvasTkAgg(fig, master=self.FigureRoot)
        self.canvas = self.canvas.get_tk_widget()
        self.canvas.pack(fill=BOTH,expand=YES)

    def UpdatePlot(self, fig):
        self.canvas.destroy()
        self.canvas = FigureCanvasTkAgg(fig, master=self.FigureRoot)
        self.canvas = self.canvas.get_tk_widget()
        self.canvas.pack(fill=BOTH,expand=YES)

    def destroy(self):
        self.FigureRoot.destroy()
    
class LabelWidget:
    global num, col
    def __init__(self, parent):
        self.Label_Root = parent
        self.Label_Root.title("Enter event descriptors")
        global textbox_list, answer_list
        textbox_list = [] #holds identifiers for individual text boxes
        answer_list = pd.DataFrame({'color_group' : pd.Series(color_list), 'event' : pd.Series(repeat('event', len(color_list)))})

        self.Top_Label_Root = Frame(self.Label_Root)
        self.Top_Label_Root.grid(row=0,column=0)
        self.Bottom_Label_Root = Frame(self.Label_Root)
        self.Bottom_Label_Root.grid(row=1,column=0)

        #labels for the colors going across the top row
        self.redbutton = Button(self.Top_Label_Root,text='red',command=lambda: self.TriggerPlot(COL='red',NUM=num),width=4)
        self.redbutton.grid(row=0, column=1, sticky=S, pady=2)
        self.bluebutton = Button(self.Top_Label_Root,text='blue',command=lambda: self.TriggerPlot(COL='blue',NUM=num),width=5)
        self.bluebutton.grid(row=0, column=2, sticky=S, pady=2)
        self.greenbutton = Button(self.Top_Label_Root,text='green',command=lambda: self.TriggerPlot(COL='green',NUM=num),width=6)
        self.greenbutton.grid(row=0, column=3, sticky=S, pady=2)
        self.brownbutton = Button(self.Top_Label_Root,text='brown',command=lambda: self.TriggerPlot(COL='brown',NUM=num),width=6)
        self.brownbutton.grid(row=0, column=4, sticky=S, pady=2)

        #print the numbers vertically in column 0
        num_colorgroups = int(ceil(len(color_list)/4.0))+1
        button_list = []
        for I in range(1,num_colorgroups):
            Button(self.Top_Label_Root,text=I,command=lambda I=I: self.TriggerPlot(COL=col,NUM=I),width=2).grid(row=I, column=0, sticky=E, padx=2)

        #print text boxes for entry in the matrix
        for i in range(0,len(color_list)):
            textbox_list.append(Text(self.Top_Label_Root,height=1,width=25,borderwidth=2,relief=SUNKEN))
            textbox_list[i].bind("<Tab>", self.focus_next_window)
            textbox_list[i].grid(row=int(floor((i/4)+1)),column=(int(i%4)+1))

        #create reference water label and entry widget for drift correction
        self.ref_label = Label(self.Bottom_Label_Root,text='Reference standard for drift correction:')
        self.ref_label.grid(row=1,column=0,sticky='NESW')
        self.ref_entry = Text(self.Bottom_Label_Root,height=1,width=25,borderwidth=2,relief=SUNKEN)
        self.ref_entry.grid(row=1,column=1,sticky='NESW')
        #create enter button for the Label_Root
        self.highliteall_button = Button(self.Bottom_Label_Root, text='Highlight all', command=lambda: self.TriggerPlot(highlight='all'), width=18)
        self.highliteall_button.grid(row=0, column=0,sticky=E,padx=2)
        self.removehighlites_button = Button(self.Bottom_Label_Root, text='Remove all highlights', command=lambda: self.TriggerPlot(), width=18)
        self.removehighlites_button.grid(row=0,column=1,sticky=W,padx=2)

        self.enter_button = Button(self.Bottom_Label_Root, text='OK', command=self.Frame2_LabelEntry, width=5)
        self.enter_button.grid(row=2, column=0,sticky=E,padx=2,pady=10)  
        self.quit_button = Button(self.Bottom_Label_Root, text='Quit', command=sys.exit, width=5)
        self.quit_button.grid(row=2,column=1,sticky=W,padx=2,pady=10)
    
    def TriggerPlot(self,highlight=None,NUM=0,COL=''):
        #creates a new f
        CreateFigure(highlight=highlight,NUMBER=NUM,COLOR=COL)
        #updates the figure widget with the new f
        figure.UpdatePlot(f)
    
    def focus_next_window(self, event):
        event.widget.tk_focusNext().focus()
        return('break')
    
    def Frame2_LabelEntry(self):
        global answer_list
        global ref_entry
        for i in range(len(answer_list['event'])):
            answer_list['event'][i] = textbox_list[i].get("1.0",'end-1c')
        ref_entry = self.ref_entry.get("1.0", 'end-1c')
        figure.destroy()
        self.Label_Root.destroy()


###GLOBAL METHODS
#following method modifies global variable f to represent the figure you intend to show
#use global variable f when creating an instance of FigureWidget to tell the instance what image to display
#also can use the class method FigureWidget.UpdatePlot(f) to change the figure on the widget
def CreateFigure(highlight=None, COLOR='', NUMBER=0):
    global a,f,num,col,color_list
    num=NUMBER
    col=COLOR
    f = plt.Figure()
    a = f.add_subplot(111)
    color_list = []
    for i in range(1,(max_group+2)):
        if i == max_group + 1:
            hold = data_inc_avg[data_inc_avg['group'] == 0]
            a.plot(hold['index'], hold['dD'], color = 'black', marker = '.', linestyle = 'None', alpha = .1) #this line plots memory effects
            continue
        if i != max_group + 1:
            hold = data_inc_avg[data_inc_avg['group'] == i]

            #plot all highlighted and thickened
            if highlight is 'all':
                if i % 4 == 1:
                    a.plot(hold['index'], hold['dD'], linewidth = 4.5, color = 'red')
                    s='red '+str(int((round(i/4))+1))
                    color_list.append(s)
                    continue
                if i % 4 == 2:
                    a.plot(hold['index'], hold['dD'], linewidth = 4.5, color = 'blue')
                    s='blue '+str(int((round(i/4))+1))
                    color_list.append(s)
                    continue
                if i % 4 == 3:
                    a.plot(hold['index'], hold['dD'], linewidth = 4.5, color = 'green')
                    s='green '+str(int((round(i/4))+1))
                    color_list.append(s)
                    continue
                if i % 4 == 0:
                    a.plot(hold['index'], hold['dD'], linewidth = 4.5, color = 'saddlebrown')
                    s='brown '+str(int(round(i/4)))
                    color_list.append(s)
                    continue

            #plot nothing thickened or highlighted
            if (COLOR is '') and (NUMBER is 0):
                if i % 4 == 1:
                    a.plot(hold['index'], hold['dD'], linewidth = 3.0, alpha = .25, color = 'red')
                    s='red '+str(int((round(i/4))+1))
                    color_list.append(s)
                    continue
                if i % 4 == 2:
                    a.plot(hold['index'], hold['dD'], linewidth = 3.0, alpha = .25, color = 'blue')
                    s='blue '+str(int((round(i/4))+1))
                    color_list.append(s)
                    continue
                if i % 4 == 3:
                    a.plot(hold['index'], hold['dD'], linewidth = 3.0, alpha = .25, color = 'green')
                    s='green '+str(int((round(i/4))+1))
                    color_list.append(s)
                    continue
                if i % 4 == 0:
                    a.plot(hold['index'], hold['dD'], linewidth = 3.0, alpha = .25, color = 'saddlebrown')
                    s='brown '+str(int(round(i/4)))
                    color_list.append(s)
                    continue

            #plot a certain color highlighted and thickened
            if (col is not '') and (num is 0):
                if i % 4 == 1:
                    if col is 'red':
                        a.plot(hold['index'], hold['dD'], linewidth = 4.5, color = 'red')
                    else:
                        a.plot(hold['index'], hold['dD'], linewidth = 3.0, alpha = .25, color = 'red')
                    s='red '+str(int((round(i/4))+1))
                    color_list.append(s)
                    continue
                if i % 4 == 2:
                    if col is 'blue':
                        a.plot(hold['index'], hold['dD'], linewidth = 4.5, color = 'blue')
                    else:
                        a.plot(hold['index'], hold['dD'], linewidth = 3.0, alpha = .25, color = 'blue')
                    s='blue '+str(int((round(i/4))+1))
                    color_list.append(s)
                    continue
                if i % 4 == 3:
                    if col is 'green':
                        a.plot(hold['index'], hold['dD'], linewidth = 4.5, color = 'green')
                    else:
                        a.plot(hold['index'], hold['dD'], linewidth = 3.0, alpha = .25, color = 'green')
                    s='green '+str(int((round(i/4))+1))
                    color_list.append(s)
                    continue
                if i % 4 == 0:
                    if col is 'brown':
                        a.plot(hold['index'], hold['dD'], linewidth = 4.5, color = 'saddlebrown')
                    else:
                        a.plot(hold['index'], hold['dD'], linewidth = 3.0, alpha = .25, color = 'saddlebrown')
                    s='brown '+str(int(round(i/4)))
                    color_list.append(s)
                    continue

            #plot a certain number highlighted and thickened
            if (col is '') and (num is not 0):
                if i in [x+((num-1)*4) for x in range(1,5)]:
                    if i % 4 == 1:
                        a.plot(hold['index'], hold['dD'], linewidth = 4.5, color = 'red')
                        s='red '+str(int((round(i/4))+1))
                        color_list.append(s)
                        continue
                    if i % 4 == 2:
                        a.plot(hold['index'], hold['dD'], linewidth = 4.5, color = 'blue')
                        s='blue '+str(int((round(i/4))+1))
                        color_list.append(s)
                        continue
                    if i % 4 == 3:
                        a.plot(hold['index'], hold['dD'], linewidth = 4.5, color = 'green')
                        s='green '+str(int((round(i/4))+1))
                        color_list.append(s)
                        continue
                    if i % 4 == 0:
                        a.plot(hold['index'], hold['dD'], linewidth = 4.5, color = 'saddlebrown')
                        s='brown '+str(int(round(i/4)))
                        color_list.append(s)
                        continue
                else:
                    if i % 4 == 1:
                        a.plot(hold['index'], hold['dD'], linewidth = 3.0, alpha = .25, color = 'red')
                        s='red '+str(int((round(i/4))+1))
                        color_list.append(s)
                        continue
                    if i % 4 == 2:
                        a.plot(hold['index'], hold['dD'], linewidth = 3.0, alpha = .25, color = 'blue')
                        s='blue '+str(int((round(i/4))+1))
                        color_list.append(s)
                        continue
                    if i % 4 == 3:
                        a.plot(hold['index'], hold['dD'], linewidth = 3.0, alpha = .25, color = 'green')
                        s='green '+str(int((round(i/4))+1))
                        color_list.append(s)
                        continue
                    if i % 4 == 0:
                        a.plot(hold['index'], hold['dD'], linewidth = 3.0, alpha = .25, color = 'saddlebrown')
                        s='brown '+str(int(round(i/4)))
                        color_list.append(s)
                        continue
            #plot a certain color/number combination as highlighted and thickened
            if (col is not '') and (num is not 0):
                if i in [x+((num-1)*4) for x in range(1,5)]:
                    if i % 4 == 1:
                        if col is 'red':
                            a.plot(hold['index'], hold['dD'], linewidth = 4.5, color = 'red')
                        else:
                            a.plot(hold['index'], hold['dD'], linewidth = 3.0, alpha = .25, color = 'red')
                        s='red '+str(int((round(i/4))+1))
                        color_list.append(s)
                        continue
                    if i % 4 == 2:
                        if col is 'blue':
                            a.plot(hold['index'], hold['dD'], linewidth = 4.5, color = 'blue')
                        else:
                            a.plot(hold['index'], hold['dD'], linewidth = 3.0, alpha = .25, color = 'blue')
                        s='blue '+str(int((round(i/4))+1))
                        color_list.append(s)
                        continue
                    if i % 4 == 3:
                        if col is 'green':
                            a.plot(hold['index'], hold['dD'], linewidth = 4.5, color = 'green')
                        else:
                            a.plot(hold['index'], hold['dD'], linewidth = 3.0, alpha = .25, color = 'green')
                        s='green '+str(int((round(i/4))+1))
                        color_list.append(s)
                        continue
                    if i % 4 == 0:
                        if col is 'brown':
                            a.plot(hold['index'], hold['dD'], linewidth = 4.5, color = 'saddlebrown')
                        else:
                            a.plot(hold['index'], hold['dD'], linewidth = 3.0, alpha = .25, color = 'saddlebrown')
                        s='brown '+str(int(round(i/4)))
                        color_list.append(s)
                        continue
                else:
                    if i % 4 == 1:
                        a.plot(hold['index'], hold['dD'], linewidth = 3.0, alpha = .25, color = 'red')
                        s='red '+str(int((round(i/4))+1))
                        color_list.append(s)
                        continue
                    if i % 4 == 2:
                        a.plot(hold['index'], hold['dD'], linewidth = 3.0, alpha = .25, color = 'blue')
                        s='blue '+str(int((round(i/4))+1))
                        color_list.append(s)
                        continue
                    if i % 4 == 3:
                        a.plot(hold['index'], hold['dD'], linewidth = 3.0, alpha = .25, color = 'green')
                        s='green '+str(int((round(i/4))+1))
                        color_list.append(s)
                        continue
                    if i % 4 == 0:
                        a.plot(hold['index'], hold['dD'], linewidth = 3.0, alpha = .25, color = 'saddlebrown')
                        s='brown '+str(int(round(i/4)))
                        color_list.append(s)
                        continue

    by = len(data_inc_avg.index)/10 # 9 (10-1) time tick marks on graph
    at = [x*by for x in range(1, 10)]
    l = []
    for i in at:
        l.append(data_inc_avg['time'][i])

    a.set_xticks(at, minor=False)
    a.set_xticklabels(l, fontdict=None, minor=False)
    a.set_xlabel('time')
    a.set_ylabel('uncalibrated delta deuterium')
    a.set_title(fo)



'''
All classes and global methods are now defined.

The following code runs the actual program 
by calling the widgets in order and assigning 
values to globa variables that need to be used 
by future widgets and code.
'''


#Run the first widget
root = Tk()
first = FirstWidget(root)
root.mainloop()

#Run the manual standard entry widget if need be
#Standard data is set here to the variable std
if first.standard_method.get() == 'man':
    root = Tk()
    ManualStdEntryWidget(root)
    root.mainloop()
elif (first.standard_method.get() == '') and (std_data == ''):
    print('\nWARNING: No standard data selected or no standard entry method choosen! The time-series \
    graph will be displayed but data synthesis is not possible with calibration standards. \n')
else:
    std = pd.read_csv(std_data)


#Prepare the data
print('Averaging by: %d' % avgby)
print('Memory Effect Value: %d' % float(memeffval))
print('Running Program on: %s' % fi)
print('Files named '+fo+' will be written out to '+dir_)
global data_inc_avg
os.chdir(home)

print("Preparing data...")

###read in the data
frames = []
for f in fi:
    filetype= f.split(".")
    if filetype[len(filetype)-1] == 'dat':
        temp = pd.read_csv(f, delim_whitespace=True)
    elif filetype[len(filetype)-1] == 'csv':
        temp = pd.read_csv(f) 
    else:
        print("ERROR: input file must either be a .csv or a .dat file")
        sys.exit()
    frames.append(temp)
master_data = pd.concat(frames, ignore_index=True)

#add time to the master data using the epoch time column
master_data['seconds'] = map(lambda e: int(time.strftime('%S', time.localtime(e))), master_data['EPOCH_TIME'])
master_data['hourminutes'] = map(lambda e: time.strftime('%H:%M', time.localtime(e)), master_data['EPOCH_TIME'])

nrows = len(master_data.axes[0])
ncols = len(master_data.axes[1])
delta_18O = master_data['Delta_18_16']

data_inc_avg = pd.DataFrame({'time' : pd.Series([NaN]), 'd18O' : pd.Series([NaN]), 'dD' : pd.Series([NaN]), 'H2O' : pd.Series([NaN])})
#if useavgby is true, avg by avgby
if useavgby:
    for i in range(0, nrows-1):
        if i == 0:
            start = i
            continue
        #find what second we are at in the current iteration of the for loop    
        s = master_data['seconds'][i]
        #if we are at a seconds value equal to 0 mod avgby, average the preceding rows
        if s % avgby != 0:
            continue
        elif s % avgby == 0:
            #case for if we are at the last row
            if i == nrows - 1:
                temp = pd.DataFrame({'time' : pd.Series([master_data['hourminutes'][i]]),
                    'd18O' : pd.Series([master_data['Delta_18_16'][start:i].mean()]), 
                    'dD' : pd.Series([master_data['Delta_D_H'][start:i].mean()]),
                    'H2O' : pd.Series([master_data['H2O'][start:i].mean()])})
                data_inc_avg = data_inc_avg.append(temp, ignore_index = True)
                break
            eptime_next = round(master_data['EPOCH_TIME'][i+1])
            s_next = int(time.strftime('%S', time.localtime(eptime_next)))
            #case for if the next line is also 0 mod avgby
            if s_next % avgby == 0:
                continue
            #case if the next line is not 0 mod avgby
            if s_next % avgby != 0:
                temp = pd.DataFrame({'time' : pd.Series([master_data['hourminutes'][start]]),
                    'd18O' : pd.Series([master_data['Delta_18_16'][start:i].mean()]), 
                    'dD' : pd.Series([master_data['Delta_D_H'][start:i].mean()]),
                    'H2O' : pd.Series([master_data['H2O'][start:i].mean()])})
                data_inc_avg = data_inc_avg.append(temp, ignore_index = True)
                start = i + 1
                continue
    #delete the first row of NaN's
    data_inc_avg = data_inc_avg.ix[1:]
    data_inc_avg['index'] = list(range(1, len(data_inc_avg.axes[0])+1))
#if useavgby is false, then just use the master data as data_inc_avg
else:
    data_inc_avg = data_inc_avg.append(pd.DataFrame({'time' : pd.Series(master_data['hourminutes']), \
        'd18O' : pd.Series(master_data['Delta_18_16']), \
        'dD' : pd.Series(master_data['Delta_D_H']), \
        'H2O' : pd.Series(master_data['H2O'])}), ignore_index = True)
    data_inc_avg = data_inc_avg.ix[1:]
    data_inc_avg['index'] = list(range(1, len(data_inc_avg.axes[0])+1))

#create event column and enter in 'mem' for wherever the change is > memeffval
mem_series = ['']
for i in data_inc_avg['index']:
    if i == 1:
        continue
    if abs(data_inc_avg['dD'][i] - data_inc_avg['dD'][i-1]) > memeffval:
        mem_series.append('mem')
    else:
        mem_series.append('')
data_inc_avg['event'] = mem_series

#fill in mem gaps 
for i in data_inc_avg['index']:
    if (i == 1) or (i == 2):
        continue
    if (data_inc_avg['event'][i] == 'mem') and \
    (data_inc_avg['event'][i-2] == 'mem') and \
    (abs(data_inc_avg['dD'][i] - data_inc_avg['dD'][i-1]) > (memeffval - .15)):
        data_inc_avg['event'][i-1] = 'mem'
        continue

#give group numbers based on separation by mems
group = []
for i in data_inc_avg['index']:
    if i == 1:
        tracker = 1
    if i == len(data_inc_avg['event']):
        if data_inc_avg['event'][i] == 'mem':
            group.append(0)
            break
        if data_inc_avg['event'][i] != 'mem':
            group.append(tracker)
            break
    if data_inc_avg['event'][i] != 'mem':
        group.append(tracker)
        continue
    if data_inc_avg['event'][i] == 'mem':
        group.append(0)
        if data_inc_avg['event'][i+1] == 'mem':
            continue
        if data_inc_avg['event'][i+1] != 'mem':
            tracker = tracker + 1
            continue
data_inc_avg['group'] = group
max_group = max(data_inc_avg['group'])
#add col_group for later matching
col_group = []
for i in data_inc_avg['group']:
    if i!=0:
        if i%4==1:
            col_group.append('red '+str(int((round(i/4))+1)))
        if i%4==2:
            col_group.append('blue '+str(int((round(i/4))+1)))
        if i%4==3:
            col_group.append('green '+str(int((round(i/4))+1)))
        if i%4==0:
            col_group.append('brown '+str(int(round(i/4))))
    if i==0:
        col_group.append('mem')
data_inc_avg['col_group'] = col_group

#create the initial figure with no highlights or thickens
#this sets the initial value for f
CreateFigure()

#creates the label widget
#these two widgets are canceled by buttons inside the widgets
root = Tk()
label = LabelWidget(root)
#creates the figure widget inside the mainloop of the label widget
root2 = Tk()

#initializes a FigureWidget instance with the global variable f, created by CreateFigure() method above
figure = FigureWidget(root2, f)

root2.mainloop() #inner loop = figure
root.mainloop() #outter loop = labels

'''
At this point, all tkinter widgets are closed and the program just has to 
print out the LMWL and time series plot, drift correct and calibrate the data,
and the export the new data to a csv file in the working directory
'''
#prints out the time series plot
CreateFigure(highlight='all')
c=FigureCanvas(f)
c.print_figure(dir_+fo+'.pdf')

event = []
for i in data_inc_avg['col_group']:
    if i == 'mem':
        event.append('mem')
        continue
    if i != 'mem':
        if vers == 2:
            event.append(str([answer_list['event'][j] for j in range(len(answer_list['color_group'])) if answer_list['color_group'][j] == i])[3:-2])
        elif vers == 3:
            event.append(str([answer_list['event'][j] for j in range(len(answer_list['color_group'])) if answer_list['color_group'][j] == i])[2:-2])
data_inc_avg['event'] = event

###Drift Correction
###keep only reference water data
drift_data = data_inc_avg[data_inc_avg['event'] == ref_entry]
###get rid of the first and last 10 minutes
drift_data = drift_data[21:-20]
###keep the remaining first and last 10% of the data
keep = int(max(drift_data['index'])*.1)
keep_d18O = [np.mean(drift_data['d18O'][0:keep]), np.mean(drift_data['d18O'][-keep:max(drift_data['index'])])]
keep_dD = [np.mean(drift_data['dD'][0:keep]), np.mean(drift_data['dD'][-keep:max(drift_data['index'])])]
drift_d18O = (keep_d18O[1]-keep_d18O[0])/max(drift_data['index'])
drift_dD = (keep_dD[1]-keep_dD[0])/max(drift_data['index'])
data_inc_avg['drift_corrected_d18O'] = np.add([i*drift_d18O for i in range(len(data_inc_avg['d18O']))], data_inc_avg['d18O'])
data_inc_avg['drift_corrected_dD'] = np.add([i*drift_dD for i in range(len(data_inc_avg['dD']))], data_inc_avg['dD'])

# data_inc_avg.to_csv(home+'/Python/files/data_inc_avg.csv')
# sys.exit()

###Calibration
grouped = data_inc_avg.groupby('event', as_index = False)
# event_means = data_inc_avg.groupby('event', as_index = False).mean()
event_means = grouped.agg(np.mean)
# event_stddev = data_inc_avg.groupby('event', as_index = False).std()
measured_stds = event_means[event_means['event'].isin(std['standard'])]
real_d18O = []
real_dD = []
for i in measured_stds['event']:
    real_d18O.append(float(std['real.d18O'][std['standard']==i]))
    real_dD.append(float(std['real.D_H'][std['standard']==i]))
###compute linear regression stats
d18O_calibration_plot = plt.plot(measured_stds['drift_corrected_d18O'], real_d18O)
dD_calibration_plot = plt.plot(measured_stds['drift_corrected_dD'], real_dD)
slope_d18O, intercept_d18O, r_value_d18O, p_value_d18O, std_err_d18O = stats.linregress(measured_stds['drift_corrected_d18O'], real_d18O)
slope_dD, intercept_dD, r_value_dD, p_value_dD, std_err_dD = stats.linregress(measured_stds['drift_corrected_dD'], real_dD)
###predict calculated values using the linear regression info
data_inc_avg['calculated_d18O'] = [slope_d18O*x + intercept_d18O for x in data_inc_avg['drift_corrected_d18O']]
data_inc_avg['calculated_dD'] = [slope_dD*x + intercept_dD for x in data_inc_avg['drift_corrected_dD']]

###Plotting LMWL and writing data
plt.cla()
plt.clf()
#first plot the LMWL data
def checkForRain(inputString):
    return bool(re.search('rain', inputString))
d = data_inc_avg    
keep = list(map(checkForRain, d['event']))
keep = [i for i in range(len(keep)) if keep[i]]
if len(keep) > 0:
    keep = d.iloc[keep,:]
    x = keep['calculated_d18O']
    y = keep['calculated_dD']
    m, b = np.polyfit(x, y, 1)
    plt.plot(x, y, '.')
    y_hat = [m*X + b for X in x]
    plt.plot(x, y_hat, '-')
    plt.ylabel('delta deuterium')
    plt.xlabel('delta 18O')
    plt.title(fo)
    plt.savefig(dir_+fo+'_LMWL.pdf')
#write out the data
data_inc_avg.to_csv(dir_+fo+'_analysis.csv')

###compute averages and standard deviations for all non-mem events
iso_aggs = grouped['d18O', 'dD'].agg([np.mean, np.std]) 
iso_aggs.to_csv(dir_+fo+'_aggregation.csv')