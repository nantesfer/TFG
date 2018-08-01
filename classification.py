import pymongo
from pymongo import MongoClient
from sklearn import svm
from sklearn.model_selection import train_test_split
import numpy as np
from bson.binary import Binary
import pickle
import matplotlib.pyplot as plt


import difflib

con = MongoClient("localhost", 27017)
db = con.tfg
mean_word2vec = db.mean_word2vec

vector_rating = [] #Vector de diccionarios con la review y su rating

resultados = mean_word2vec.find({}, {'_id': 0, 'mean_vector': 1, 'rating': 1}) #Obtenemos los vectores y sus valoraciones.

for i in resultados:
    vector_rating.append({'vector': list(pickle.loads(i['mean_vector'])), 'rating': i['rating']})

#Creamos dos listas: una lista de entrenamiento con el 80% de las reviews, y otra de testeo con el 20% restante.
samples = train_test_split(vector_rating, test_size=0.2, train_size=0.8, shuffle=False)

train_sample = samples[0]
test_sample = samples[1]

train_sample_vector = []
train_sample_rating = []

test_sample_vector = []
test_sample_expected_ratings = []


for i in range(len(train_sample)):
    train_sample_vector.append(train_sample[i]['vector']) #Meter en una matriz todos los vectores

for i in range(len(train_sample)):
    train_sample_rating.append(train_sample[i]['rating']) #Meter en una lista todas las ratings

for i in range(len(test_sample)):
    test_sample_vector.append(test_sample[i]['vector']) #Meter en una matriz todos los vectores

for i in range(len(test_sample)):
    test_sample_expected_ratings.append(test_sample[i]['rating']) #Meter en una lista todas las ratings esperadas.

#Así, ahora tenemos una lista de listas de tamaño n_muestras x n_características, que nos sirve como entrenamiento.

clf = svm.SVC(gamma=0.001, C=100.)
clf.fit(train_sample_vector, train_sample_rating) #Entrenamos con las reviews y sus valoraciones

predicted_ratings = clf.predict(test_sample_vector)

print("Valoraciones esperadas:")
print(test_sample_expected_ratings)
print("Valoraciones obtenidas con Scikit:")
print(predicted_ratings)

equal = 0

for x,y in zip(test_sample_expected_ratings, predicted_ratings):
    if x == y:
        equal += 1

print("Equal ratings: ",equal," out of 185.")

###################### DISPLAY RESULTS ##########################
diferencias = []
Y = [0,0,0,0,0]
X = [0,1,2,3,4]
for x,y in zip(test_sample_expected_ratings, predicted_ratings):
    if x < y:
        diferencias.append(y-x)
    else:
        diferencias.append(x-y)

for i in diferencias:
    if i == 0:
        Y[0] += 1
    if i == 1:
        Y[1] += 1
    if i == 2:
        Y[2] += 1
    if i == 3:
        Y[3] += 1
    if i == 4:
        Y[4] += 1

plt.bar(X, Y, width=0.8, color='r')

plt.show()