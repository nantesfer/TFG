import pyfreeling
import sys, os
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId

# Conexión con la base de datos
con = MongoClient('localhost', 27017)
db = con.tfg # Conectamos a la BD "tfg"
reviews = db.reviews # Tabla reviews.
freeling_db = db.freeling_db



################################ FREELING CONF FILES #################################

## Check whether we know where to find FreeLing data files
if "FREELINGDIR" not in os.environ :
   if sys.platform == "win32" or sys.platform == "win64" : os.environ["FREELINGDIR"] = "C:\\Program Files"
   else : os.environ["FREELINGDIR"] = "/usr/local"
   print("FREELINGDIR environment variable not defined, trying ", os.environ["FREELINGDIR"], file=sys.stderr)

if not os.path.exists(os.environ["FREELINGDIR"]+"/share/freeling") :
   print("Folder",os.environ["FREELINGDIR"]+"/share/freeling",
         "not found.\nPlease set FREELINGDIR environment variable to FreeLing installation directory",
         file=sys.stderr)
   sys.exit(1)

# Location of FreeLing configuration files.
DATA = os.environ["FREELINGDIR"]+"/share/freeling/";

# Init locales
pyfreeling.util_init_locale("default");

# create language detector. Used just to show it. Results are printed
# but ignored (after, it is assumed language is LANG)
la=pyfreeling.lang_ident(DATA+"common/lang_ident/ident-few.dat");

# create options set for maco analyzer. Default values are Ok, except for data files.
LANG="es"; # Se asume que se van a analizar textos en español.
op= pyfreeling.maco_options(LANG);
op.set_data_files( "", 
				DATA + "common/punct.dat",
				DATA + LANG + "/dicc.src",
				DATA + LANG + "/afixos.dat",
				"",
				DATA + LANG + "/locucions.dat", 
				DATA + LANG + "/np.dat",
				DATA + LANG + "/quantities.dat",
				DATA + LANG + "/probabilitats.dat");

# create analyzers
tk=pyfreeling.tokenizer(DATA+LANG+"/tokenizer.dat");
sp=pyfreeling.splitter(DATA+LANG+"/splitter.dat");
sid=sp.open_session();
mf=pyfreeling.maco(op);

# activate mmorpho odules to be used in next call
mf.set_active_options(False, True, True, True,  # select which among created 
					True, True, False, True,  # submodules are to be used. 
					True, True, True, True ); # default: all created submodules are used


# create tagger
tg=pyfreeling.hmm_tagger(DATA+LANG+"/tagger.dat",True,2);

print("Freeling initialized!\n")

######################################################################################

def query_names(): # Método que devuelve los nombres de los sitios que tienen reviews
    query = reviews.distinct('name')

    return query

def get_data(name): #Obtiene las reviews de un sitio determinado

    rev = reviews.find({'name': name, 'language': 'es'}, {'_id': 0})

    return rev

def freeling_analysis(lin, p_a_f_e, p_a_s): #Metodo que recibe la review, y la analiza con freeling para obtener la FC y la etiqueta.

    while(lin): #Mientras no se acabe el texto introducido
        l = tk.tokenize(lin) # Tokenizamos
        ls = sp.split(sid, l, True) # Dividimos la cadena
        ls = mf.analyze(ls) # Analizador morfológico
        ls = tg.analyze(ls) #Permite obtener entidades (lugares, nombres propios, etc)
        global parsed_string

        for s in ls:
            ws = s.get_words()
            for w in ws:

                parsed_string += w.get_lemma() + " "
                #print(p_s)
                #print("\n")
                p_a_s.append(w.get_lemma())
                #print(p_a_s)
                #print("\n")

                p_a_f_e.append({'FC': w.get_lemma(), 'Etiqueta': w.get_tag()})
                #print(p_a_f_e)
                #print("\n")


        break



####### MAIN #######

nombres = query_names() #Obtenemos los nombres de los sitios

for i in nombres:
    row={}
    row['name'] = i # Nombre del sitio

    data = get_data(i) #Obtenemos todos los datos asociados a un sitio (reviews, localización, rating, etc)
    for j in data:
        resultados = freeling_db.find({'original_review': j['review'], 'name': i})
        if(resultados.count() == 0): #Si la review no está ya analizada
            parsed_string=''
            parsed_array_string=[]
            parsed_array_fc_etiq=[]

            row['type'] = j['type']
            row['_id'] = ObjectId()
            row['rating'] = j['rating']
            row['original_review'] = j['review']
            
            
            freeling_analysis(row['original_review'], parsed_array_fc_etiq, parsed_array_string)
            
            row['parsed_string'] = parsed_string
            row['parsed_array_string'] = parsed_array_string
            row['parsed_array_fc_etiq'] = parsed_array_fc_etiq
            
            
            
            freeling_db.insert(row)
            print("Inserted!\n")
        else:
            print("Review already parsed!")


sp.close_session(sid)
con.close()