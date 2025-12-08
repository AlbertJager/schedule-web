from flask import Flask, render_template, request, flash, get_flashed_messages, url_for, redirect, jsonify, session
from werkzeug.exceptions import HTTPException
from schedule_parser import get_schedule
from weather_api import get_weather
import datetime
from dotenv import load_dotenv
import os


load_dotenv()
API_WEATHER_TOKEN = os.getenv('API_WEATHER_TOKEN')

app = Flask(__name__)
app.secret_key = 'asad;alskdjaqegqwu@!"?>>>><eh128e9yeqfuhbcscczxc'
# app.config['SESSION_PERMANENT'] = False

#апишки ниже
@app.route('/')
def index():
    print(session.get("username", "Гость"))
    return render_template("index.html")


@app.route('/getting_group/')
def getting_group():
    return render_template("getting_group.html")


@app.route("/getting_type_of_schedule", methods=["GET", "POST"])
def getting_type_of_schedule():
    group = request.form.to_dict().get("group")  # группа
    
    if get_schedule(group) == None: # словарь вида {'2025-11-15': 'text'}
        return render_template("wrong_group.html")        
    else:
        #записываем в бд группу от конкретного пользователя(логин)    (когда нибудь добавлю авторизацию и в разрере логинов буду хранить) 
        return render_template("getting_type_of_schedule.html", group=group)


#ТУТ НАДО СДЕЛАТЬ /schedule/{group}!!!!!!!!!
@app.route("/schedule/<group>/<type_of_schedule>", methods=["GET", "POST"])   # проверить вписав только лишь путь!!!!!!!
def schedule(group, type_of_schedule):
    
    # type_of_schedule = request.form.to_dict().get("type_of_schedule")  #today(ключ=today), tomorrow(ключ=tomorrow), week1(ключ = first_week), week2(ключ = second_week)
    
    schedule = get_schedule(group)
    if schedule == None:
        return render_template('httperror.html', error="Упс...", description="К сожалению, введенные данные содержат ошибки."), 404
    res = ""
    if type_of_schedule == 'today':
        today = datetime.date.today().__str__()
        if today in schedule["first_week"]:
            week = "first_week"
        else:
            week = "second_week"
        res = schedule[week].get(today)  # список вида [день, тип недели, начало пары, конец пары, препод, дисциплина, тип дисциплины, аудитория или ссылка]  
        
    elif type_of_schedule == 'tomorrow':
        tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).__str__()
        if tomorrow in schedule["first_week"]:
            week = "first_week"
        else:
            week = "second_week"
        res = schedule[week].get(tomorrow)  # список вида [день, тип недели, начало пары, конец пары, препод, дисциплина, тип дисциплины, аудитория или ссылка] 
    
    elif type_of_schedule == 'week1':
        week = "first_week"

        res = schedule[week].values()  # тут список со списками(днями) 
    
    elif type_of_schedule == 'week2':
        week = "second_week"

        res = schedule[week].values()  # тут список со списками(днями)
    
    else:
        return render_template('httperror.html', error="Упс...", description="Такой тип расписания недоступен, выберите из списка."), 404
    
    return render_template("schedule.html", res=res, type=type_of_schedule, group=group)


@app.route('/getting_city')
def getting_city():
    return render_template("getting_city.html")


@app.post('/get_weather')
def get_weather_from_api():
    city = request.form.to_dict().get("city").strip().capitalize()
    
    response = get_weather(city, API_WEATHER_TOKEN)
    status_code = response[0]
    weather_result = response[-1]
    
    if status_code == 200:
        return render_template("weather.html", city=city, weather_result=weather_result)
    else:
        return render_template("wrong_city.html")


@app.route("/sign_out", methods=["POST"])
def sign_out():
    session["authorized"] = False
    flash('Вы вышли из системы', 'logout')
    return redirect(url_for('index'))


@app.route("/sign_in", methods=["POST"])
def sign_in():
    login = request.form["login"]
    password = request.form["password"]

    if len(login) <= 2:
        return jsonify({'success': False, 'error': 'Логин должен быть не менее 3 символов'})
    else:
        # session['user'] = login
        session["authorized"] = True
        session["username"] = login
        session["password"] = password

        return jsonify({'success': True, 'username': session["username"]})

    

@app.route("/sign_up", methods=["POST"])
def sign_up():
    login, email, password = request.form["login"], request.form["email"], request.form["password"] 
    return f"{login}, {email}, {password}"


@app.errorhandler(HTTPException)
def error_handler(error):
    return render_template('httperror.html', error=error.code, description=error.description), error.code
#run app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)