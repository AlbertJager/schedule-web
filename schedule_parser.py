import requests
from bs4 import BeautifulSoup
import re
from datetime import date


current_date = date.today().__str__()  #  текущая дата в виде строки '2025-11-15'
CURRENT_YEAR = str(date.today().year)
# словарь для хранения строковых представлений месяцев
months = {
    'января': '01',
    'февраля': '02',
    'марта': '03',
    'апреля': '04',
    'мая': '05',
    'июня': '06',
    'июля': '07',
    'августа': '08',
    'сентября': '09',
    'октября': '10',
    'ноября': '11',
    'декабря': '12',
}

def get_page_by_group(group: str):
    '''
        Получает и наводит красоту сайта с расписанием конкретной группы.
        Возвращает красивую форму сайта в виде html
    '''
    
    url = f'https://s.kubsau.ru/?type_schedule=1&val={group}'
    headers = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"}


    response = requests.get(url, headers=headers)
    souped = BeautifulSoup(response.text, 'lxml')
    
    #Проверка на ошибку, если такой группы нет или неверные данные
    if souped.find('div', class_='row sched fast-schedule') == None:
        print('Данные о группе неверные, введите в похожем формате: ИТ2304')
        return None        
    else:
        return souped
    

def checking_the_amount_of_disciplines(all_rows_of_table) -> int:
    c = 0
    for row in all_rows_of_table:
        c+= len(row.find('td', class_='diss').text.split())
    return c

def get_schedule(group: str):
    '''
        Используя souped-версию сайта, достает все данные о расписании группы на две недели
    '''
    
    
    main_dict = {
        "first_week": {},
        "second_week": {}
    }

    page = get_page_by_group(group)
    if page == None:
        return None
    else:

        # num_of_group = page.find('h2',class_='h2-responsive').find('strong').text

        days = page.find_all('div', class_=re.compile(r'card-block.*day-\d{4}-\d{2}-\d{2}'))[3:]
        
        for i in range(len(days)):
            res = []
            
            #начиная с 7 индекса идет вторая неделя
            if i < 7:
                key_week = "first_week"
                num_of_week = 'Первая неделя'
            else:
                key_week = "second_week"
                num_of_week = "Вторая неделя"
            
            # main_dict[key_week] = {}
            
            day = days[i]
            
            day_of_the_week, date, month  = [el for el in day.find('h4').text.split() if el != '|']  #Конкретный день

            if int(date) < 10:
                key_date = f'{CURRENT_YEAR}-{months[month]}-{"0" + date}'
            else:
                key_date = f'{CURRENT_YEAR}-{months[month]}-{date}'
            
            table_body = day.find('tbody')  #тело расписания(таблица)
            
            for_print = f'{day_of_the_week} | {date} {month}'

            # frame_width = 57 if 57 % len(for_print) == 0 else 58  # выбираем ширину рамки

            
            
            
            # res+=('-' * frame_width+'\n')
            # res+=('|' + for_print.center(frame_width - 2) + '|'+'\n')
            # res+=('-' * frame_width + '\n')
            res.append(for_print)
            res.append(num_of_week)

            all_rows_of_table = table_body.find_all('tr')  #все строки с занятиями конкретного дня
            
            #Если у конкретного дня нет занятий, то переходим к следующему дню!!!!
            if checking_the_amount_of_disciplines(all_rows_of_table) == 0:
                res.append('Нет занятий')
                # добавление пустого дня
                main_dict[key_week][key_date] = res
                continue
            else:
                for row in all_rows_of_table:  # обработка строк таблицы(пар)   
                    #Если длина учителя-списка больше 3, то
                    #перебрать в цикле


                    if len(row.find('td', class_='diss').text.split()) == 0:  # если нет занятия, остальные данные не нужны, переходим к следующей строке
                        continue
                    else:
                        teacher_row = row.find('td', class_='diss').find('span', class_='diss-info').text.strip()
                        teacher_list = [word for word in teacher_row.split() if word !=',']
                        if len(teacher_list) > 3 and any(item.startswith(group) for item in teacher_list):
                            teacher = teacher_list[0]+' '
                            for i in range(1, len(teacher_list)):
                                word = teacher_list[i]
                                if word.startswith(f'{group}'):
                                    teacher += 'и ' + word + ' '                    
                                else:
                                    teacher += word+' ' 
                        else:
                            teacher = ' '.join(teacher_list)
                        
                        discipline_list = [word for word in row.find('td', class_='diss').text.split() if word !='Ссылка' and word !='на' and word !='занятие' and word not in teacher and word not in "0123456789!@#$%^&*()_+=[]|;:',."]
                        discipline = ' '.join(discipline_list)  # строка дисциплины, содержащая данные о предмете    

                        # если физкультура 
                        if discipline_list[0] == 'Элективные':
                            discipline = ' '.join(discipline_list[:5])
                            teacher = ' '.join(teacher_list[:3]) + ' и многие другие'
            
                        
                        
                        time_start, time_end = row.find('td', class_='time').text.split()  # Начало и конец пары

                        type_of_discipline = 'Практика' if row.find('td', class_='lection yes') == None else 'Лекция'  # Тип дисциплины
                        
                        
                        online_diss = row.find('td', class_='diss').find('a', class_='webex')
                            
                        final = ''
                        # проверка на наличие онлайн занятия, если оно есть, то в аудиторию записывается ссылка на занятие
                        if online_diss == None:
                            final = row.find('td', class_="who-where").text.strip()
                            
                        else:
                            final = online_diss['href']  # аудитория
                                
                        
                        # main_dict[key_week][key_date]["audience"] = final  # аудитория           
            # res+=('-'*57)
                    res.append(time_start)
                    res.append(time_end)
                    res.append(teacher)
                    res.append(discipline)
                    res.append(type_of_discipline)
                    res.append(final)
                    res.append("конец")

            main_dict[key_week][key_date] = res  # список вида [день, тип недели, начало пары, конец пары, препод, дисциплина, тип дисциплины, аудитория или ссылка]    
        
        return(main_dict)