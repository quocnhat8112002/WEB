from flask_socketio import SocketIO
from paho.mqtt import client as mqtt_client
import json
import random
from flask import Flask

socketio = SocketIO( Flask(__name__) ,cors_allowed_origins='*', logger=True)

#kích hoạt khi một client kết nối thành công với server
@socketio.on('connect')
def connect_event():
    print('Client connected')

# tạo một kết nối MQTT tới broker được chỉ định và thiết lập các xử lý sự kiện khi kết nối được thiết lập (hoặc thất bại). 
# Nó trả về một đối tượng mqtt_client.
def mqtt_connect(broker):
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    port = 1883
    #Tạo một client ID động để đảm bảo tính duy nhất khi kết nối với MQTT broker.
    client_id = f'rems-mqtt-{random.randint(0, 1000)}'
    # username = 'emqx'
    # password = 'public'
    
    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def mqtt_subscribe(client: mqtt_client):
    # là hàm callback được gọi khi nhận được một tin nhắn từ MQTT broker. 
    # Nó chuyển đổi dữ liệu từ dạng byte thành dạng JSON và in ra chủ đề của tin nhắn.
    def on_message(client, userdata, msg):
        topic = msg.topic
        data = json.loads(str(msg.payload.decode()))
        print(topic)
        #Lưu dl mới nhất vào db
        import requests
        # Gọi API /device-state
        api_url = 'http://127.0.0.1:5000/device-state'
        headers = {'Content-Type': 'application/json'}
        # Thực hiện yêu cầu POST
        response = requests.post(api_url, json=data, headers=headers)
        # Kiểm tra trạng thái của yêu cầu
        if response.status_code == 200:
            print('API request successful')
            #đẩy dữ liệu lên front end qua 
            socketio.emit('data', data)
        else:
            print(f'API request failed with status code {response.status_code}')
    # nhận tất cả các tin nhắn trên chủ đề con
    client.subscribe('rems/telemetry/dev/#')
    # Đặt hàm callback on_message cho sự kiện nhận tin nhắn.
    client.on_message = on_message

# kết nối và lắng nghe dữ liệu từ MQTT broker bằng cách sử dụng các hàm được định nghĩa trong mqtt_connect và mqtt_subscribe
def events_init(broker):
    client = mqtt_connect(broker)
    mqtt_subscribe(client)
    client.loop_start()

@socketio.on('client_request')
def sendRequest(data):
    
    print("da gửi đến esp")
    print(data)
    # id = data.get('id')
    # switchId = data.get('switchId')
    # value = data.get('value')    
    # # Xử lý yêu cầu từ client và gửi phản hồi
    # # Gửi thông điệp tới ESP8266 qua MQTT 
    # mqtt_command = {"id": id, f"sw{switchId}": (value)}
    # mqtt_client.publish('rems/telemetry/dev/#', json.dumps(mqtt_command))
    #cần thêm điều kiện là esp8266 phải phản hồi thì mới đẩy lên data
    print("da gửi đến esp")
    socketio.emit('server_response', {'response': 'Request processed successfully'})

