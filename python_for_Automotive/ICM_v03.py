import threading
import time
import random
import pika
import json
from pika.exchange_type import ExchangeType
from tkinter import *
from PIL import ImageTk, Image,ImageDraw
import math
from tkinter import ttk
from tkinter import font as tkFont

ECU_Name ="ICM"    # Assign ECU Name 
Network="ACC_Vehicle_Network"  # Assign Network or db
Channel =1		       # Assign Channel
Baudrate =500000	       # Assign Baudrate
print("%s is connected with %s in Channel %d  and run @ the speed of  %d kb/s"%(ECU_Name,Network,Channel,(Baudrate/1000)))  # print ACC Module detail

ICM_Info={"ID":hex(0x120),"Tx Method":"Cyclic","Cycle Time":150,"Channel":1,"DLC":1,"Data":{"CruiseSwitchRequest":0,"BrakeSwitch1":0}}
global vs_prv
vs_prv=0
global onoffbtn_status
onoffbtn_status=0
global txt_id
txt_id=0
global dinfo_prv
dinfo_prv=0
global bsw_count
bsw_count=0




def onoff_pressed(state):
    global onoffbtn_status
    if onoffbtn_status:
        ICM_Info["Data"]["CruiseSwitchRequest"]=0
        onoffbtn_status=0
    else:
        ICM_Info["Data"]["CruiseSwitchRequest"]=1
        onoffbtn_status=1
def released(state):
    ICM_Info["Data"]["CruiseSwitchRequest"]=7
    
def setbtn_pressed(state):
    ICM_Info["Data"]["CruiseSwitchRequest"]=2
    
def coastbtn_pressed(state):
    ICM_Info["Data"]["CruiseSwitchRequest"]=3

def resumebtn_pressed(state):
    ICM_Info["Data"]["CruiseSwitchRequest"]=4
def tplus_pressed(state):
    ICM_Info["Data"]["CruiseSwitchRequest"]=5
def tminus_pressed(state):
    ICM_Info["Data"]["CruiseSwitchRequest"]=6

def bsw1_pressed(state):
    ICM_Info["Data"]["BrakeSwitch1"]=1

def bsw1_released(state):
    ICM_Info["Data"]["BrakeSwitch1"]=0



    
    
def CruiseSwitches():
    
    global window_count   # count cruise GUI instance
    if window_count<1:    # check no. of window is onely 1
        cs = Toplevel(root) # create a window for cruise switches
        global cimg         # image object to store cruise sw image
        cs.title("Cruise Buttons")    # giving title to cruise window
        cs.config(width=500, height=370)  # give dimension for cruise sw window
        canvas_width, canvas_height = 450, 300  # create variables to hold size of canvas
        
        
        #global canvas  # set canvas object to global
        canvas2 = Canvas(cs, width=canvas_width, height=canvas_height)  # create a canvas
        canvas2.pack() # pack the canvas to screen
        canvas2.create_image(20, 20, anchor=NW, image=cimg)  # creat cruise sw img in Canvas
        Ar14 = tkFont.Font(family='Arial', size=14, weight=tkFont.BOLD) # create a font variable to use
        onoff = Button(cs, text="ON/Off",bg="#454346",fg="White",width=5,height=1,font=Ar14,activebackground="Green") # create a button for on/ off
        onoff.bind("<ButtonPress-1>",onoff_pressed,add="+") # attach the event procedure for button press 
        onoff.bind("<ButtonRelease-1>",released,add="+")  # attach even procedure for button release
        onoff.pack() # pack the button to GUI
        onoff.place(x=240, y=78) # define the location to place
        
        setbtn = Button(cs, text="SET",bg="#454346",fg="White",width=3,height=1,font=Ar14,activebackground="Green") # create Set button
        setbtn.bind("<ButtonPress-1>",setbtn_pressed,add="+") # attach event procedure for button press
        setbtn.bind("<ButtonRelease-1>",released,add="+")   # attached event procedure for button release
        #setbtn.wm_attributes('-transparentcolor', '#ab23ff')
        #def callback(e):
            #canvas = e.widget
           # x = e.x
           # y = e.y
   
            #print("Pointer is currently at %d, %d" %(x,y))
        #cs.bind('<Motion>',callback)
        setbtn.pack() # pack it to GUI
        setbtn.place(x=223, y=225) # define button location
        
        coastbtn= Button(cs, text="CST",bg="#454346",fg="White",width=4,height=1,font=Ar14,activebackground="Green")
        coastbtn.bind("<ButtonPress-1>",coastbtn_pressed,add="+")
        coastbtn.bind("<ButtonRelease-1>",released,add="+") 
        coastbtn.pack()
        coastbtn.place(x=145, y=77)

        resumebtn = Button(cs, text="RES",bg="#454346",fg="White",width=4,height=1,font=Ar14,activebackground="Green")
        resumebtn.bind("<ButtonPress-1>",resumebtn_pressed,add="+")
        resumebtn.bind("<ButtonRelease-1>",released,add="+") 
        resumebtn.pack()
        resumebtn.place(x=176, y=164)

        tplus = Button(cs, text="T+",bg="#454346",fg="White",width=3,height=1,font=Ar14,activebackground="Green")
        tplus.bind("<ButtonPress-1>",tplus_pressed,add="+")
        tplus.bind("<ButtonRelease-1>",released,add="+") 
        tplus.pack()
        tplus.place(x=310, y=223)
        
        tminus = Button(cs, text="T-",bg="#6C6C6C",fg="White",width=3,height=1,font=Ar14,activebackground="Green")
        tminus.bind("<ButtonPress-1>",tminus_pressed,add="+")
        tminus.bind("<ButtonRelease-1>",released,add="+") 
        tminus.pack()
        tminus.place(x=290, y=160)
        
        window_count+=1   # increment the window count

    
def ICMdashboard():
    
    global root # set root as global
    root=Tk()  # to create a window
    root.geometry("700x600")   # Set the size of the window
    canvas_width, canvas_height = 700, 600  # create variables to hold size of canvas
    
    img = Image.open("meter.png")    # read image from the file to a object
    #resized_image= img.resize((700,600), Image.Resampling.LANCZOS)
    img = ImageTk.PhotoImage(img)   # create Tk image object from the image object
    global canvas  # set canvas object to global
    canvas = Canvas(root, width=canvas_width, height=canvas_height)  # create a canvas
    canvas.pack() # pack the canvas to screen
    canvas.create_image(20, 20, anchor=NW, image=img)  # embed the image on the canvas
    global txt_id
    txt_id=canvas.create_text(350,250, text="ACC Off", fill="#77FF63", font=('Arial 15 bold'))
    global x  # create global varibale x
    x=560   # x - coordinate of needle
    global y # create a global variable y
    y=260   # y - coordinate of needle
    global endy  
    endy = y + 115 * math.sin(math.radians(87)) # find angular end y coordinate
    global endx
    endx = x + 115 * math.cos(math.radians(87)) # find angular end x coordinate
    global lineid  # create global line id varible
    canvas.create_oval(x-20,y-20,x+20,y+20,fill="Red")  # draw a red circle at the centre
    canvas.create_oval(x-10,y-10,x+10,y+10,fill="Gray") # draw a gray inner circle at the centre
    lineid=canvas.create_line(x,y, endx,endy,fill="Red",arrow="last",smooth=True,width=5) # draw the needle
    #points = [500, 230, 430, 260]
    #250, 450, 285,450,265, 530, 220, 500, 230]
   # points = [100, 140, 110, 110, 140, 100, 110, 90, 100, 60, 90, 90, 60, 100, 90, 110]
    #canvas.create_polygon(points, outline='green', fill='yellow', width=3)
    global window_count
    window_count=0
    global cimg
    cimg = Image.open("cruiseSw1.png") 
    cimg = ImageTk.PhotoImage(cimg) # create Cruise Switches Image to display in the GUI
    
    # creating button to open Cruise Switches GUI
    button_open = ttk.Button(
    root,
    text="CB",
    command=CruiseSwitches )
    button_open.place(x=600, y=550) # create a button to open Cruise switches GUI
    
    # Adding Brake Sw1 to the GUI
    bsw1 = ttk.Button(
    root,
    text="Brake SW1")
    bsw1.bind("<ButtonPress-1>",bsw1_pressed,add="+") # attach the event procedure for button press 
    bsw1.bind("<ButtonRelease-1>",bsw1_released,add="+")  # attach even procedure for button release
    bsw1.place(x=530, y=550) # create a button to open Brake switches GUI

    root.mainloop() # wait for user input
    
    
    
def TransmitMsg():
    connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    
    channel.exchange_declare(exchange='ICMExchange',exchange_type=ExchangeType.fanout)
    #channel.queue_declare(queue='',exclusive=True)
    result=json.dumps(ICM_Info)
    print("Transmitting .. %s"%result)

    channel.basic_publish(
        exchange='ICMExchange',
        routing_key='',
        body=result)
    
    
    connection.close()
    
    threading.Timer(int(ICM_Info["Cycle Time"])/1000,TransmitMsg).start()
    

def onmsg():
    connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    #channel.exchange_declare(exchange='BCMExchnage',exchange_type=ExchangeType.fanout)
    queue=channel.queue_declare(queue='',exclusive=True)
    channel.queue_bind(exchange='ECMExchange',queue=queue.method.queue)
    channel.basic_consume(
    queue=queue.method.queue, on_message_callback=callback, auto_ack=True)
    
    channel.queue_bind(exchange='ACCExchange',queue=queue.method.queue)
    channel.basic_consume(
    queue=queue.method.queue, on_message_callback=callback, auto_ack=True)
    channel.queue_bind(exchange='BCMExchange',queue=queue.method.queue)
    channel.basic_consume(
    queue=queue.method.queue, on_message_callback=callback, auto_ack=True)
    
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
    #threading.Timer(0.001,onmsg).start()
    
def callback(ch, method, properties, body):
    global root
    global canvas
    global endy
    global endx
    global vs_prv
    global x
    global y
    global lineid
    global txt_id
    global dinfo_prv
    #print(body)
    res = json.loads(body) # convert string to dictionary
    if int(res["ID"],0)== 0x110:
        ang=(1.33*int(res["Data"]["VehicleSpeed"])+85)%360
        endy   = y + 115 * math.sin(math.radians(ang))
        endx   = x + 115 * math.cos(math.radians(ang))
        if int(vs_prv) != int(res["Data"]["VehicleSpeed"]):
            canvas.delete(lineid)
            lineid=canvas.create_line(x,y, endx,endy,fill="Red",arrow="last",smooth=True,width=5)
            vs_prv=int(res["Data"]["VehicleSpeed"])
    
    
    if int(res["ID"],0)==0x230:
        match int(res["Data"]["ACCDriverInfo"]):
            case 0:
                if dinfo_prv !=int(res["Data"]["ACCDriverInfo"]):
                    canvas.delete(txt_id)
                    txt_id=canvas.create_text(350,250, text="ACC Off", fill="#77FF63", font=('Arial 15 bold'))
            case 1:
                if dinfo_prv !=int(res["Data"]["ACCDriverInfo"]):
                    canvas.delete(txt_id)
                    txt_id=canvas.create_text(350,250, text="ACC ON", fill="#77FF63", font=('Arial 15 bold'))
            case 2:
                if dinfo_prv !=int(res["Data"]["ACCDriverInfo"]):
                    canvas.delete(txt_id)
                    txt_id=canvas.create_text(350,250, text="ACC Standby", fill="#77FF63", font=('Arial 15 bold'))
            case 3:
                if dinfo_prv !=int(res["Data"]["ACCDriverInfo"]):
                    canvas.delete(txt_id)
                    txt_id=canvas.create_text(350,250, text="ACC Active", fill="#77FF63", font=('Arial 15 bold'))
            case 4:
                if dinfo_prv !=int(res["Data"]["ACCDriverInfo"]):
                    canvas.delete(txt_id)
                    txt_id=canvas.create_text(350,250, text="Driver\nIntervention\nRequired", fill="#77FF63", font=('Arial 15 bold'))
                    #canvas.itemconfig(txt_id, text="ACC Active")
        
        dinfo_prv=int(res["Data"]["ACCDriverInfo"])
        
        
   
    
   
#threading.Timer(int(BCM_Info["Cycle Time"])/1000.0,TransmitMsg).start()
#threading.Timer(1,ChangeVehicleSpeed).start()

    
TransmitMsg()
threading.Thread(target=ICMdashboard).start()
onmsg()