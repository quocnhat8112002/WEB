from flask_socketio import SocketIO
from paho.mqtt import client as mqtt_client
import json
import random
from flask import Flask
socketio = SocketIO( Flask(__name__) ,cors_allowed_origins='*', logger=True)


@socketio.on('connect')
def connect_event():
    print('Client connected')

def mqtt_connect(broker):
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    port = 1883
    client_id = f'rems-mqtt-{random.randint(0, 1000)}'
    # username = 'emqx'
    # password = 'public'
    
    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def mqtt_subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        topic = msg.topic
        data = json.loads(str(msg.payload.decode()))
        print(topic)
        print(data)
        
        #đẩy dữ liệu lên front end qua 
        socketio.emit('data', data)

    client.subscribe('rems/telemetry/dev/#')
    client.on_message = on_message

def events_init(broker):
    client = mqtt_connect(broker)
    mqtt_subscribe(client)
    client.loop_start()


