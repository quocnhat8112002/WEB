# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from operator import and_

import requests
from apps.home import blueprint
from flask import render_template, request, jsonify ,redirect ,url_for
from flask_login import login_required
from jinja2 import TemplateNotFound

from apps.home.model import Sales ,Room ,Device ,DeviceState ,RoomStatus ,RuleCondition ,RuleAction
from flask_socketio import emit
from sqlalchemy.sql import func ,desc
from apps import db
from apps.events import client
from datetime import datetime, timedelta


@blueprint.route('/index', methods=['GET'])
@login_required

def index():
    query = db.session.query(func.count(Sales.product), func.count(Sales.product).filter(Sales.status == 'Completed'))
    sales = query.first()

    rooms = Room.query.all()
    room_list = [{'id': room.id, 'name': room.name ,'description': room.description} for room in rooms]
    print(room_list)
    
    return render_template('home/index.html', segment='index', sales=sales ,room_list=room_list)

@blueprint.route('/edit_condition/<int:id>')
def render_condition(id):
    return render_template('home/edit_condition.html', id=id)

@blueprint.route('/edit_action/<int:id>')
def render_action(id):
    return render_template('home/edit_action.html', id=id)

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
@blueprint.route('/latest_device_state/<int:room_id>/<string:type>', methods=['GET'])
def get_device_state(room_id , type):
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
    ).filter(Device.room_id == room_id) 
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
    for resource in ['pir', 'temp', 'humi', 'sw1', 'sw2' , 'e' , 'i']:
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
    
    
@blueprint.route('/device-state/<int:device_state_id>', methods=['DELETE'])
def delete_device_state_by_id(device_state_id):
    device = DeviceState.query.get(device_state_id)
    if device:
        db.session.delete(device)
        db.session.commit()
        return "Device State Deleted"
    else:
        return jsonify({'error': 'Device State not found'}), 404
#Tìm tất cả giá trị theo room_id và type nhập vào
@blueprint.route('/device_state/<int:room_id>/<string:type>', methods=['GET'])
def get_all_device_states(room_id, type):
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
        DeviceState,
        Device.id == DeviceState.device_id
    ).join(
        Room,
        Device.room_id == Room.id
    ).filter(
        (Device.room_id == room_id) &
        (Device.type == type)
    )
    results = query.all()

    device_states = []
    for device, time_stamp, resource, value, room_name, room_id, device_name in results:
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

#Tìm trạng thái chung mới nhất của từng phòng
@blueprint.route('/latest_deviceState/<string:type>', methods=['GET'])
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

#### XU LY KHI CLIENT GUI LENH
@blueprint.route('/request/esp', methods=['POST'])
def request_esp():
    data = request.get_json()
    print(data)
    client.publish("rems/client/request", payload=str(data))
    return jsonify(data, 200)

##########  ROOM STATUS   ############################
#Thêm trạng thái vào phòng
@blueprint.route('/room_status', methods=['POST'])
def add_status():
    data = request.get_json()
    room_id = data['room_id'] 
    time_stamp = datetime.now()
    resource = data['resource'] 
    value = data['value']
    roomStatus = RoomStatus(room_id=room_id,  time_stamp = time_stamp, resource= resource ,value= value)
    roomStatus.save()
    return jsonify(data, 200)

#Cập nhật trạng thái mới của bảng
@blueprint.route('/room_status', methods=['PUT'])
def update_status_room():
    data = request.get_json()
    # Kiểm tra xem data có trường 'id' không
    if 'id' not in data:
        return jsonify({'error': 'Missing id in request data'}), 400
    # Lấy room_id từ bảng Device dựa trên id trong request data
    device_id = data['id']
    device = Device.query.filter_by(id=device_id).first()
    if not device:
        return jsonify({'error': 'Device not found'}), 404
    room_id = device.room_id
    # Lấy giá trị từ các trường 'pir', 'temp', 'i' nếu có
    pir_value = data.get('pir')
    i_value = data.get('i')
    # Gán trường và giá trị dựa trên trường tồn tại trong dữ liệu đầu vào
    field = ""
    value_field = ""
    if pir_value is not None:
        field = "pir"
        value_field = pir_value
    elif i_value is not None:
        field = "i"
        value_field = i_value
    # Kiểm tra xem có trường nào tồn tại không và thực hiện gán giá trị
    if field:
        # Chiếu vào bảng RoomStatus và cập nhật giá trị
        room_status_record = RoomStatus.query.filter_by(room_id=room_id, resource=field).first()

        if room_status_record:
            room_status_record.value = value_field
            room_status_record.time_stamp = datetime.now()

        # Lưu thay đổi vào database
        db.session.commit()
    return jsonify({'message': 'Data processed successfully'})

####################### RULE CONDITION  ###########################
@blueprint.route('/rule_condition', methods=['POST'])
def add_condition():
    data = request.get_json()
    resource = data['resource'] 
    condition = data['condition'] 
    value = data['value']
    ruleCondition = RuleCondition( resource= resource ,condition = condition ,value= value)
    ruleCondition.save()
    # Sử dụng thuộc tính returning để lấy ID sau khi thêm mới
    db.session.refresh(ruleCondition)

    # Trả về kết quả với ID
    response_data = {
        'id': ruleCondition.id,
        'resource': ruleCondition.resource,
        'condition': ruleCondition.condition,
        'value': ruleCondition.value,
    }
    return jsonify(response_data)

@blueprint.route('/rule_condition/<int:id>', methods=['PUT'])
def update_rule_condition(id):
    data = request.get_json()
    # Kiểm tra xem có bản ghi nào có trường 'id' như người dùng đã nhập không
    rule_condition = RuleCondition.query.get(id)
    if rule_condition is None:
        return jsonify({'error': f'RuleCondition with id {id} not found'}), 404

    rule_condition.condition = data['condition']
    rule_condition.value = data['value']
    db.session.commit()
    
    return jsonify({'message': f'RuleCondition with id {id} updated successfully'}), 200

@blueprint.route('/rule_condition', methods=['GET'])
def get_all_condition():
    conditions = RuleCondition.query.all()
    list_conditions = [{'id': condition.id, 'resource': condition.resource ,'condition': condition.condition , 'value': condition.value  } for condition in conditions]
    return jsonify(list_conditions)

#######################  RULE ACTION  ##########################
@blueprint.route('/rule_action', methods=['POST'])
def add_action():
    data = request.get_json()
    id_rule = data['id_rule'] 
    device = data['device'] 
    value = data['value']
    ruleAction = RuleAction( id_rule= id_rule ,device = device ,value= value)
    ruleAction.save()
    return jsonify(data, 200)

@blueprint.route('/rule_action/<int:id>', methods=['PUT'])
def update_rule_action(id):
    data = request.get_json()
    # Kiểm tra xem có bản ghi nào có trường 'id' như người dùng đã nhập không
    rule_action = RuleAction.query.get(id)
    if rule_action is None:
        return jsonify({'error': f'RuleCondition with id {id} not found'}), 404

    rule_action.device = data['device']
    rule_action.value = data['value']
    db.session.commit()
    
    return jsonify({'message': f'RuleCondition with id {id} updated successfully'}), 200

@blueprint.route('/rule_action', methods=['GET'])
def get_all_action():
    actions = RuleAction.query.all()
    list_actions = [{'id': action.id, 'id_rule': action.id_rule ,'device': action.device , 'value': action.value  } for action in actions]
    return jsonify(list_actions)

#### XU LY KHI RULE GUI LENH
@blueprint.route('/rule/request', methods=['POST'])
def rule_request():
    data = request.get_json()
    print(data)
    # Khởi tạo mảng id_device chứa id của các thiết bị cần tắt
    id_device = []
    # Lặp qua từng giá trị trong mảng 'ids'
    for room_id in data:
        print(room_id)
        # Tìm bản ghi trong bảng Device có room_id và type tương ứng
        device_record = Device.query.filter_by(room_id=int(room_id), type='controller').first()

        # Nếu bản ghi tồn tại, thêm id vào mảng id_device
        if device_record:
            id_device.append(device_record.id)

    print("abcb")
    client.publish("rems/rule/request", payload=str(id_device))
    return jsonify( 200)

@blueprint.route('/rule', methods=['POST'])
def rule():
    # Lấy thời điểm 10 phút trước
    ten_minutes_ago = datetime.utcnow() - timedelta(minutes=10)
    # Lấy tất cả các bản ghi RoomStatus có trường resource='pir' và time_stamp <= ten_minutes_ago
    pir_records = RoomStatus.query.filter(
        RoomStatus.resource == 'pir',
        RoomStatus.time_stamp <= ten_minutes_ago
    ).all()
    # Lưu danh sách room_id của những bản ghi có điều kiện
    room_ids = []
    for record in pir_records:
        room_ids.append(record)

    # Loại bỏ các room_id trùng lặp (nếu có)
    room_ids = list(set(room_ids))

    if room_ids :
        # Lọc bảng RuleCondition để lấy ra bản ghi có trường resource = 'pir'
        pir_conditions = RuleCondition.query.filter_by(resource='pir').first()
        #Gán kiểu điều kiện     
        value_condition = pir_conditions.condition
        #Gía trị để thỏa mãn điều kiện
        value = pir_conditions.value
        id = pir_conditions.id
        #Danh sách các phòng thỏa mãn condition
        rooms = []
        #Kiểm tra condition xem điều kiện là gì, 0 ở đây là = , 1 là >, 2 là <
        if value_condition == "0":
            for room_id in room_ids:
            # Kiểm tra xem bản ghi có tồn tại và có thỏa mãn điều kiện trong RuleCondition không
                if  room_id.value == value:
                    # Thêm bản ghi vào danh sách rooms
                    rooms.append(room_id)

            #Tiếp tục tìm action thỏa mãn với id rule
            actions = []
            # Lặp qua danh sách các bản ghi trong bảng RuleAction
            for action in RuleAction.query.filter_by(id_rule=id).all():
                # Thêm bản ghi vào danh sách actions
                actions.append(action)

            # Kiểm tra xem danh sách actions có tồn tại hay không
            if actions:
                #lấy ra id của các phòng thỏa mãn điều kiện
                ids = []
                for room in rooms:
                    ids.append(room.room_id)
                
                print(ids)
                for rule_action in actions:
                    if rule_action.device == "sw" and rule_action.value == "0" :
                        # Gửi lệnh tắt tất cả các sw của các phòng trong ids
                        data = ids
                        api_url = 'http://127.0.0.1:5000/rule/request'
                        headers = {'Content-Type': 'application/json'}
                        # Thực hiện yêu cầu POST
                        response = requests.post(api_url, json=data, headers=headers)
                        if response.status_code == 200:
                            print('Post api successful')
                        else :
                            print(f'API request failed with status code {response.status_code}')
            else:
                print("Danh sách actions không tồn tại.")
    return ("da thuc hien router" )
            

