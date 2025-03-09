import requests
import json
import datetime
import configparser

# 读取配置文件
config = configparser.ConfigParser()
config.read('config.txt')

# 获取配置信息
weather_api_key = config['WEATHER_API']['api_key']
app_id = config['WECHAT']['app_id']
app_secret = config['WECHAT']['app_secret']
template_id = config['WECHAT']['template_id']
custom_message = config['CUSTOM_MESSAGE']['message']
user_ids = config['WECHAT']['user_ids'].split(',')  # 多个用户ID，用逗号分隔

# 城市设置为武汉
city = "武汉市"

# 获取天气信息
def get_weather(city):
    try:
        url = f"http://api.weatherapi.com/v1/current.json?key={weather_api_key}&q={city}"
        print(f"请求天气API的URL: {url}")  # 打印请求URL
        response = requests.get(url)
        print(f"天气API响应状态码: {response.status_code}")  # 打印状态码
        print(f"天气API响应内容: {response.text}")  # 打印响应内容
        response.raise_for_status()  # 检查请求是否成功
        data = response.json()
        
        # 检查返回的数据是否包含所需字段
        if 'current' in data and 'condition' in data['current']:
            weather = data['current']['condition']['text']
            temp = data['current']['temp_c']
            return weather, temp
        else:
            print("API 返回数据格式不正确:", data)
            return "未知", "未知"
    except Exception as e:
        print(f"获取天气信息失败: {e}")
        return "未知", "未知"

# 获取联网随机好句
def get_random_sentence_online():
    try:
        url = "https://api.quotable.io/random"
        print(f"请求随机好句API的URL: {url}")  # 打印请求URL
        response = requests.get(url)
        print(f"随机好句API响应状态码: {response.status_code}")  # 打印状态码
        print(f"随机好句API响应内容: {response.text}")  # 打印响应内容
        response.raise_for_status()  # 检查请求是否成功
        data = response.json()
        return f"{data['content']} ——{data['author']}"
    except Exception as e:
        print(f"获取随机好句失败: {e}")
        return "每一天都是一个新的开始。"  # 失败时返回默认句子

# 计算在一起的天数
def calculate_days_together():
    start_date = datetime.datetime(2025, 1, 30)
    today = datetime.datetime.now()
    delta = today - start_date
    return delta.days

# 获取微信公众号访问令牌
def get_access_token(app_id, app_secret):
    try:
        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={app_id}&secret={app_secret}"
        print(f"请求微信公众号访问令牌的URL: {url}")  # 打印请求URL
        response = requests.get(url)
        print(f"微信公众号访问令牌响应状态码: {response.status_code}")  # 打印状态码
        print(f"微信公众号访问令牌响应内容: {response.text}")  # 打印响应内容
        response.raise_for_status()  # 检查请求是否成功
        data = response.json()
        return data['access_token']
    except Exception as e:
        print(f"获取微信公众号访问令牌失败: {e}")
        return None

# 发送模板消息
def send_template_message(access_token, openid, template_id, data):
    try:
        url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}"
        payload = {
            "touser": openid,
            "template_id": template_id,
            "data": data
        }
        response = requests.post(url, json=payload)
        print(f"模板消息响应状态码: {response.status_code}")  # 打印状态码
        print(f"模板消息响应内容: {response.text}")  # 打印响应内容
        response.raise_for_status()  # 检查请求是否成功
        return response.json()
    except Exception as e:
        print(f"发送模板消息失败: {e}")
        return None

# 主函数
def main():
    # 获取天气信息
    weather, temp = get_weather(city)
    if weather == "未知" or temp == "未知":
        print("天气信息获取失败，使用默认值。")
        weather, temp = "晴", "25"  # 默认值
    
    # 获取联网随机好句
    random_sentence = get_random_sentence_online()
    
    # 计算在一起的天数
    days_together = calculate_days_together()
    
    # 获取微信公众号访问令牌
    access_token = get_access_token(app_id, app_secret)
    if not access_token:
        print("无法获取微信公众号访问令牌，程序退出。")
        return
    
    # 准备模板消息数据
    today = datetime.datetime.now().strftime("%Y-%m-%d %A")
    data = {
        "date": {"value": today},
        "city": {"value": city},
        "weather": {"value": weather},
        "temp": {"value": f"{temp}°C"},
        "days_together": {"value": days_together},
        "custom_message": {"value": custom_message},
        "random_sentence": {"value": random_sentence}
    }
    
    # 发送模板消息给多个用户
    for user_id in user_ids:
        result = send_template_message(access_token, user_id, template_id, data)
        if result and result.get('errcode') == 0:
            print(f"发送给用户 {user_id} 的结果: 成功")
        else:
            print(f"发送给用户 {user_id} 的结果: 失败")

if __name__ == "__main__":
    main()
