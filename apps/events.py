from flask_socketio import SocketIO
from paho.mqtt import client as mqtt_client
from apscheduler.schedulers.background import BackgroundScheduler
import json
import ssl
import random
from flask import Flask
import requests,time
# Khởi tạo biến last_message_time với giá trị ban đầu
last_message_time = time.time()
socketio = SocketIO( Flask(__name__) ,cors_allowed_origins='*', logger=True)
client_id = f'rems-mqtt-{random.randint(0, 1000)}'
    # username = 'emqx'
    # password = 'public'
    
client = mqtt_client.Client(client_id)

#kích hoạt khi một client kết nối thành công với server
@socketio.on('connect')
def connect_event():
    print('Client connected')

# tạo một kết nối MQTT tới broker được chỉ định và thiết lập các xử lý sự kiện khi kết nối được thiết lập (hoặc thất bại). 
# Nó trả về một đối tượng mqtt_client.
def mqtt_connect(broker, ca_cert_file):
    global client 
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    port = 8883
    #Tạo một client ID động để đảm bảo tính duy nhất khi kết nối với MQTT broker.
    # Cấu hình bảo mật TLS
    client.tls_set(ca_certs = ca_cert_file, certfile=None, keyfile=None, tls_version=ssl.PROTOCOL_TLSv1_2)

    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def mqtt_subscribe(client: mqtt_client):
    # là hàm callback được gọi khi nhận được một tin nhắn từ MQTT broker. 
    # Nó chuyển đổi dữ liệu từ dạng byte thành dạng JSON và in ra chủ đề của tin nhắn.
    def on_message(client, userdata, msg):
        global last_message_time
        try:
            topic = msg.topic
            data = json.loads(str(msg.payload.decode()))
            #kiểm tra topic và chia hướng xử lí
            #Topic này xử lí khi nhận dữ liệu từ esp
            if topic == 'rems/telemetry/dev':
                last_message_time =time.time()
                print(topic)
                post_api(data)
                #đẩy dữ liệu lên front end qua 
                socketio.emit('data', data)

            #TOPIC này xử lí khi nhận dữ liệu phản hồi từ esp
            if topic == 'rems/respone/dev':
                print(topic)
                fb_value = data.get('fb')
                rp = data.get('rp')
                # Kiểm tra giá trị và thực hiện xử lý
                if fb_value is not None:
                    if fb_value == 0:
                        post_api(data)
                        socketio.emit('respone' ,data)
                    else :
                        socketio.emit('respone' ,data)
                if rp is not None:
                    if rp == 0:
                        post_api(data)
                        socketio.emit('rule', data)
                    else:
                        mes ="Tự động tắt thất bại, hãy kiểm tra lại controller"
                        socketio.emit('err',mes)
            
        except json.decoder.JSONDecodeError:
        # Nếu không thể phân tích message thành JSON, bỏ qua việc xử lý
            print("Received non-JSON message. Skipping processing.")
            return  
    # nhận tất cả các tin nhắn trên chủ đề con
    client.subscribe('rems/telemetry/dev/#')
    client.subscribe('rems/respone/dev/#')
    
    # Đặt hàm callback on_message cho sự kiện nhận tin nhắn.
    client.on_message = on_message

# kết nối và lắng nghe dữ liệu từ MQTT broker bằng cách sử dụng các hàm được định nghĩa trong mqtt_connect và mqtt_subscribe
def events_init(broker, ca_cert_file):
    client =  mqtt_connect(broker, ca_cert_file)
    mqtt_subscribe(client)
    client.loop_start()

def post_api(data):
    #Lưu dl mới nhất vào db
    import requests
    api_url1 = 'http://127.0.0.1:5000/device-state'
    headers = {'Content-Type': 'application/json'}
    response1 = requests.post(api_url1, json=data, headers=headers)
    # Kiểm tra trạng thái của yêu cầu
    if response1.status_code == 200:
        if "pir" in data or "i" in data:
            api_url2 = 'http://127.0.0.1:5000/room_status'
            response2 = requests.put(api_url2, json=data, headers=headers)
            if response2.status_code == 200:
                print('Update room status successful')
            else :
                print(f'API request failed with status code {response2.status_code}')
    else:
        print(f'API request failed with status code {response1.status_code}')

scheduler = BackgroundScheduler()

def check_connect():
    global last_message_time
    current_time = time.time()
    # Tính thời gian từ lúc nhận được tin nhắn đến thời điểm hiện tại
    time_since_last_message = current_time - last_message_time
    # Kiểm tra nếu đã quá 7 giây mà không nhận được tin nhắn
    if time_since_last_message > 7:
        data = "ESP bị mất kết nối"
        socketio.emit('message', data)