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
    url = f"http://api.weatherapi.com/v1/current.json?key={weather_api_key}&q={city}"
    response = requests.get(url)
    data = response.json()
    weather = data['current']['condition']['text']
    temp = data['current']['temp_c']
    return weather, temp


# 获取联网随机好句
def get_random_sentence_online():
    try:
        url = "https://api.quotable.io/random"
        response = requests.get(url)
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
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={app_id}&secret={app_secret}"
    response = requests.get(url)
    data = response.json()
    return data['access_token']


# 发送模板消息
def send_template_message(access_token, openid, template_id, data):
    url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}"
    payload = {
        "touser": openid,
        "template_id": template_id,
        "data": data
    }
    response = requests.post(url, json=payload)
    return response.json()


# 主函数
def main():
    # 获取天气信息
    weather, temp = get_weather(city)

    # 获取联网随机好句
    random_sentence = get_random_sentence_online()

    # 计算在一起的天数
    days_together = calculate_days_together()

    # 获取微信公众号访问令牌
    access_token = get_access_token(app_id, app_secret)

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
        print(f"发送给用户 {user_id} 的结果: {result}")


if __name__ == "__main__":
    main()
