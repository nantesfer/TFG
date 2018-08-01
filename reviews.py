import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
import requests
import json

con = MongoClient('localhost', 27017)
db = con.tfg # Conectado a la BD "tfg"
places = db.places
reviews = db.reviews # Creamos tabla "reviews"

api_key = "your_api_key_here"

query = places.find({}, {'type': 1, 'name':1, 'place_id': 1, '_id': 0}) # SELECT places_id FROM places


for i in query:
    row = {}
    res = requests.get('https://maps.googleapis.com/maps/api/place/details/json?placeid='+i['place_id']+'&key='+api_key+'&language=es')
    json_data = res.json()

    if 'reviews' in json_data['result'].keys(): # Si el sitio tiene reviews
        for j in range(len(json_data['result']['reviews'])):
            resultados = reviews.find({'review': json_data['result']['reviews'][j]['text'], 'name': json_data['result']['name']}) # Hacemos un find a ver si la review ya está en la BD.
            if(resultados.count() == 0): # Si la review NO está en la BD, insertamos
                row['name'] = i['name']
                row['type'] = i['type']
                if 'rating' in json_data['result'].keys():
                    row['avg_rating'] = json_data['result']['rating'] # Valoración media del sitio
                row['location'] = {'lat': json_data['result']['geometry']['location']['lat'], 'lng': json_data['result']['geometry']['location']['lng']}
                if 'language' in json_data['result']['reviews'][j].keys():
                    row['language'] = json_data['result']['reviews'][j]['language'] # Idioma de la review
                row['rating'] = json_data['result']['reviews'][j]['rating'] # Valoración individual de la review
                row['review'] = json_data['result']['reviews'][j]['text'] # Review
                row['_id'] = ObjectId()  
                reviews.insert(row) #Insertamos en la BD
                print("Insertado\n")
            else:
                print("La review:\n '"+ json_data['result']['reviews'][j]['text']+"'\n ya está insertada")

'''
for i in query:
    row={}
    row['name'] = i['name']
    res = requests.get('https://maps.googleapis.com/maps/api/place/details/json?placeid='+i['place_id']+'&key='+api_key+'&language=es')
    json_data = res.json()
    row['avg_rating'] = "0"
    if 'rating' in json_data['result'].keys():
        row['avg_rating'] = json_data['result']['rating']
    row['location'] = {'lat': json_data['result']['geometry']['location']['lat'], 'lng': json_data['result']['geometry']['location']['lng']}
    row['type'] = i['type']
    row['reviews'] = ""

    if 'reviews' in json_data['result'].keys():
        inserted_reviews = reviews.find({'name': i['name']}, {'reviews': 1, '_id': 0}) # Obtener reviews ya insertadas del sitio.
        if(inserted_reviews.count() == 0): # El sitio no está insertado (por tanto no tiene reviews)
            reviews = {}
            for j in json_data['result']['reviews']:
                reviews[j] = {'text': json_data['result']['reviews'][j]['text'], 'language': json_data['result']['reviews'][j]['language'], 'rating': json_data['result']['reviews'][j]['rating']}
            row['reviews'] = reviews
            print(row) #Insert 
        else: # El sitio está en la BD con sus reviews
            for j in json_data['result']['reviews']:
                if(any(json_data['result']['reviews'][j]['text'] in d.values() for d in inserted_reviews['reviews'].values())): # Si la review ya está insertada
                    print("Review already inserted!")
                else:
                    length = len(inserted_reviews['reviews'])
                    reviews.update(
                        {'name': i['name']}, # Seleccionar la fila con el nombre del sitio
                        {
                            '$set': {
                                'reviews[%d]' % (length) : {'text': json_data['result']['reviews'][j]['text'], 'language': json_data['result']['reviews'][j]['language'], 'rating': json_data['result']['reviews'][j]['rating']}
                            }
                        
                        }
                    )

'''













con.close() # Cerrar conexión con BBDD.

