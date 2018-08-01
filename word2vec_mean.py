import string
from string import digits
import gensim
from pymongo import MongoClient
import pymongo
from bson.objectid import ObjectId
import numpy
from bson.binary import Binary
import pickle

con = MongoClient("localhost", 27017)
database = con.tfg

mean_word2vec = database.mean_word2vec
freeling_db = database.freeling_db #Tabla de reviews
string.punctuation += "¡¿€$" #Añadimos apertura de exclamación e interrogación del español, y símbolos de divisas

print("Cargando modelo...")
model = gensim.models.Word2Vec.load("modelo_entrenado.txt")
print("Modelo cargado.")
word_vectors = model.wv


# # # # # # FUNCTIONS # # # # # #
def query_names(): # Método que devuelve los nombres de los sitios que tienen reviews
    query = freeling_db.distinct('name')

    return query

def get_data(name): #Obtiene las reviews de un sitio determinado

    rev = freeling_db.find({'name': name}, {'_id': 0})

    return rev

# # # # # # # # # # # # # # # # # 

nombres = query_names() #Obtenemos los nombres de todos los sitios
rejected_words = []

for i in nombres:
    row = {}
    row['name'] = i #Nombre del sitio

    data = get_data(i) #Obtenemos todos los datos asociados a un sitio (reviews, tipo, etc.)
    for j in data:
        resultados = mean_word2vec.find({'original_review': j['original_review'], 'name': i})
        if(resultados.count() == 0): #Si la review no esta ya convertida a Word2Vec
            array_word2vec = []
            res = []
            media = []

            row['type'] = j['type']
            row['_id'] = ObjectId()
            row['original_review'] = j['original_review']
            row['rating'] = j['rating']

            s = j['parsed_string'].translate(str.maketrans('','',string.punctuation)) #Quitamos los signos de puntuación a la review.
            ar = s.split() # Creamos una lista de strings separando cada palabra de la review
            for i in range(len(ar)):
                if ar[i] in word_vectors.vocab:
                    palabra = list(model.wv[ar[i]])
                    array_word2vec.append(palabra) #Tenemos matriz con cada palabra convertida a vector de 200 dimensiones
                else:
                    rejected_words.append(ar[i]) #Recolectamos las palabras que no se encuentren en el vocabulario.

            '''
            print("Word2Vec:\n")
            print(array_word2vec)
            print("\n")
            '''
            if not array_word2vec:
                print("No se ha obtenido media de esta review. Quizá ninguna palabra estuviese en el vocabulario y no se pudiese convertir a Word2Vec.")
            else:
                media = numpy.mean(array_word2vec, axis=0)
                binary_media = Binary(pickle.dumps(media, protocol=2), subtype=128) #Convertimos array a binario para poder insertarlo.
                row['mean_vector'] = binary_media
                #print(row)
                mean_word2vec.insert(row)
                print("Inserted!\n")
        else:
            print("Already inserted!")

print("Palabras no aceptadas:")
print(rejected_words)
f = open('palabras_rechazadas.txt', 'w')
for item in rejected_words:
    f.write("%s\n" % item)
con.close()



