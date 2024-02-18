# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from operator import and_
from apps.home import blueprint
from flask import render_template, request, jsonify ,redirect ,url_for
from flask_login import login_required
from jinja2 import TemplateNotFound

from apps.home.model import Sales ,Room ,Device ,DeviceState
from flask_socketio import emit
from sqlalchemy.sql import func ,desc
from apps import db
from datetime import datetime


@blueprint.route('/index', methods=['GET'])
@login_required

def index():
    query = db.session.query(func.count(Sales.product), func.count(Sales.product).filter(Sales.status == 'Completed'))
    sales = query.first()

    rooms = Room.query.all()
    room_list = [{'id': room.id, 'name': room.name ,'description': room.description} for room in rooms]
    print(room_list)
    
    return render_template('home/index.html', segment='index', sales=sales ,room_list=room_list)



@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:

        if not template.endswith('.html'):
            template += '.html'
        # Detect the current page
        segment = get_segment(request)
        

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500

@blueprint.route('/edit_room.html/<int:room_id>', methods=['GET'])
@login_required
def edit_room(room_id):
    # Thực hiện các thao tác cần thiết để lấy thông tin phòng với room_id từ cơ sở dữ liệu

    # Chuyển thông tin phòng tới trang chỉnh sửa
    return render_template("home/edit_room.html", room_id=room_id)

@blueprint.route('/room_control.html', methods=['GET'])
@login_required
def room_control():
    room_id = request.args.get('room_id')
    if room_id is not None:
        # Xử lý khi có giá trị room_id
        return render_template('home/room_control.html', room_id=room_id)
    else:
        # Xử lý khi không có giá trị room_id
        return "Missing room_id parameter."

# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None


@blueprint.route('/sales', methods=['POST'])
def add_sale():
    data = request.get_json()
    print(data)
    sale = Sales(product=data['product'], amount=data['amount'], status=data['status'])
    sale.save()

    query = db.session.query(func.count(Sales.product), func.count(Sales.product).filter(Sales.status == 'Completed'))
    result = query.first()
    data = {'total-sales': result[0], 'sales-completed': result[1]},
    emit('data', data, broadcast=True, namespace='/')
    return jsonify(data, 200)

#GET ROOM
####################################################################
@blueprint.route('/room/list', methods=['GET'])
def get_all_room():
    rooms = Room.query.all()
    room_list = [{'id': room.id, 'name': room.name ,'description': room.description} for room in rooms]
    return jsonify(room_list)

@blueprint.route('/room/list/<int:room_id>', methods=['GET'])
def get_room_by_id(room_id):
    room = Room.query.get(room_id)
    if room:
        return jsonify({'id': room.id, 'name': room.name ,'description': room.description})
    else:
        return jsonify({'error': 'Room not found'}), 404



@blueprint.route('/edit_room/<int:room_id>', methods=['PUT'])
@login_required

def update_room_by_id(room_id):
    room = Room.query.get(room_id)
    if not room:
        return jsonify({'error': 'Item not found'}), 404
    else:
        data = request.get_json()
        print(data)
        room.name = data['name']
        room.description = data['description']
        room.save()
        return jsonify(data, 200)
    
@blueprint.route('/add_room', methods=['POST'])
def add_room():
    data = request.form.to_dict()
    print(data)
    room = Room(name=data['name'], description=data['description'])
    print("abc")
    room.save()
    return jsonify(data, 200)

@blueprint.route('/room/<int:room_id>', methods=['DELETE'])
def delete_room_by_id(room_id):
    room = Room.query.get(room_id)
    if room:
        db.session.delete(room)
        db.session.commit()
        return "Room Deleted"
    else:
        return jsonify({'error': 'Room not found'}), 404

# XỬ LÍ TẤT CẢ LIÊN QUAN ĐẾN DEVICE
###############################################################################
# tìm giá trị của sw1, sw2 theo room_id và kiểu là controller mới nh
@blueprint.route('/device/<int:room_id>/get_by_type', methods=['GET'])
def get_devices(room_id):
    devices = Device.query.filter_by(type='controller', room_id=room_id).all()
    device_list = []
    for device in devices:
        device_state_sw1 = DeviceState.query.filter_by(device_id=device.id, resource='sw1').order_by(desc(DeviceState.time_stamp)).first()
        device_state_sw2 = DeviceState.query.filter_by(device_id=device.id, resource='sw2').order_by(desc(DeviceState.time_stamp)).first()

        device_list.append({
            'id': device.id,
            'time_stamp_sw1': device_state_sw1.time_stamp if device_state_sw1 else None,
            'value': device_state_sw1.value if device_state_sw1 else None,
            'resource': 'sw1',
        })
        device_list.append({
            'id': device.id,
            'time_stamp_sw2': device_state_sw2.time_stamp if device_state_sw2 else None,
            'value': device_state_sw2.value if device_state_sw2 else None,
            'resource': 'sw2',
        })

    return jsonify(device_list)


@blueprint.route('/device', methods=['POST'])
def add_device():
    print("acb")
    data = request.get_json()
    print(data)
    id = data['id']
    room_id=data['room_id'] 
    name=data.get('name','')
    type=data.get('type','')
    description=data.get('description','')
    create_time= datetime.now()
    update_time = datetime.now()
    info = data.get('info', "")
    # if 'name' in data:
    #     device['name'] = data['name']
    device = Device(id= id ,room_id=room_id, name=name, type=type, description=description ,update_time=update_time ,create_time=create_time, info=info)
    device.save()
    return jsonify(data, 200)



@blueprint.route('/add_device.html', methods=['GET'])
@login_required
def get_room_id():
    room_id = request.args.get('room_id')
    if room_id is not None:
        # Xử lý khi có giá trị room_id
        return render_template('home/add_device.html', room_id=room_id)
    else:
        # Xử lý khi không có giá trị room_id
        return "Missing room_id parameter."


@blueprint.route('/device/list', methods=['GET'])
def get_all_device():
    devices = Device.query.all()
    device_list = [{'id': device.id, 'room_id': device.room_id ,'name': device.name ,'type' :device.type ,'description': device.description ,'create_time' : device.create_time ,'update_time' : device.update_time ,'info' : device.info} for device in devices]
    return jsonify(device_list)

@blueprint.route('/device/<int:device_id>', methods=['GET'])
def get_device_by_id(device_id):
    device = Device.query.get(device_id)
    if device:
        return jsonify({'id': device.id, 'room_id': device.room_id ,'name': device.name ,'type' :device.type ,'description': device.description ,'create_time' : device.create_time ,'update_time' : device.update_time ,'info' : device.info})
    else:
        return jsonify({'error': 'Room not found'}), 404
    
@blueprint.route('/device/<int:room_id>/<string:type>', methods=['GET'])
def get_device_by_room_and_type(room_id, type):
    devices = Device.query.filter_by(room_id=room_id, type=type).all()
    
    if devices:
        device_list = []
        for device in devices:
            device_data = {
                'id': device.id,
                'room_id': device.room_id,
                'name': device.name,
                'type': device.type,
                'description': device.description or '',
                'create_time': device.create_time,
                'update_time': device.update_time,
                'info': device.info or ''
            }
            device_list.append(device_data)

        return jsonify({'devices': device_list})
    else:
        return jsonify({'error': 'Devices not found for the specified room_id and type'}), 404

    
@blueprint.route('/device/<string:device_id>', methods=['PUT'])
def update_device_by_id(device_id):
    device = Device.query.get(device_id)
    if not device:
        return jsonify({'error': 'Device not found'}), 404
    else:
        data = request.get_json()
        print(data)
        # Cập nhật chỉ khi có dữ liệu mới được cung cấp
        if 'id' in data:
            device.id = data['id']
        if 'room_id' in data:
            device.room_id = data['room_id']
        if 'name' in data:
            device.name = data['name']
        if 'type' in data:
            device.type = data['type']
        if 'description' in data:
            device.description = data['description']
        if 'info' in data:
            device.info = data['info']
        device.update_time = datetime.now()
        device.save()
        return jsonify({'message': 'Device updated successfully'})
    
@blueprint.route('/device/<string:device_id>', methods=['DELETE'])
def delete_device_by_id(device_id):
    device = Device.query.get(device_id)
    if device:
        db.session.delete(device)
        db.session.commit()
        return "Room Deleted"
    else:
        return jsonify({'error': 'Room not found'}), 404
    
#DEVICE STATE
#################################################################################
#Thực hiện truy vấn bảng DeviceState lấy trạng thái mới nhất của 
# tất cả các thiết bị của các phòng có type là dữ liệu nhập vào
@blueprint.route('/latest_device_state/<string:type>', methods=['GET'])
def get_latest_device_state(type):
    subquery = db.session.query(
        DeviceState.device_id,
        DeviceState.resource,
        func.max(DeviceState.time_stamp).label('latest_time_stamp')
    ).join(Device).filter(Device.type == type).group_by(DeviceState.device_id, DeviceState.resource).subquery()

    query = db.session.query(
        Device,
        DeviceState.time_stamp,
        DeviceState.resource,
        DeviceState.value,
        Room.name.label('room_name'),
        Device.room_id,
        Device.name.label('device_name')
    ).select_from(Device) \
    .join(
        subquery,
            (Device.id == subquery.c.device_id)&
            (DeviceState.resource == subquery.c.resource)&
            (DeviceState.time_stamp == subquery.c.latest_time_stamp)
    ).join(
        DeviceState,
            (Device.id == DeviceState.device_id)&
            (DeviceState.resource == subquery.c.resource)&
            (DeviceState.time_stamp == subquery.c.latest_time_stamp)
    ).join(
        Room,
            Device.room_id == Room.id
    )
    results = query.all()

    device_states = []
    for device, time_stamp, resource, value, room_name, room_id ,device_name in results:
        device_states.append({
            'device_id': device.id,
            'room_id': room_id,
            'room_name': room_name,
            'device_name': device_name,
            'time_stamp': time_stamp,
            'resource': resource,
            'value': value
        })

    return jsonify({'device_states': device_states})

@blueprint.route('/device-state', methods=['POST'])
def add_device_state():
    data = request.get_json()
    device_id=data['id'] 
    device_states = []

    # Kiểm tra từng trường hợp và thêm vào danh sách trạng thái
    # Tạo danh sách từ điển từ dữ liệu
    for resource in ['pir', 'temp', 'humi', 'sw1', 'sw2']:
        if resource in data:
            device_states.append({
                'device_id': device_id,
                'time_stamp': datetime.now(),
                'resource': resource,
                'value': data[resource],
            })

    # Lưu từng trạng thái vào cơ sở dữ liệu
    for device_state_data in device_states:
        db.session.add(DeviceState(**device_state_data))

    db.session.commit()

    # Trả về JSON
    return jsonify(device_states=device_states)

@blueprint.route('/device-state/list', methods=['GET'])
def get_all_device_state():
    deviceS = DeviceState.query.all()
    device_state_list = [{'id': device.id, 'device_id': device.device_id ,'time_stamp': device.time_stamp ,'resource' : device.resource ,'value': device.value } for device in deviceS]
    return jsonify(device_state_list)

@blueprint.route('/device-state/list/<int:device_state_id>', methods=['GET'])
def get_device_state_by_id(device_state_id):
    device = DeviceState.query.get(device_state_id)
    if device:
        return jsonify({'id': device.id, 'device_id': device.device_id ,'time_stamp': device.time_stamp ,'resource' : device.resource ,'value': device.value } )
    else:
        return jsonify({'error': 'Room not found'}), 404
    
# @blueprint.route('/device-state/<int:device_state_id>', methods=['PUT'])
# def update_device_state_by_id(device_state_id):
#     device = DeviceState.query.get(device_state_id)
#     if not device:
#         return jsonify({'error': 'Device not found'}), 404
#     else:
#         data = request.get_json()
#         print(data)
#         device.room_id=data['room_id'] 
#         device.name=data['name']
#         device.type=data['type']
#         device.description=data['description']
#         device.update_time = datetime.now()
#         device.info = data['info']
#         device.save()
#         return jsonify({'message': 'Device updated successfully'})
    
@blueprint.route('/device-state/<int:device_state_id>', methods=['DELETE'])
def delete_device_state_by_id(device_state_id):
    device = DeviceState.query.get(device_state_id)
    if device:
        db.session.delete(device)
        db.session.commit()
        return "Device State Deleted"
    else:
        return jsonify({'error': 'Device State not found'}), 404


