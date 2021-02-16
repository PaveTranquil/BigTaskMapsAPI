# Пользователь печатает в командной строке запрос,
# а наша задача состоит в том, чтобы найти координаты запрошенного объекта
# и показать его на карте, выбрав соответствующий масштаб и позицию карты

import pygame
import sys
import os
import requests

# Пусть наше приложение предполагает запуск в командной строке:
# python search_req.py Москва, ул. Ак. Королева, 12
# Тогда запрос к геокодеру формируется следующим образом:
# http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode=Москва, ул. Ак. Королева, 12&format=json

API_KEY = '40d1649f-0493-4b70-98ba-98533de7710b'


# Функция сборки запроса для геокодера
def geocode(address):
    # Собираем запрос для геокодера.
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/"
    geocoder_params = {
        "apikey": API_KEY,
        "geocode": address,
        "format": "json"}

    # Выполняем запрос.
    response = requests.get(geocoder_request, params=geocoder_params)

    if response:
        # Преобразуем ответ в json-объект
        json_response = response.json()
    else:
        # прочитать о методах обработки ошибок, статусов ошибок
        pass

    features = json_response["response"]["GeoObjectCollection"]["featureMember"]
    return features[0]["GeoObject"] if features else None


# Получаем координаты объекта по его адресу.
def get_coordinates(address):
    toponym = geocode(address)
    if not toponym:
        return None, None
    # Координаты центра топонима:
    toponym_coodrinates = toponym["Point"]["pos"]
    # Широта, долгота:
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
    return float(toponym_longitude), float(toponym_lattitude)


# Получаем параметры объекта для рисования карты вокруг него.
def get_ll_span(address):
    global parametr
    toponym = geocode(address)
    if not toponym:
        return (None, None)

    # Координаты центра топонима:
    toponym_coodrinates = toponym["Point"]["pos"]
    # Долгота и Широта :
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

    # Собираем координаты в параметр ll
    ll = ",".join([toponym_longitude, toponym_lattitude])
    a = toponym["boundedBy"]["Envelope"]["lowerCorner"]
    b = toponym["boundedBy"]["Envelope"]["upperCorner"]
    parametr = toponym_coodrinates
    spn = str(abs(float(a.split()[0]) - float(b.split()[0])) / 2) + "," + str \
        (abs(float(a.split()[1]) - float(b.split()[1])) / 2)
    return ll, spn


def show_map(ll_spn=None, map_type="map", add_params=None):
    if ll_spn:
        map_request = f"http://static-maps.yandex.ru/1.x/?{ll_spn}&l={map_type}"
    else:
        map_request = f"http://static-maps.yandex.ru/1.x/?l={map_type}"

    if add_params:
        map_request += "&" + add_params
    response = requests.get(map_request)

    if not response:
        pass

    # Запишем полученное изображение в файл.
    map_file = "map.png"
    try:
        with open(map_file, "wb") as file:
            file.write(response.content)
    except IOError as ex:
        print("Ошибка записи временного файла:", ex)
        sys.exit(2)

    # Инициализируем pygame
    pygame.init()
    screen = pygame.display.set_mode((600, 450))
    # Рисуем картинку, загружаемую из только что созданного файла.
    screen.blit(pygame.image.load(map_file), (0, 0))
    # Переключаем экран и ждем закрытия окна.
    pygame.display.flip()


def main():
    global parametr
    toponym_to_find = " ".join(sys.argv[1:])
    if toponym_to_find:
        # Показываем карту с фиксированным масштабом.
        lat, lon = get_coordinates(toponym_to_find)
        spn = get_ll_span(toponym_to_find)
        ll_spn = f"ll={spn[0]}&spn={spn[1]}"
        print(ll_spn)
        show_map(ll_spn, "map")
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                coords = [float(i) for i in spn[0].split(",")]
                print("CCCCCCCC", coords)
                if event.key == pygame.K_DOWN:
                    coords[0] -= 1
                elif event.key == pygame.K_UP:
                    coords[0] += 1
                elif event.key == pygame.K_RIGHT:
                    coords[1] -= 1
                elif event.key == pygame.K_LEFT:
                    coords[1] += 1
                print("ггггггггг", coords)
                coords = [str(i) for i in spn[0].split(",")]
                spn = (coords[0] + "," + coords[1], spn[1])
                ll_spn = f"ll={spn[0]}&spn={spn[1]}"
                show_map(ll_spn, "map")
                print("ADSAS")


if __name__ == "__main__":
    main()
