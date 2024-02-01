from flask_socketio import SocketIO
from paho.mqtt import client as mqtt_client
import json
import random
from flask import app
from datetime import datetime

socketio = SocketIO(cors_allowed_origins='*', logger=True)

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
        # Đưa dữ liệu vào hàng đợi
        data_callback(data)
        # TODO: 
        # Lấy dl mới nhất từ db lên lưu vào latest_data
        # latest_data = {
        #     'id_room': '1',
        #     'temp': 40,
        #     'humi': 100
        # }
        #đẩy dữ liệu lên front end qua 
        # socketio.emit('data', latest_data)
        socketio.emit('data', data)

    client.subscribe('rems/telemetry/dev/#')
    client.on_message = on_message

def events_init(broker):
    client = mqtt_connect(broker)
    mqtt_subscribe(client)
    client.loop_start()


#######################################################
def data_callback(data):
    print("da goi dc ham")
    #  luu db 
    with app.app_context():
        from apps.home.model import DeviceState
        from apps import db
        device_id=data['id'] 
        time_stamp= datetime.now()
        device_states = []

        # Kiểm tra từng trường hợp và thêm vào danh sách trạng thái
        if 'pir' in data:
            device_states.append(DeviceState(device_id=device_id, time_stamp=time_stamp, resource='pir', value=data['pir']))

        if 'temp' in data:
            device_states.append(DeviceState(device_id=device_id, time_stamp=time_stamp, resource='temp', value=data['temp']))

        if 'humi' in data:
            device_states.append(DeviceState(device_id=device_id, time_stamp=time_stamp, resource='humi', value=data['humi']))
        print("da tach duoc du lieu")
        # Lưu từng trạng thái vào cơ sở dữ liệu
        for device_state in device_states:
            db.session.add(device_state)

        db.session.commit()
        #  day len FE de show man hinh
            
   
