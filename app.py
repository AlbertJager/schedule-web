from flask import Flask, render_template, request
from schedule_parser import get_schedule
from weather_api import get_weather
from dotenv import load_dotenv
import os


load_dotenv()
API_WEATHER_TOKEN = os.getenv('API_WEATHER_TOKEN')

app = Flask(__name__)

#апишки ниже
@app.route('/')
def index():
    return render_template("index.html")


@app.route('/getting_group')
def getting_group():
    return render_template("getting_group.html")


@app.route("/getting_type_of_schedule", methods=["POST"])
def getting_type_of_schedule():
    group = request.form.to_dict().get("group")  # группа
    
    if get_schedule(group) == None: # словарь вида {'2025-11-15': 'text'}
        return render_template("wrong_group.html")        
    else:
        #записываем в бд группу от конкретного пользователя(логин)    (когда нибудь добавлю авторизацию и в разрере логинов буду хранить) 
        return render_template("getting_type_of_schedule.html", group=group)


@app.route("/schedule", methods=["POST"])   
def choosing_type_of_schedule():
    type_of_schedule = request.form.to_dict().get("type_of_schedule")  #today(ключ=today), tomorrow(ключ=tomorrow), week1(ключ = first_week), week2(ключ = second_week)
    
    
    
    return render_template("schedule.html", type_of_schedule=type_of_schedule)

    # group = request.form.to_dict().get("group")  # группа 
    
    # result = get_schedule(group)
    
    # return 












@app.route('/getting_city')
def get_tingcity():
    return render_template("getting_city.html")


@app.post('/get_weather')
def get_weather_from_api():
    city = request.form.to_dict().get("city").capitalize()
    
    response = get_weather(city, API_WEATHER_TOKEN)
    status_code = response[0]
    weather_result = response[-1]
    
    if status_code == 200:
        return render_template("weather.html", city=city, weather_result=weather_result)
    else:
        return render_template("wrong_city.html")

#run
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)