from flask import current_app
from apps.home.model import DeviceState
from flask import render_template, request, jsonify ,redirect ,url_for
from flask_socketio import emit
from datetime import datetime

def data_callback(data):
    print("da goi dc ham")
    with current_app.app_context():
    #  luu db 
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

        # Lưu từng trạng thái vào cơ sở dữ liệu
        for device_state in device_states:
            device_state.save()

        #  day len FE de show man hinh
        data_a = {
            'id_room': '1',
            'temp': 40,
            'humi': 900
        }
        emit('data', data_a, broadcast=True, namespace='/')
