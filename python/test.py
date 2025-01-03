import requests
from datetime import datetime

def get_weather():
    # 使用 OpenWeatherMap API，你需要注册一个免费账号来获取 API key
    api_key = "YOUR_API_KEY_HERE"
    city = "Beijing"  # 你可以更改为任何城市
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    try:
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            temperature = data['main']['temp']
            description = data['weather'][0]['description']
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']

            print(f"天气报告 - {city} ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
            print(f"温度: {temperature}°C")
            print(f"天气状况: {description}")
            print(f"湿度: {humidity}%")
            print(f"风速: {wind_speed} m/s")
        else:
            print("无法获取天气信息")

    except requests.RequestException as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    get_weather()
