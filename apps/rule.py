from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apps.home.model import Room ,Device ,DeviceState ,RoomStatus ,RuleCondition ,RuleAction
import requests

scheduler = BackgroundScheduler()

def check_conditions():
    import requests
    # Gọi API /device-state
    data = None
    api_url1 = 'http://127.0.0.1:5000/rule'
    headers = {'Content-Type': 'application/json'}
    # Thực hiện yêu cầu POST
    response1 = requests.post(api_url1, json=data, headers=headers)
    # # Lấy thời điểm 10 phút trước
    # ten_minutes_ago = datetime.utcnow() - timedelta(minutes=10)
    # # Lấy tất cả các bản ghi RoomStatus có trường resource='pir' và time_stamp <= ten_minutes_ago
    # pir_records = RoomStatus.query.filter(
    #     RoomStatus.resource == 'pir',
    #     RoomStatus.time_stamp <= ten_minutes_ago
    # ).all()
    # # Lưu danh sách room_id của những bản ghi có điều kiện
    # room_ids = []
    # for record in pir_records:
    #     room_ids.append(record)

    # # Loại bỏ các room_id trùng lặp (nếu có)
    # room_ids = list(set(room_ids))

    # if room_ids :
    #     # Lọc bảng RuleCondition để lấy ra bản ghi có trường resource = 'pir'
    #     pir_conditions = RuleCondition.query.filter_by(resource='pir').all()
    #     #Gán kiểu điều kiện     
    #     value_condition = pir_conditions.condition
    #     #Gía trị để thỏa mãn điều kiện
    #     value = pir_conditions.value
    #     id = pir_conditions.id
    #     #Danh sách các phòng thỏa mãn condition
    #     rooms = []
    #     #Kiểm tra condition xem điều kiện là gì, 0 ở đây là = , 1 là >, 2 là <
    #     if value_condition == "0":
    #         for room_id in room_ids:
    #         # Kiểm tra xem bản ghi có tồn tại và có thỏa mãn điều kiện trong RuleCondition không
    #             if  room_id.value == value:
    #                 # Thêm bản ghi vào danh sách rooms
    #                 rooms.append(room_id)

    #         #Tiếp tục tìm action thỏa mãn với id rule
    #         actions = []
    #         # Lặp qua danh sách các bản ghi trong bảng RuleAction
    #         for action in RuleAction.query.filter_by(id_rule=id).all():
    #             # Thêm bản ghi vào danh sách actions
    #             actions.append(action)

    #         # Kiểm tra xem danh sách actions có tồn tại hay không
    #         if actions:
    #             #lấy ra id của các phòng thỏa mãn điều kiện
    #             ids = []
    #             for room in rooms:
    #                 ids.append(room.room_id)
                
    #             # for rule_action in actions:
    #             #     if rule_action.device == "sw" and rule_action.value == "0" :
    #                     #Gửi lệnh tắt tất cả các sw của các phòng trong ids
    #                     # data = {'ids': ids}
    #                     # api_url = 'http://127.0.0.1:5000/rule/request'
    #                     # headers = {'Content-Type': 'application/json'}
    #                     # # Thực hiện yêu cầu POST
    #                     # response = requests.post(api_url, json=data, headers=headers)
    #                     # if response.status_code == 200:
    #                     #     print('Post api successful')
    #                     # else :
    #                     #     print(f'API request failed with status code {response.status_code}')
    #         # else:
    #         #     print("Danh sách actions không tồn tại.")
            

