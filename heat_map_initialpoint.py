import pandas as pd
import folium
from folium.plugins import HeatMap
import psycopg2
import geopandas as gpd
from unidecode import unidecode
import branca.colormap as cm

#Conexao a Base de dados
db = psycopg2.connect(user = "postgres", password = "psql", host = "localhost", database = "postgres")

#Query para recolher os nomes dos concelhos e as suas respetivas posicoes
#st_y e st_x estao ao contrario para dar correto no mapa
cursor = db.cursor()
cursor.execute("select concelho,st_y(st_centroid(st_collect(geom))),st_x(st_centroid(st_collect(geom)))"\
  " from cont_aad_caop2017 group by 1 order by 1;")
results = cursor.fetchall()
lat = []
log = []
conc = []
amount = []

#Adicionar os resultados aos arrays
for row in results:
    conc.append(row[0])
    lat.append(row[1])
    log.append(row[2])

#Query para obter o numero de servicos em cada concelho
for i in conc:
    cursor.execute("select count(initial_point) from cont_aad_caop2017,"\
      "taxi_services where st_contains(geom,initial_point) and concelho ilike '"+i+"';")
    result = cursor.fetchone()
    amount.append(result[0])

#Criacao da Estrutura de dados
for_map = pd.DataFrame()
for_map['concelho'] = conc
for_map['latitude'] = lat
for_map['longitude'] = log
for_map['amount'] = amount
max_amount = float(for_map['amount'].max())

#Configuracao do Mapa
hmap = folium.Map(location=[38.6817,-7.996], zoom_start=7)
hm_wide = HeatMap(list(zip(for_map.latitude.values, for_map.longitude.values, for_map.amount.values)),
                   min_opacity=0.2,
                   max_val=max_amount,
                   radius=13, blur=10,
                   max_zoom=1,)

#Configuracao da Barra 
colors=["#3333ff","#42f4f4","#ffff00","#cc0000"]
colormap = cm.LinearColormap(colors).to_step(10).scale(0,50000)
colormap.caption = 'Numero de servicos'

hmap.add_child(colormap)
hmap.add_child(hm_wide)
hmap.save('teste.html')