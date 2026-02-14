import threading
import time
import random
import pika
import json
from pika.exchange_type import ExchangeType
from tkinter import *
from PIL import ImageTk, Image,ImageDraw
import turtle

ECU_Name ="BCM"    # Assign ECU Name 
Network="ACC_Vehicle_Network"  # Assign Network or db
Channel =1		       # Assign Channel
Baudrate =500000	       # Assign Baudrate
print("%s is connected with %s in Channel %d  and run @ the speed of  %d kb/s"%(ECU_Name,Network,Channel,(Baudrate/1000)))  # print ACC Module detail

BCM_Info={"ID":hex(0x110),"Tx Method":"Cyclic","Cycle Time":250,"Channel":1,"DLC":1,"Data":{"VehicleSpeed":0}}
#Period=0.25
SpeedSamples=[]
index=0;
global Speedindex
Speedindex=0

global veh_free_time
veh_free_time=0
while index in range(0,10):
    SpeedSamples.append(random.randint(0,250))
    index+=1

def setVehicleSpeed(v):
    BCM_Info["Data"]["VehicleSpeed"]=v
def VehicleCtrl():
    global horizantal
    root=Tk()  # to create a window
    root.title("BCM")
    root.geometry("700x200")   # set the dimension for window
    horizantal=Scale(root,label="Vehicle Speed",from_=0,to=360,orient=HORIZONTAL,width=20,length=500,tickinterval=50,command=setVehicleSpeed,troughcolor="Black",sliderlength=20,highlightcolor="Red",cursor="bottom_side",activebackground="Green",bg="Blue",bd =10)
    horizantal.pack()
    
    #img.show()
    #my_pen = turtle.Turtle()
    #my_pen.color("orange")
    #my_pen.fd(100)
    root.mainloop()
    
     
    
def ChangeVehicleSpeed():
    global Speedindex
    BCM_Info["Data"]["VehicleSpeed"]=SpeedSamples[Speedindex]
    Speedindex=(Speedindex+1)%10

def TransmitMsg():
    connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    
    channel.exchange_declare(exchange='BCMExchange',exchange_type=ExchangeType.fanout)
    #channel.queue_declare(queue='',exclusive=True)
    result=json.dumps(BCM_Info)
    print("Transmitting .. %s"%result)

    channel.basic_publish(
        exchange='BCMExchange',
        routing_key='',
        body=result)
    
    #channel.queue_declare(queue='',exclusive=True)
    result=json.dumps(BCM_Info)
    #print("Transmitting .. %s"%result)

    #channel.basic_publish(
     #   exchange='',
     #   routing_key='BCMQ',
     #   body=result)

    connection.close()
    # print(BCM_Info)
    threading.Timer(int(BCM_Info["Cycle Time"])/1000,TransmitMsg).start()
    #threading.Timer(1,ChangeVehicleSpeed).start()

def onmsg():
    connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    #channel.exchange_declare(exchange='ICMExchange',exchange_type=ExchangeType.fanout)
    queue=channel.queue_declare(queue='',exclusive=True)
    channel.queue_bind(exchange='ECMExchange',queue=queue.method.queue)
    channel.basic_consume(
    queue=queue.method.queue, on_message_callback=callback, auto_ack=True)
    channel.queue_bind(exchange='ACCExchange',queue=queue.method.queue)
    channel.basic_consume(
    queue=queue.method.queue, on_message_callback=callback, auto_ack=True)
    channel.queue_bind(exchange='ICMExchange',queue=queue.method.queue)
    channel.basic_consume(
    queue=queue.method.queue, on_message_callback=callback, auto_ack=True)
    
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
    #threading.Timer(0.001,onmsg).start()
    
def callback(ch, method, properties, body):
   print("Received %r" % body)    
            
    

TransmitMsg()
threading.Thread(target=VehicleCtrl).start()


 