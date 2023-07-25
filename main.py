import datetime
import os
import shutil
import time
import cv2 as cv
import numpy as np
import pymysql
'''
@Author：Himit_ZH
@Date: 2020.3.1
'''
# Подключение данных к базе данных
def PutDatatoSql(sname,sno):
    flag = 1
    con = pymysql.connect(host='localhost', password='123456', user='root', port=3306,db='facedata')
    # Создать объект курсора
    cur = con.cursor()
    # Определить, существует ли библиотека
    # Судя по тому, есть таблица или нет, автоматически создавать ее
    sql1 = r'''
                CREATE TABLE IF NOT EXISTS t_stu (
                id int PRIMARY KEY NOT NULL auto_increment,
                sname VARCHAR(20) NOT NULL,
                sno VARCHAR(14) NOT NULL,
                created_time DATETIME )
                 '''
    cur.execute(sql1)
    # Напишите sql для запроса данных
    sql2 = 'select * from t_stu where sname=%s and sno=%s'
    try:
        cur.execute(sql2,args=(sname,sno))
        con.commit()
        # Обработка набора результатов
        student = cur.fetchall()
        if student:
            con.close()
            flag = 2
            return flag
    except Exception as e:
        print(e)
        print("Не удалось запросить данные")
        flag = 0
        return flag
    # Напишите sql для вставки данных
    sql3 = 'insert into t_stu(sname,sno,created_time) values(%s,%s,%s)'
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        # Выполнить sql
        cur.execute(sql3, (sname,sno,dt))
        # Зафиксировать транзакцию
        con.commit()
        print("Вставить данные успешно")
        return flag
    except Exception as e:
        print(e)
        con.rollback()
        print("Не удалось вставить данные")
        flag = 0
        return flag
    finally:
        # Закрыть соединение
        con.close()



if __name__ == '__main__':
    while True:
        face_id = input("Пожалуйста, введите студенческий билет:")
        face_name = input("Пожалуйста, введите свое имя:")
        result = PutDatatoSql(face_name, face_id)
        if  result == 1:
            break
        elif result == 2:
            # В базе данных могут быть записи, но ресурсы изображений были удалены. В этом случае введите заново.
            if not os.path.exists('./Picture_resources/Stu_' + str(face_id)): # Папка существует?
                break
            elif not os.listdir("./Picture_resources/Stu_" + str(face_id)): # В папке есть файл
                break
            else:
                print("Пользователь уже существует!")
        else:
            print("Не удалось успешно подключиться к базе данных")
    print("Пожалуйста, посмотрите в камеру и начните собирать 300 изображений лиц за 3 секунды (нажмите ESC для принудительного выхода) ...")
    count = 0 # Подсчитать количество фото
    path = "./Picture_resources/Stu_" + str(face_id) # Путь хранения данных изображения лица
    # Читать видео
    cap=cv.VideoCapture(0)
    time.sleep(3) # Включите камеру после трехсекундной паузы
    while True:
        flag,frame=cap.read()
        #print('flag:',flag,'frame.shape:',frame.shape)
        if not flag:
            break
        # Оттенки серого
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        # Загрузить данные функции
        face_detector = cv.CascadeClassifier('haarcascade_frontalface_default.xml')
        faces = face_detector.detectMultiScale(gray, 1.2, 5)
        if not os.path.exists(path):  # Если соответствующей папки нет, автоматически генерируется
            os.makedirs(path)
        if len(faces) > 1: # Две фотографии в одном кадре отбрасываются. Причина: кто-то заходит случайно или могут быть ошибки в распознавании лиц.
            continue
        # Кадр для выбора лиц, для цикла для обеспечения динамического видеопотока в реальном времени, который может быть обнаружен
        for x, y, w, h in faces:
            cv.rectangle(frame, (x, y), (x + w, y + h), color=(0, 255, 0), thickness=2)
            count += 1
            cv.imwrite(path+'/'+str(count) + '.png', gray[y:y + h, x:x + w])
            # отображаемое изображение
            cv.imshow('Camera', frame)
        print("Количество успешно собранных фотографий лиц:"+str(count))
        if 27 == cv.waitKey(1) or count>=300: # Нажмите ESC для выхода, по умолчанию соберите 500 фото
            break
    # Закрыть ресурсы
    print("Фотосъемка прошла успешно, выйдите из программы через 3 секунды ...")
    time.sleep(3)
    cv.destroyAllWindows()
    cap.release()
