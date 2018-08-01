import pymongo
from pymongo import MongoClient
import requests
import json


def placeid_request(api_key, location, radius, keyword):
    '''
    Esta petición devuelve un JSON con todos los lugares
    que estén en el radio radius, partiendo desde el lugar
    location, y que coincidian con keyword
    '''
    res = requests.get('https://maps.googleapis.com/maps/api/place/nearbysearch/json?key='+api_key+'&location='+location+'&radius='+radius+'&keyword='+keyword)
    json_data = res.json()
    return json_data

def insert_places(data):
    '''
    Insertar en la base de datos el nombre, place_id y raw JSON en BBDD.
    ''' 

    for i in range(len(data['results'])):
        resultados = places.find({'place_id': data['results'][i]['place_id']}, {'place_id':1, '_id':0}) # Consultamos la BD a ver si hay un sitio insertado con ese place_id

        if(resultados.count() == 0): # Si el sitio no esta en la BD, insertamos        
            place = {'name': data['results'][i]['name'], 'place_id': data['results'][i]['place_id'], 'JSON': data['results'][i], 'type': keyword}
            places.insert(place)
            #print(place)
        else:
            print(data['results'][i]['name']+" already inserted!\n")

    
    print(keyword+ " insertado!")




# Conexion con la base de datos.
con = MongoClient('localhost', 27017)
db = con.tfg # Conectado a la BD "tfg"

api_key = "your_api_key_here"
meridiano = "28.45692,-16.260844" # Centro Comercial Meridiano, S/C.
plaza_charco = "28.4159607,-16.5505253" # Plaza del Charco, Puerto de la Cruz.
plaza_españa = "28.4680087,-16.249337" # Plaza de España, Santa Cruz de Tenerife.
plaza_adelantado = "28.4875287,-16.3157637" # Plaza del Adelantado, La Laguna.
tienda_costa_adeje = "28.0854407,-16.7287703" # Tienda Yoigo en Costa Adeje.
hospital_los_cristianos = "28.0586742,-16.7251284" # Hospiten Sur en Los Cristianos.
radius = "3500" # 2000 metros de radio.
keyword = "playa" # Buscamos places_id de hoteles.

datos = placeid_request(api_key, tienda_costa_adeje, radius, keyword)

places = db.places # Elegimos la tabla (o coleccion) "places"
# Creamos indice en el campo "name" para evitar duplicados.

insert_places(datos)
# Proyección de la columna place_id.
# for i in places.find():
    #print (i['place_id'])















con.close() # Cerrar conexión con BBDD.


