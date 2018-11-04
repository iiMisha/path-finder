# -*- coding: utf-8 -*-
#read_map.py


import sys
from tkinter import *
from tkinter.messagebox import *
import json
import math
#import tkMessageBox

class Dialog(Toplevel):

    def __init__(self, parent, title = None):

        Toplevel.__init__(self, parent)
        self.transient(parent)

        if title:
            self.title(title)

        self.parent = parent

        self.result = None

        body = Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        self.buttonbox()

        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))

        self.initial_focus.focus_set()

        self.wait_window(self)

    #
    # construction hooks

    def body(self, master):
        # create dialog body.  return widget that should have
        # initial focus.  this method should be overridden

        pass

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons

        box = Frame(self)

        w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    #
    # standard button semantics

    def ok(self, event=None):

        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return

        self.withdraw()
        self.update_idletasks()

        self.apply()

        self.cancel()

    def cancel(self, event=None):

        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    #
    # command hooks

    def validate(self):

        return 1 # override

    def apply(self):

        pass # override

class KPDialog(Dialog):
	isApplied = False
	def body(self, master):
		#print ('dialog')
		Label(master, text="Название КП:").grid(row=0)
		Label(master, text="Количество баллов:").grid(row=1)

		self.e1 = Entry(master)
		self.e2 = Entry(master)

		self.e1.grid(row=0, column=1)
		self.e2.grid(row=1, column=1)
		return self.e1 # initial focus

	def apply(self):
				
		self.isApplied = True
		
	def validate(self):
		self.name = self.e1.get()
		if self.name == '':
			return 0
		score = self.e2.get()
		if score == '':
			score = self.name[:-1]			
		try:
			self.score = int(score)
		except:
			return 0
		return 1
		
class DistanceDialog(Dialog):
	#distance = 0.0
	result = 0.0
	isApplied = False
	
	def __init__(self,parent,title=None,distance=0.0):
		self.distance = distance
		print (distance)
		Dialog.__init__(self,parent,title)		
	
	def body(self, master):
		#print ('dialog')		
		Label(master, text="Выделенная дистанция в точках: %f"%(self.distance)).grid(row=0,columnspan=2)
		Label(master, text="Введите эту дистанцию (в см или км)").grid(row=1)

		self.e2 = Entry(master)

		self.e2.grid(row=1, column=1)
		return self.e2 # initial focus

	def apply(self):
				
		self.isApplied = True
		
	def validate(self):
		try:
			self.result = float(self.e2.get())
		except:
			return 0
		return 1		

		
class MyScrollbar(Scrollbar):
	currentBegin = 0.0
	currentEnd = 0.0
	
	def set(self, *args):
		print ('scrollbar',args)
		self.currentBegin = args[0]
		self.currentEnd = args[1]
		Scrollbar.set(self,*args)
		#args[0] - верхняя (левая) граница скролбара
		#args[1] - низняя (правая) граница скролбара

#canvas.grid(row = 0, column = 0)



#canvas.create_image(0,0, image=photo)
def getRealCoordinate(length,scrollBegin,scrollEnd,coord):
	print (scrollBegin*length)
	return int(round(scrollBegin*length))+coord

def key(event):
	print ("pressed",event.char)
	
def leftClick(event):
	print ("button",event.x,event.y)
	d = KPDialog(root)
	if not d.isApplied:
		return
	name = d.name
	score = d.score
	
	x = getRealCoordinate(map_w,float(xscrollbar.currentBegin),float(xscrollbar.currentEnd),event.x)
	y = getRealCoordinate(map_h,float(yscrollbar.currentBegin),float(yscrollbar.currentEnd),event.y)
	print (x,y)
	points.append ((x,y,score,name)) 
	#TODO: выводить перечень занесенных точек. Определять и исключать дубли. Особенное внесение для стартовой точки.

g_firstClick = True
g_firstCoords = (0,0)
g_factor = None

def rightClick(event): #TODO перейти на realCoordinate
	global g_firstClick
	global g_firstCoords
	global g_factor
	if g_firstClick:
		g_firstCoords=(event.x,event.y)
		g_firstClick = False
	else:
		distance = math.sqrt(pow(event.x-g_firstCoords[0],2) + pow(event.y-g_firstCoords[1],2))
		print (distance)
		d = DistanceDialog(root,distance=distance)
		if not d.isApplied:
			g_firstClick = True
			g_firstCoords = (0,0)
			return
		result = d.result
		g_factor = result/distance
		text = "Дистанция на 100 точек теперь составляет %f" %(g_factor*100)
		showinfo('info',text)
		g_firstClick = True
		g_firstCoords = (0,0)
		
	
	
def getXY(event):
    #print ('started')               #проверка срабатывания
 
    getx=event.x        #координата x сохраняется в переменной getx
    gety=event.y        #y  соответственно в gety
                            #ВНИМАНИЕ координаты отсчитываются относительно ЭКРАНА.
                            #Если требуется отсчет относительно ОКНА, нужно использовать getx=event.x 
                            #для y соответственно
 
    #print('x',getx)               #контроль
    #print('y',gety)
	
usage = '''python3(!) read_map_with_canvas.py map.gif(jpg,png) outfile
'''
if __name__ == '__main__':
	if len(sys.argv)<3:
		print (usage)
		sys.exit(0)
	map_name = sys.argv[1]
	outfile = sys.argv[2]
	root=Tk()
	#root.geometry('1024x1024')
	frame = Frame(root, width=1200, height=800,bd=2, relief=SUNKEN)
	frame.grid_rowconfigure(0, weight=1)
	frame.grid_columnconfigure(0, weight=1)
	xscrollbar = MyScrollbar(frame, orient=HORIZONTAL)
	xscrollbar.grid(row=1, column=0, sticky=E+W)
	yscrollbar = MyScrollbar(frame)
	yscrollbar.grid(row=0, column=1, sticky=N+S)
	canvas = Canvas(frame, width=1200,height=800,bd=0, xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set, xscrollincrement = 10, yscrollincrement = 10)
	canvas.grid(row=0, column=0, sticky=N+S+E+W)

	File = "map_om.gif"

	photo = PhotoImage(file = map_name)
	map_h = photo.height()
	map_w = photo.width()
	canvas.create_image(0,0,image=photo, anchor="nw")
	canvas.config(scrollregion=canvas.bbox(ALL))
	xscrollbar.config(command=canvas.xview)
	yscrollbar.config(command=canvas.yview)
	frame.pack()

	canvas.bind('<Button-1>',leftClick)
	canvas.bind('<Button-3>',rightClick)
	
	points = []
	#canvas.bind('<Motion>', getXY)
	#root.bind('<Key>',key)
	root.mainloop()
	out = open(outfile,'w')
	result = {}
	result['points'] = points
	result['factor'] = g_factor
	out.write(json.dumps(result))
	out.close()
	
