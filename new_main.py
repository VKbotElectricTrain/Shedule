import vk_api
import time
import csv
import datetime
import random
import requests
import json
from time import sleep
import codecs
from names import STATION_NAMES
import VK_Api
import Ya_Api

###################################################################################################
###################################################################################################
###################################################################################################



API_KEY = Ya_Api.token() # ключ к API яндекс.расписаний
VK_TOKEN = VK_Api.token() # токен для доступа к функциям VK API



###################################################################################################
###################################################################################################
###################################################################################################



def Time_Maker(): # озвращает текущую дату
    return  datetime.datetime.now().strftime('%Y-%m-%d')



###################################################################################################
###################################################################################################
###################################################################################################



def Time_To_Departure(departure_time):
    """
    time format: HH:MM
    """
    hours, minuites = list(map(int, departure_time.split(':')))
    c_hours, c_minuites = list(map(int, datetime.datetime.now().time().strftime('%H:%M').split(':')))
    t2 = 60*c_hours + c_minuites
    t1 = 60*hours + minuites
    if t2 <= t1:
        delta = t1 - t2
    elif t2 > t1:
        delta = 24*60 - abs(t2-t1)
    if (delta%60)//10 == 0:
        return str(delta//60) + ':0' + str(delta%60)
    else:
        return str(delta//60) + ':' + str(delta%60)


###################################################################################################
###################################################################################################
###################################################################################################



def get_schedule(from_depature,destination_depature,date):  # Возвращает расписание за весь день
    '''
    CODES-dict of station codes- must have been declared outer
    API_KEY - must have been also predeclared
    *
    date=YYYY-MM-DD
    '''
    from_depature=CODES[from_depature]
    destination_depature=CODES[destination_depature]
    url='https://api.rasp.yandex.net/v3.0/search/?apikey='+API_KEY+'&format=json&transport_types=suburban&from='+from_depature+'&to='+destination_depature+'&lang=ru_RU&page=1&date='+date
    resp = requests.get(url=url)
    return resp.json()



###################################################################################################
###################################################################################################
###################################################################################################


def forming_schedule(from_depature,destination_depature,date):
    '''
    date=YYYY-MM-DD
    '''
    raw_respond=get_schedule(from_depature,destination_depature,date)
    arrival_time=[]
    departure_time=[]
    thread=[]
    count = 0
    ### parsing raw respond in order to pass fucking exam
    for i in raw_respond['segments']:
        current_time = datetime.datetime.now().hour*60+datetime.datetime.now().minute
        hour_of_departure = int(i['departure'][-14:-6][:2])
        minute_of_departure = int(i['departure'][-14:-6][3:5])
        if (hour_of_departure*60 + minute_of_departure)>current_time and count <= 4:
            count += 1
            arrival_time.append(i['arrival'][11:16])
            departure_time.append(i['departure'][11:16])
            thread.append(i['thread']['title'])
    return departure_time, arrival_time, thread




###################################################################################################
###################################################################################################
###################################################################################################
def suggester(inputed_name, id_of_user):
    number_of_rec=0
    inputed_name = inputed_name.title()
    #print(inputed_name)
    if inputed_name not in STATION_NAMES:
        suggested_stations=[]
        for station_name in STATION_NAMES:
            if inputed_name in station_name:
                number_of_rec += 1
                suggested_stations.append(station_name)
                send_message(str(number_of_rec) + ': ' + station_name, id_of_user)
        if number_of_rec == 0:
            send_message('Такой станции нет, повторите ввод', id_of_user)
            #global iterator
            #iterator=not iterator
            return 0
        else:
            send_message('Введите номер нужной вам станции', id_of_user)
        for event2 in longpoll.listen():
            if event2.type == VkEventType.MESSAGE_NEW and event2.to_me and event2.text:
                chosen_rec_number=event2.text
                if chosen_rec_number not in [str(i) for i in range(1,number_of_rec+1)]:
                    send_message('Произошла ошибка, введите станцию заново',id_of_user)
                    return 0
                else:
                    return suggested_stations[int(chosen_rec_number)-1]
    return inputed_name

###################################################################################################
###################################################################################################
###################################################################################################

###################################################################################################
###################################################################################################
###################################################################################################



def send_message(text, id_of_user):
    vk.messages.send( #Отправляем сообщение
        user_id=id_of_user,
        message=text,
        random_id = random.randint(1000000000,100000000000)
        )



###################################################################################################
###################################################################################################
###################################################################################################



from vk_api.longpoll import VkLongPoll, VkEventType


with codecs.open("CODES.csv", 'r', encoding="UTF-8") as f:
    data = f.readlines() ######
data = list(map(lambda string: string.rstrip('\n').split(','), data))
CODES = dict(data)


vk_session = vk_api.VkApi(token=VK_TOKEN)
longpoll = VkLongPoll(vk_session)
vk = vk_session.get_api()
iterator=True
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
        if iterator:
            station_0=suggester(event.text, event.user_id )
            if station_0 == 0:
                continue
            if iterator and station_0:
                send_message(u'Теперь введите другую станцию', event.user_id)
                iterator = not iterator
            elif not iterator and station_0:
                iterator = not iterator
        else:
            station_1 = suggester(event.text, event.user_id)
            if station_1 == 0:
                continue
            if not iterator and station_1:
                send_message(u'Ожидайте...', event.user_id)
                print('break-point')
                try:
                    departures, arrivals, thread = forming_schedule(station_0, station_1, Time_Maker())
                except:
                    send_message(u'Произошла неизвестная ошибка. Требуется перезагрузка программы.', event.user_id)
                    continue
                if len(arrivals) == 0:
                    send_message('\tСоставление расписания невозможно: прямого маршрута не существует.\n Введите станции заново.', event.user_id)
                    iterator = not iterator
                else:
                    number_of_respond = 1
                    print(arrivals)
                    #send_message(u'  Отправление  Прибытие  Маршрут       Время до отправления', event.user_id)
                    for i in range(len(arrivals)):
                        print(i)
                        send_message(str(i+1) + ': ' + str(thread[i]) + '\n' + "#  Время отправления: " + str(departures[i])+ '\n' + "#  Время прибытия: " + str(arrivals[i]) + '\n' + "#  Время до отправления: " + str(Time_To_Departure(departures[i])) + '\n', event.user_id)
                        #send_message("\t Время отправления: " + str(departures[i]), event.user_id)
                        #send_message("\t Время прибытия: " + str(arrivals[i]), event.user_id)
                        #send_message("Маршрут: " + str(thread[i]), event.user_id)
                        #send_message("\tВремя до отправления: " + str(Time_To_Departure(departures[i])), event.user_id)
                        #send_message(str(number_of_respond) + ':    ' + str(departures[i]) + '      ' + str(arrivals[i]) + '     ' + str(thread[i]) + '        ' + str(Time_To_Departure(departures[i])), event.user_id)
                        #send_message( + '      ' +  + '     ' +  + '        ' +
                        number_of_respond += 1

                    iterator = not iterator
            else:
                iterator = not iterator
