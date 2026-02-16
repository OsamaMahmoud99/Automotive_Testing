# ACC Module Details
import pika
import threading
import json
from pika.exchange_type import ExchangeType
from tkinter import *
from PIL import ImageTk, Image,ImageDraw
import tkinter as tk
from tkinter import ttk
import math
import random
import csv
ECU_Name ="ACC"    # Assign ECU Name 
Network="ACC_Vehicle_Network"  # Assign Network or db
Channel =1		       # Assign Channel
Baudrate =500000	       # Assign Baudrate
print("%s is connected with %s in Channel %d  and run @ the speed of  %d kb/s"%(ECU_Name,Network,Channel,(Baudrate/1000)))  # print ACC Module details

ACC_Info={"ID":hex(0x230),"Tx Method":"Cyclic","Cycle Time":120,"Channel":1,"DLC":3,"Data":{"ACCDriverInfo":0,"ACCState":0,"BrakeDecelReq":0,"TargetSpeed":0}}
global ACCState
ACCState=0
              
def TransmitMsg():
    connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    #channel.queue_declare(queue='ACCQ')
    channel.exchange_declare(exchange='ACCExchange',exchange_type=ExchangeType.fanout)
    result=json.dumps(ACC_Info)
    print("Transmitting .. %s"%result)

    channel.basic_publish(
        exchange='ACCExchange',
        routing_key='',
        body=result)

    connection.close()
    # print(BCM_Info)
    threading.Timer(int(ACC_Info["Cycle Time"])/1000,TransmitMsg).start()
    
    
def onmsg():
    connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    # ALWAYS declare exchanges
    channel.exchange_declare(exchange='ICMExchange', exchange_type=ExchangeType.fanout)
    channel.exchange_declare(exchange='BCMExchange', exchange_type=ExchangeType.fanout)
    channel.exchange_declare(exchange='ECMExchange', exchange_type=ExchangeType.fanout)
 
    # Create queue
    queue = channel.queue_declare(queue='', exclusive=True)

    # Bind all exchanges
    channel.queue_bind(exchange='ICMExchange', queue=queue.method.queue)
    channel.queue_bind(exchange='BCMExchange', queue=queue.method.queue)
    channel.queue_bind(exchange='ECMExchange', queue=queue.method.queue)

    # ONE consume only
    channel.basic_consume(
        queue=queue.method.queue,
        on_message_callback=callback,
        auto_ack=True
    )

    print(' [*] Waiting for messages...')
    channel.start_consuming()


def callback(ch, method, properties, body):
   global ACCState
   #print("Received %r" % body)
   res = json.loads(body)
   if int(res["ID"], 0)==0x120 :
        match int(res["Data"]["CruiseSwitchRequest"]) :
            case 0:
                ACCState=0
                ACC_Info["Data"]["ACCState"]=0
                ACC_Info["Data"]["ACCDriverInfo"]=0
            case 1: 
                if ACCState==0:
                    ACCState=2
                    ACC_Info["Data"]["ACCState"]=2 
                    ACC_Info["Data"]["ACCDriverInfo"]=2
            case 2: 
                if ACCState==2:
                    ACCState=3
                    ACC_Info["Data"]["ACCState"]=3
                    ACC_Info["Data"]["ACCDriverInfo"]=3
            case 3:
                ACC_Info["Data"]["ACCState"]=2
                ACC_Info["Data"]["ACCDriverInfo"]=2
            case 4:
                if ACCState==2:
                    ACC_Info["Data"]["ACCState"]=3
                    ACC_Info["Data"]["ACCDriverInfo"]=3
            case 5: 
                ACC_Info["Data"]["ACCState"]=3
                ACC_Info["Data"]["ACCDriverInfo"]=3
            case 6: 
                ACC_Info["Data"]["ACCState"]=3
                ACC_Info["Data"]["ACCDriverInfo"]=3
                  
        if res["Data"]["BrakeSwitch1"]:
                ACCState=2
                ACC_Info["Data"]["ACCState"]=2
                ACC_Info["Data"]["ACCDriverInfo"]=2
                

TransmitMsg()
onmsg()