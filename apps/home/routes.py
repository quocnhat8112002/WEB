# -*- encoding: utf-8 -*-

import json
import os
from operator import and_

import requests
from apps.home import blueprint
from flask import render_template, request, jsonify ,redirect ,url_for
from flask_login import login_required
from jinja2 import TemplateNotFound

from flask_socketio import emit
from sqlalchemy.sql import func ,desc
from apps import db
import pandas as pd
from apps.events import client
from datetime import datetime, timedelta
from apps.home.model import Role, Project_list, Method_list, User_project_role, Page, Permissions, Role_permissions, Project_1
from apps.authentication.models import Users

UPLOAD_FOLDER = "C:/Users/ktvkt04.mhv/SystemIOT/WEB_CONTROL/WEB/Thiết kế DATABASE"


@blueprint.route('/index', methods=['GET'])
@login_required

def index():
    return render_template('home/index.html', segment='index') 

# @blueprint.route('/edit_condition/<int:id>')
# def render_condition(id):
#     return render_template('home/edit_condition.html', id=id)


@blueprint.route('/<path:template>')
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

# Helper - Extract current page name from request
def get_segment(request):
    try:
        segment = request.path.split('/')[-1]
        if segment == '':
            segment = 'index'
        return segment
    except:
        return None

##########################   ROLE   ################################

@blueprint.route('/role', methods=['POST'])  
# @login_required
def add_role():
    data = request.get_json()
    name = data.get('name')
    role = Role(name= name)
    role.save()
    return jsonify(200)

##########################   Project List   ################################

@blueprint.route('/project_list', methods=['POST'])  
# @login_required
def add_project_list():
    data = request.get_json()
    name=data.get('name','')
    address=data.get('address','')
    type = data.get('type', '')
    investor = data.get('investor', '')
    project = Project_list(name= name ,address=address, type=type, investor=investor)
    project.save()
    return jsonify(data, 200)
##########################   Map User_Project_Role   ################################

@blueprint.route('/user_project_role', methods=['POST'])  
# @login_required
def add_user_project_role():
    data = request.get_json()
    user_id=data.get('user_id','')
    project_id=data.get('project_id','')
    role_id = data.get('role_id', '')
    map_upr = User_project_role(user_id= user_id ,project_id=project_id, role_id=role_id)
    map_upr.save()
    return jsonify(data, 200)

##########################   Method List   ################################

@blueprint.route('/method_list', methods=['POST'])  
# @login_required
def add_method():
    data = request.get_json()
    method = data.get('method','')
    method_list = Method_list(method = method)
    method_list.save()
    return jsonify(data, 200)

##########################   Page List   ################################

@blueprint.route('/page_list', methods=['POST'])  
# @login_required
def add_page():
    data = request.get_json()
    url = data.get('url','')
    description = data.get('description','')
    page_list = Page(url = url, description = description)
    page_list.save()
    return jsonify(data, 200)

##########################   Permissions  ################################

@blueprint.route('/permissions_list', methods=['POST'])  
# @login_required
def add_permissions():
    data = request.get_json()
    page_id = data.get('page_id','')
    method_id = data.get('method_id','')
    description = data.get('description','')
    permissions = Permissions(page_id = page_id, method_id = method_id, description = description)
    permissions.save()
    return jsonify(data, 200)

##########################  Map Role_Permissions  ################################

@blueprint.route('/role_permissions', methods=['POST'])  
# @login_required
def add_role_permissions():
    data = request.get_json()
    role_id = data.get('role_id','')
    permissions_id = data.get('permissions_id','')
    role_permissions = Role_permissions(role_id = role_id, permissions_id = permissions_id)
    role_permissions.save()
    return jsonify(data, 200)

##########################  Project 1  ################################

#Add dữ liệu từ file excel đã có sẵn
@blueprint.route('/project_1', methods=['POST'])  
# @login_required
def add_project_1():
    filename = 'DATABASE.xlsx'  
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    # Kiểm tra xem file có tồn tại không
    if not os.path.exists(filepath):
        return jsonify({"error": f"File {filename} not found"}), 404
    try:
        data_frame = pd.read_excel(filepath, sheet_name='data_1')
        data_list = data_frame.to_dict(orient='records')

        created_records = []
        errors = []

        for index, record in enumerate(data_list):
            try:
                floor_id = record.get('floor_id', '')
                room_id = record.get('room_id', '')
                areas = record.get('areas', '')
                acreage = record.get('acreage', '')
                bedroom = record.get('bedroom', '')
                bathroom = record.get('bathroom', '')
                direction = record.get('direction', '')
                status = record.get('status', '')
                price = record.get('price', '')
                utility = record.get('utility', '')
                power = record.get('power', '')

                project_1 = Project_1(
                    floor_id=floor_id,
                    room_id=room_id,
                    areas=areas,
                    acreage=acreage,
                    bedroom=bedroom,
                    bathroom=bathroom,
                    direction=direction,
                    status = status,
                    price=price,
                    utility=utility,
                    power=power
                )
                project_1.save() 
                created_records.append(record)
            except Exception as e:
                errors.append({"index": index, "error": str(e)})
        return jsonify({
            "created_records": created_records,
            "errors": errors
        }), 200 if not errors else 207

    except Exception as e:
        return jsonify({"error": f"Failed to process file: {str(e)}"}), 500
    
#Tìm danh sách các phòng theo điều kiện và bật cổng led tương ứng
@blueprint.route('/condition_search', methods=['GET'])
# @login_required
def condition_search():
    data = request.get_json()  

    floor_id = data.get('floor_id', None)
    areas = data.get('areas', None)
    acreage = data.get('acreage', None)
    bedroom = data.get('bedroom', None)
    bathroom = data.get('bathroom', None)
    direction = data.get('direction', None)
    status = data.get('status', None)
    price = data.get('price', None)
    utility = data.get('utility', None)

    query = Project_1.query # Tạo truy vấn động

    if floor_id is not None:
        query = query.filter(Project_1.floor_id == floor_id)
    if areas is not None:
        query = query.filter(Project_1.areas == areas)
    if acreage is not None:
        query = query.filter(Project_1.acreage == acreage)
    if bedroom is not None:
        query = query.filter(Project_1.bedroom == bedroom)
    if bathroom is not None:
        query = query.filter(Project_1.bathroom == bathroom)
    if direction is not None:
        query = query.filter(Project_1.direction == direction)
    if status is not None:
        query = query.filter(Project_1.status == status)
    if price is not None:
        query = query.filter(Project_1.price == price)
    if utility is not None:
        query = query.filter(Project_1.utility.like(f"%{utility}%"))

    results = query.all()
    rooms = []
    channel_ids = []
    for project in results:
        rooms.append({
            'id': project.id,
            'floor_id': project.floor_id,
            'room_id': project.room_id,
            'areas': project.areas,
            'acreage': project.acreage,
            'bedroom': project.bedroom,
            'bathroom': project.bathroom,
            'direction': project.direction,
            'status': project.status,
            'price': project.price,
            'utility': project.utility,
            'power': project.power,
        })
        channel_ids.append(project.id)

    topic = "modelx/192.168.87.122/request/one"
    payload = {
        "topic": topic,
        "channels": channel_ids,
        "value": 1  
    }
    url_update_power = "http://192.168.1.82:5000/update_power"
    url_post_mqtt = "http://192.168.1.82:5000/post_mqtt"

    try:
        response_1 = requests.post(url_update_power, json=payload)
        if response_1.status_code != 200:
            return jsonify({'error': 'Failed to call first external API.'}), 500

        response_2 = requests.post(url_post_mqtt, json=payload)
        if response_2.status_code != 200:
            return jsonify({'error': 'Failed to call second external API.'}), 500

        return jsonify({'message': 'Rooms found and both MQTT requests sent successfully.', 'rooms': rooms}), 200
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500


# Lưu trạng thái các cổng
@blueprint.route('/update_power', methods=['POST'])
# @login_required
def update_power():
    try:
        data = request.get_json()
        channels = data.get('channels', []) 
        value = data.get('value', None)  
        if value is None:
            return jsonify({'error': 'Invalid data. Please provide "value".'}), 400

        if not channels:
            update_data = [{'id': project.id, 'power': value} for project in Project_1.query.all()]
        else:
            update_data = [{'id': channel, 'power': value} for channel in channels]

        # Sử dụng bulk_update_mappings để cập nhật nhiều bản ghi trong một lần
        db.session.bulk_update_mappings(Project_1, update_data)
        db.session.commit()

        return jsonify({'message': f'Successfully updated {len(update_data)} records.'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# API nhận topic và gửi dữ liệu lên MQTT
@blueprint.route('/post_mqtt', methods=['POST'])
# @login_required
def post_mqtt():
    try:
        data = request.get_json()
        topic = data.get('topic')
        data.pop('topic', None)   # Loại bỏ topic khỏi dữ liệu để gửi phần còn lại
        
        json_payload = json.dumps(data)
        client.publish(topic, payload=(json_payload))

        return jsonify({'message': f"Successfully sent data to {topic}."}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# API nhận topic và gửi dữ liệu lên MQTT
@blueprint.route('/post_mqtt_one', methods=['POST'])
# @login_required
def post_mqtt_one():
    try:
        data = request.get_json()
        json_payload = json.dumps(data)
        client.publish("modelx/192.168.87.122/request/one", payload=(json_payload))

        return jsonify({'message': f"Successfully sent data"}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

##############################################################################   
#### XU LY KHI RULE GUI LENH
# @blueprint.route('/rule/request', methods=['POST'])
# def rule_request():
#     data = request.get_json()
#     # Lặp qua mỗi device_id
#     for device_id in data:
#         # Tạo một từ điển mới
#         device_dict = {'id': device_id, 'sw1': 0 ,'sw2':0}
#         json_data = json.dumps(device_dict)
#         client.publish("rems/request/dev", payload=(json_data))
#     return jsonify( 200)
    

# @blueprint.route('/rule', methods=['POST'])
# def rule():
#     #Danh sách các phòng mà api sẽ gửi lệnh tắt lên mqtt
#     ids = []
#     ###########################################################################
#     #Lấy ra các phòng có time_stamp thỏa mãn với điều kiện time condition của pir
#     time = datetime.now()
#     # Lấy tất cả các bản ghi RoomStatus có trường resource='pir' 
#     pir_records = RoomStatus.query.filter(
#         RoomStatus.resource == 'pir',
#     ).all()
#     # Lưu danh sách room_id của những bản ghi có điều kiện time thỏa mãn của pir
#     pir_room_ids = []
#     for record in pir_records:
#         if record.time_stamp <= time - timedelta(minutes=record.time_condition):
#             pir_room_ids.append(record)

#     # Loại bỏ các room_id trùng lặp (nếu có)
#     pir_room_ids = list(set(pir_room_ids))
#     print(pir_room_ids)
#     ###############################################################################
#     #Danh sách phòng với giá trị i
#     i_records = RoomStatus.query.filter(
#         RoomStatus.resource == 'i',
#     ).all()    
#     ##################################################################################
#     if pir_room_ids or i_records:
#         # Lọc bảng RuleCondition để lấy ra bản ghi có trường resource = 'pir'
#         pir_conditions = RuleCondition.query.filter_by(resource='pir').first()
#         #Gán kiểu điều kiện     
#         value_condition = pir_conditions.condition
#         #Gía trị để thỏa mãn điều kiện
#         value = pir_conditions.value
#         #Id rule condition
#         id = pir_conditions.id
#         ################################################################################
#         #Lọc bảng ruleCondition tìm bản ghi của i
#         i_conditions = RuleCondition.query.filter_by(resource='i').first()
#         #Gán kiểu điều kiện     
#         i_condition = i_conditions.condition
#         #Gía trị để thỏa mãn điều kiện
#         i_value = i_conditions.value
#         #Id rule condition
#         i_id = i_conditions.id
#         #Danh sách phòng có i lớn hơn i condition
#         i_room =[]
#         #Kiểm tra condition của i
#         for i in i_records:
#             if i_condition == "1":
#                 if i.value > i_value:
#                     i_room.append(i)
#         #Tiếp tục kiểm tra với id ruleAction xem làm gì
#         # Lặp qua danh sách các bản ghi trong bảng RuleAction
#         if i_id:
#             #Tiếp tục tìm action thỏa mãn với id rule
#             i_actions = []
#             # Lặp qua danh sách các bản ghi trong bảng RuleAction
#             for action in RuleAction.query.filter_by(id_rule=i_id).all():
#                 # Thêm bản ghi vào danh sách actions
#                 i_actions.append(action)
#                 # Kiểm tra xem danh sách actions có tồn tại hay không         
#             if i_actions:
#                 for ac in i_actions:
#                     if ac.device == "sw" and ac.value == "0":
#                     #Thỏa mãn action là tắt tất cả thiết bị thì thêm các phòng có id = i_room vào danh sách gửi lệnh tăt
#                         for i in i_room :
#                             ids.append(i.room_id)
#         #############################################################################
#         #Danh sách các phòng thỏa mãn condition của pir
#         rooms = []
#         #Kiểm tra condition xem điều kiện là gì, 0 ở đây là = , 1 là >, 2 là <
#         if value_condition == "0":
#             for room_id in pir_room_ids:
#             # Kiểm tra xem bản ghi có tồn tại và có thỏa mãn điều kiện trong RuleCondition không
#                 if  room_id.value == value:
#                     # Thêm bản ghi vào danh sách rooms
#                     rooms.append(room_id)
#             #Tiếp tục tìm action thỏa mãn với id rule
#             actions = []
#             # Lặp qua danh sách các bản ghi trong bảng RuleAction
#             for action in RuleAction.query.filter_by(id_rule=id).all():
#                 # Thêm bản ghi vào danh sách actions
#                 actions.append(action)

#             # Kiểm tra xem danh sách actions có tồn tại hay không
#             if actions:
#                 #lấy ra id của các phòng thỏa mãn điều kiện
#                 for room in rooms:
#                     ids.append(room.room_id)

#                 #Danh sách chứa nhưng id controller mà 1 trong 2 sw đang bật
#                 device_id =[]
#                 for id in ids:
#                     # Truy vấn các thiết bị có room_id tương ứng và type là "controller"
#                     devices = Device.query.filter_by(room_id=id, type='controller').all()
#                     # Lặp qua các thiết bị
#                     if devices :
#                         for device in devices:
#                             # Tìm bản ghi mới nhất của 'sw1' và 'sw2' cho mỗi device_id
#                             latest_states_sw1 = DeviceState.query.filter_by(device_id=device.id, resource='sw1').order_by(DeviceState.time_stamp.desc()).first()
#                             latest_states_sw2 = DeviceState.query.filter_by(device_id=device.id, resource='sw2').order_by(DeviceState.time_stamp.desc()).first()

#                             # Nếu bản ghi mới nhất của 'sw1' có value = 1, thêm device_id vào danh sách
#                             if latest_states_sw1.value == "1" or latest_states_sw2.value == "1":
#                                 device_id.append(device.id)
#                 # Loại bỏ các id trùng lặp (nếu có)
#                 device_id = list(set(device_id))
#                 for rule_action in actions:
#                     if rule_action.device == "sw" and rule_action.value == "0" :
#                         # Gửi lệnh tắt tất cả các sw của các phòng trong ids
#                         data = device_id
#                         api_url = 'http://127.0.0.1:5000/rule/request'
#                         headers = {'Content-Type': 'application/json'}
#                         # Thực hiện yêu cầu POST
#                         response = requests.post(api_url, json=data, headers=headers)
#                         if response.status_code == 200:
#                             print('Post api successful')
#                         else :
#                             print(f'API request failed with status code {response.status_code}')
#             else:
#                 print("Danh sách actions không tồn tại.")
#     return ("da thuc hien router" )
            


