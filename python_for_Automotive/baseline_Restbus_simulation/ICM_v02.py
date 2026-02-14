import threading
import time
import random
import pika
import json
from pika.exchange_type import ExchangeType
import math


ECU_Name ="ICM"    # Assign ECU Name 
Network="ACC_Vehicle_Network"  # Assign Network or db
Channel =1		       # Assign Channel
Baudrate =500000	       # Assign Baudrate
print("%s is connected with %s in Channel %d  and run @ the speed of  %d kb/s"%(ECU_Name,Network,Channel,(Baudrate/1000)))  # print ACC Module detail

ICM_Info={"ID":hex(0x120),"Tx Method":"Cyclic","Cycle Time":150,"Channel":1,"DLC":1,"Data":{"CruiseSwitchRequest":0,"BrakeSwitch1":0}}


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
    print("Received %r" % body)
        
   
    
   
#threading.Timer(int(BCM_Info["Cycle Time"])/1000.0,TransmitMsg).start()
#threading.Timer(1,ChangeVehicleSpeed).start()

threading.Thread(target=onmsg, daemon=True).start()    
TransmitMsg()
