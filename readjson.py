import json
import psycopg2

#Conexao com o banco de dados
try:
    conn = psycopg2.connect("dbname = 'smartmob' port = ''  user= '' password = '' host='localhost'")
except:
    print 'Erro'
cur = conn.cursor()

# Abrindo o arquivo json e transformando em um dicionario
with open('b1k3labapp-export.json') as file_json:
    json_data = json.loads(file_json.read())

dados = json_data["users"]
i = 0
for user in dados:
    # Inserindo os usuarios na tabela de usuarios
    cur.execute ("""INSERT INTO usuario (usuario) VALUES ('%s');"""% user)
    conn.commit()
    
    for data in dados[user]:
        # Inserindo os usuarios e a data na tabela das rotas
       cur.execute ("""INSERT INTO rota (id_usuario, dia) VALUES ('%s', '%s');"""% (user, data))
       conn.commit()
       for rota in dados[user][data]:
           # Enumerando as rotas
            i = i + 1

            for pts in dados[user][data][rota]:
               db = pts["db"]
               distance = pts["distance"]
               latitude = pts["latitude"]
               longitude = pts["longetude"]
               velocidade = pts["speed"]
               # Inserindo os dados dos pontos na tabela de coletas
               cur.execute ("""INSERT INTO coletas (id_rota, dist, db, veloc, lati, longi) VALUES ('%s','%s','%s','%s','%s','%s');"""% (i, distance, db, velocidade, latitude, longitude))
               conn.commit()
# Preenchendo a coluna de geometria da tabela das coletas (WGS84)
cur.execute ("""UPDATE coletas SET geom = ST_SetSRID(ST_MakePoint(longi::double precision,lati::double precision),4326) WHERE lati <> '' AND longi <> '';""")
conn.commit()
#Preenchendo a coluna de geometria em UTM da tabela das coletas (WGS84 UTM)
cur.execute("""UPDATE coletas SET geom_utm = ST_Transform(geom, 32722);""")
conn.commit()
# Criando uma view para fazer as rotas na geometria de linha
cur.execute("""CREATE VIEW temporaria AS SELECT C.id_rota, ST_MakeLine(C.geom) AS geom
	FROM (SELECT id_rota, id_ponto, geom 
		FROM coletas ORDER BY coletas.id_ponto ASC) AS C
	GROUP BY C.id_rota;""")
conn.commit()
# Preenchendo a coluna de geometria da tabela das rotas
cur.execute("""UPDATE rota AS rota SET geom = temporaria.geom FROM temporaria AS temporaria WHERE rota.id_rota = temporaria.id_rota;""")
conn.commit()

cur.close()
conn.close()
