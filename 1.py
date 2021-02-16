import sys

import pygame
import pygame.display
import requests

pygame.init()
API_KEY = '40d1649f-0493-4b70-98ba-98533de7710b'
size = (600, 450)
screen = pygame.display.set_mode(size)


def geocode(address):
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/"
    geocoder_params = {
        "apikey": API_KEY,
        "geocode": address,
        "format": "json"}

    response = requests.get(geocoder_request, params=geocoder_params)

    if response:
        json_response = response.json()
    else:
        pass

    features = json_response["response"]["GeoObjectCollection"]["featureMember"]
    return features[0]["GeoObject"] if features else None


def get_coordinates(address):
    toponym = geocode(address)
    if not toponym:
        return None, None
    toponym_coodrinates = toponym["Point"]["pos"]
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
    return float(toponym_longitude), float(toponym_lattitude)


def get_ll_span(address):
    global parametr
    toponym = geocode(address)
    if not toponym:
        return (None, None)

    toponym_coodrinates = toponym["Point"]["pos"]
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

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
        map_request += "&" + f"pt={add_params[0]},{add_params[1]},pm2dgl"
    response = requests.get(map_request)

    if not response:
        pass

    map_file = "map.png"
    try:
        with open(map_file, "wb") as file:
            file.write(response.content)
    except IOError as ex:
        print("Ошибка записи временного файла:", ex)
        sys.exit(2)

    screen.blit(pygame.transform.scale(pygame.image.load(map_file), size), (0, 0))
    pygame.display.flip()

metka = False
def main():
    global parametr
    toponym_to_find = " ".join(sys.argv[1:])
    vid = 0
    if toponym_to_find:
        lat, lon = get_coordinates(toponym_to_find)
        spn = get_ll_span(toponym_to_find)
        ll_spn = f"ll={spn[0]}&spn={spn[1]}"
        show_map(ll_spn, "map")
        coords = [float(i) for i in spn[0].split(",")]
    metka = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                coords = [float(i) for i in spn[0].split(",")]
                spn = (str(coords[0]) + "," + str(coords[1]), spn[1])
                spn_list = list(map(float, spn[1].split(',')))
                coords = [float(i) for i in coords]
                a = 0.15
                if event.key == pygame.K_DOWN:
                    coords[1] -= spn_list[1] * a
                elif event.key == pygame.K_UP:
                    coords[1] += spn_list[1] * a
                elif event.key == pygame.K_RIGHT:
                    coords[0] += spn_list[0] * a
                elif event.key == pygame.K_LEFT:
                    coords[0] -= spn_list[0] * a
                elif event.key == pygame.K_q:
                    vid += 1
                    vid = vid % 3
                elif event.key == pygame.K_f:
                    ads = input()
                    crds = geocode(ads)["Point"]["pos"]
                    coords[0] = crds.split()[0]
                    coords[1] = crds.split()[1]
                    metka = [str(i) for i in coords]
                elif event.key == pygame.K_PAGEUP:
                    spn_list[0] = spn_list[0] * 2
                    spn_list[1] = spn_list[1] * 2
                elif event.key == pygame.K_PAGEDOWN:
                    spn_list[0] = spn_list[0] / 2
                    spn_list[1] = spn_list[1] / 2
                elif event.key == pygame.K_DELETE:
                    metka = False
                coords = [str(i) for i in coords]
                spn = [','.join(list(map(str, coords))), ','.join(list(map(str, spn_list)))]
                ll_spn = f"ll={coords[0]},{coords[1]}&spn={spn[1]}"

                if vid == 0:
                    show_map(ll_spn, "map", metka)
                if vid == 1:
                    show_map(ll_spn, "sat", metka)
                if vid == 2:
                    show_map(ll_spn, "skl", metka)


if __name__ == "__main__":
    main()
