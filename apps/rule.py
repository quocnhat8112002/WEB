from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
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
    