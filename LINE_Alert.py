import requests


def req_line_alert(str_msg):
    with open(r"C:\LINE_TOEKN.txt", 'r') as file:
        TOKEN = file.read()
    # 記錄Line Notify服務資訊
    Line_Notify_Account = {'Client ID': 'xxxxxxxxxxxxxxxxx',
                           'Client Secret': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
                           'token': f'{TOKEN}'}

    # 將token放進headers裡面
    headers = {'Authorization': 'Bearer ' + Line_Notify_Account['token'],
               "Content-Type": "application/x-www-form-urlencoded"}

    # 回傳測試文字
    params = {"message": f"\n{str(str_msg)}"}

    # 執行傳送測試文字
    # 使用post方法
    print('發送訊息')
    r = requests.post("https://notify-api.line.me/api/notify",
                      headers=headers, params=params)
