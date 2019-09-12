import pandas as pd
import geopandas
from shapely.geometry import Point
import matplotlib.pyplot as plt
import psycopg2
import fiona; fiona.supported_drivers
from unidecode import unidecode

db = psycopg2.connect(user = "postgres", password = "psql", host = "localhost", database = "postgres")
cursor = db.cursor()
cursor.execute("select distinct(concelho) from cont_aad_caop2017 order by 1;")
results = cursor.fetchall()
districts = []
for row in results:
    districts.append(row[0])
ccount = []
for i in districts:
    cursor.execute("select count(final_point) from cont_aad_caop2017,taxi_services where st_contains(geom,final_point) and distrito ilike '"+i+"';")
    results_1 = cursor.fetchone()
    ccount.append(results_1[0])
db.close()

url = '/home/tito/TABD/Cont_AAD_CAOP2017.shp'
portugal = geopandas.read_file(url, encoding='utf-8')
total_count = []

for row in portugal.Distrito:
    i = 0
    while i < len(districts):
        if(row.encode('utf-8') == districts[i]):
            total_count.append(ccount[i])
        i = i + 1

portugal['total'] = total_count
portugal.plot(column='total', cmap='OrRd', scheme='quantiles')
plt.show()
