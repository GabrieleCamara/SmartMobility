#!/usr/bin/python
#-*-encoding:utf-8-*-

import cgi, os.path, sys
import psycopg2

form = cgi.FieldStorage()
user_code = int(form['user_code'].value)
num_modal = int(form['num_modal'].value)
tema = int(form['tema'].value)
num_rota = int(form['num_rota'].value)

try:
	conn = psycopg2.connect("dbname = 'smartmob' port = '5432'  user= 'user' password = 'user' host='localhost'")
	cursor = conn.cursor()
except:
	print 'Erro'

# consulta para comboBox usuarios
cursor.execute("""CREATE OR REPLACE VIEW usuario_selec AS SELECT * FROM rotas_filtradas WHERE id=%s""" %(user_code))

# consulta para comboBox rota
cursor.execute("""CREATE OR REPLACE VIEW rota_selec AS SELECT * FROM rotas_filtradas WHERE id_rota=%s;""" %(num_rota))
cursor.execute("""CREATE OR REPLACE VIEW rota_selec_usuario_selec AS SELECT * FROM rotas_filtradas WHERE id=%s;""" %(user_code))

# consulta para comboBox tema
# tema: DB - Todas as rotas/Todos os usuarios
# LINHA
cursor.execute("""CREATE OR REPLACE VIEW osm_db_rota AS SELECT row_number() OVER (PARTITION BY true) as id, osm_db.osm_id, ponto_rua.id_rota, osm_db.geom, osm_db.db_medio
FROM osm_db, ponto_rua
WHERE ponto_rua.osm_id = osm_db.gid;""")
#PONTO
cursor.execute("""CREATE OR REPLACE VIEW db_coletas AS SELECT * FROM coletas_filtradas;""")
# tema: DB - Rota selecionada/Todos os usuarios
# LINHA
cursor.execute("""CREATE OR REPLACE VIEW db_rota_selec AS SELECT * FROM osm_db_rota WHERE id_rota = %s;"""%(num_rota))
# PONTO
cursor.execute("""CREATE OR REPLACE VIEW db_coletas_selec AS SELECT * FROM coletas_filtradas WHERE id_rota = %s;"""%(num_rota))
# tema: DB - Todas as rotas/Usuarios selecionados
# LINHA
cursor.execute("""CREATE OR REPLACE VIEW db_rota_usuario_selec AS SELECT * FROM db_rota_usuarios WHERE id_user = %s;""" %(user_code))
# PONTO
cursor.execute("""CREATE OR REPLACE VIEW db_coletas_usuarios_selec AS SELECT * FROM db_coletas_usuarios WHERE id_user = %s;""" %(user_code))
# tema: DB - Rotas selecionadas /Usuarios selecionados
# LINHA
cursor.execute("""CREATE OR REPLACE VIEW db_rota_selec_usuario_selec AS SELECT * FROM db_rota_usuarios WHERE id_user = %s AND id_rota = %s;""" %(user_code, num_rota))
# PONTO
cursor.execute("""CREATE OR REPLACE VIEW db_coletas_selec_usuarios_selec AS SELECT * FROM db_coletas_usuarios WHERE id_user = %s AND id_rota = %s;""" %(user_code, num_rota))

# consulta para comboBox tema
# tema: VELOCIDADE - Todas as rotas/Todos os usuarios
# LINHA
cursor.execute("""CREATE OR REPLACE VIEW osm_veloc_rota AS
SELECT row_number() OVER (PARTITION BY true) as id, osm_veloc.osm_id, ponto_rua_veloc.id_rota, osm_veloc.geom, osm_veloc.veloc_medio
FROM osm_veloc, ponto_rua_veloc
WHERE ponto_rua_veloc.osm_id = osm_veloc.gid;""")
#PONTO
cursor.execute("""CREATE OR REPLACE VIEW veloc_coletas AS SELECT * FROM coletas_filtradas;""")
# tema: VELOCIDADE - Rota selecionada/Todos os usuarios
# LINHA
cursor.execute("""CREATE OR REPLACE VIEW veloc_rota_selec AS SELECT * FROM osm_veloc_rota WHERE id_rota = %s;"""%(num_rota))
# PONTO
cursor.execute("""CREATE OR REPLACE VIEW veloc_coletas_selec AS SELECT * FROM coletas_filtradas WHERE id_rota = %s;"""%(num_rota))
# tema: VELOCIDADE - Todas as rotas/Usuarios selecionados
# LINHA
cursor.execute("""CREATE OR REPLACE VIEW veloc_rota_usuario_selec AS SELECT * FROM veloc_rota_usuarios WHERE id_user = %s;""" %(user_code))
# PONTO
cursor.execute("""CREATE OR REPLACE VIEW veloc_coletas_usuarios_selec AS SELECT * FROM veloc_coletas_usuarios WHERE id_user = %s;""" %(user_code))
# tema: VELOCIDADE - Rotas selecionadas /Usuarios selecionados
# LINHA
cursor.execute("""CREATE OR REPLACE VIEW veloc_rota_selec_usuario_selec AS SELECT * FROM veloc_rota_usuarios WHERE id_user = %s AND id_rota = %s;""" %(user_code, num_rota))
# PONTO
cursor.execute("""CREATE OR REPLACE VIEW veloc_coletas_selec_usuarios_selec AS SELECT * FROM veloc_coletas_usuarios WHERE id_user = %s AND id_rota = %s;""" %(user_code, num_rota))

# consulta para comboBox modal
cursor.execute("""CREATE OR REPLACE VIEW rota_modal AS SELECT * FROM rotas_filtradas""")
# consulta para comboBox modal selecionado
cursor.execute("""CREATE OR REPLACE VIEW rota_modal_selec AS SELECT * FROM rotas_filtradas WHERE modal=%s"""%(num_modal))

# retorna lista de usuarios
def lista_usuarios():
	usuarios = []
	cursor.execute("""SELECT id, usuario FROM usuario""")
	usuarios.insert(0, 'Todos')
	for id,user in cursor:
		usuarios.append((id,user))
	return usuarios

# retorna lista de rotas
def lista_rotas():
    rotas = []
    cursor.execute("""SELECT id_rota FROM rota ORDER BY id_rota ASC""")
    rotas.insert(0, '')
    rotas.insert(1, 'Todas')
    for rote in cursor:
        rotas.append(rote)
    return rotas

# retorna lista com os temas dos mapas
def lista_tema():
    db = 'Decibeis'
    veloc = 'Velocidade'
    tema = ['', db, veloc]
    return tema

# retorna lista com os tipos de modais
def lista_modal():
	modais = []
	cursor.execute("""SELECT DISTINCT ON(modal)  rota.modal AS modal_ind FROM rota ORDER BY modal ASC;""")
	modais.insert(0, '')
	modais.insert(1, 'Todos')
	resposta = cursor.fetchall()
	for modal in resposta:
		if modal[0] == 1:
			modais.append('A pe')
		elif modal[0] == 2:
			modais.append('Bicicleta')
		elif modal[0] == 3:
			modais.append('Onibus')
		elif modal[0] == 4:
			modais.append('Carro')
		else:
			modais.append('Sem modal')
	return modais
    
print 'Content-Type: text/html\n\n'
print '<!DOCTYPE html>'
print '<head>'
print '<title>Smart Mobility</title>'
print '<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1.0"/>'
print '<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet"/>'
print '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css">'
print '<script src="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js"></script>'
print '<script src="https://api.mapbox.com/mapbox.js/v3.1.1/mapbox.js"></script>'
print '<link href="https://api.mapbox.com/mapbox.js/v3.1.1/mapbox.css" rel="stylesheet" />'
print """<style>
body {
    margin: 0px;
    padding: 0px;
}
select {
    width: 150px;
	height: 30px;
    display: inline-block;
}
div#opcoes {
    display: inline;
}
#map {
    position: absolute;
    top: 120px;
    bottom: 0;
    width: 100%;
}
</style>"""
print '</head>'
print '<body>'
print '<nav class="black lighten-2" role="navigation">'
print '<div class="nav-wrapper">'
print '<a class="brand-logo center">Smart Mobility</a>'
print '<ul class="left hide-on-med-and-down">'
print '<li><a href="#"><i class="material-icons">menu</i></a></li>'
print '</ul>'
print '</div>'
print '</nav>'
print '<nav class="grey darker-1" role="navigation">'
print '<div class="nav-wrapper">'
print '<ul>'
print '<form method="POST" action="smartmob_2.py">'
print '<div id="opcoes" class="input-field col s12">'
print '<li>Classificacao por usuario:'
print '<select name="user_code">'

for id,user in enumerate(lista_usuarios()):
	print '<option value = "' + str(id)+'">'+str(user)+'</option>'
    
print '</select>'
print '</li>'
print '</div>'
print '<div id="opcoes" class="input-field col s12">'
print '<li>Classificacao por modal:'
print '<select name="num_modal">'

for index,modal in enumerate(lista_modal()):
	print '<option value = "' + str(index)+'">'+str(modal)+'</option>'

print '</select>'
print '</li>'
print '</div>'
print '<div id="opcoes" class="input-field col s12">'
print '<li>Classificacao por tema:'
print '<select name="tema">'

for index,theme in enumerate(lista_tema()):
	print '<option value = "' + str(index)+'">'+str(theme)+'</option>'

print '</select>'
print '</li>'
print '</div>'
print '<div id="opcoes" class="input-field col s12">'
print '<li>Classificacao por rota:'
print '<select name="num_rota">'

for index,rote in enumerate(lista_rotas()):
	print '<option value = "' + str(index)+'">'+str(rote)+'</option>'

print '</select>'
print '</li>'
print '</div>'
print '<div><input type="submit" value="Enviar"></div>'
print '</ul>'
print '</form>'
print '</div>'
print '</nav>'
print '<div id="map"></div>'

# Todos os usuarios
if user_code == 0:
	if num_modal == 0:
		# Sem tema selecionado
		if tema == 0:
			# Todas as rotas
			if num_rota == 0:
				print """  <script>
				L.mapbox.accessToken = 'pk.eyJ1IjoiZ2FicmllbGVjYW1hcmEiLCJhIjoiY2pmMnJhcjJzMDVuMzJxbjg5aXYydjl5bCJ9.Lt4VQQDajTeH7ksmyzGqsg';
				var map = L.mapbox.map('map').setView([-25.45,-49.26], 14);
				map.options.minZoom = 14;
				L.mapbox.styleLayer('mapbox://styles/mapbox/dark-v9').addTo(map);
				var wmsLayer_user = L.tileLayer.wms('http://localhost:8082/geoserver/smartmob/wms', {
				layers: 'smartmob:rotas_todos_usuario',
				transparent: 'true',
				format: 'image/png',
				}).addTo(map);
				wmsLayer_user.options.minZoom = 13;
				wmsLayer_user.options.maxZoom = 17;
				
				</script>"""
			elif num_rota == 1:
				print """  <script>
				L.mapbox.accessToken = 'pk.eyJ1IjoiZ2FicmllbGVjYW1hcmEiLCJhIjoiY2pmMnJhcjJzMDVuMzJxbjg5aXYydjl5bCJ9.Lt4VQQDajTeH7ksmyzGqsg';
				var map = L.mapbox.map('map').setView([-25.45,-49.26], 14);
				map.options.minZoom = 14;
				L.mapbox.styleLayer('mapbox://styles/mapbox/dark-v9').addTo(map);
				var wmsLayer_user = L.tileLayer.wms('http://localhost:8082/geoserver/smartmob/wms', {
				layers: 'smartmob:rotas_todos_usuario',
				transparent: 'true',
				format: 'image/png',
				}).addTo(map);
				wmsLayer_user.options.minZoom = 13;
				wmsLayer_user.options.maxZoom = 17;
				</script>"""
			# Rotas selecionadas de todos os usuarios
			else:
				print """  <script>
				L.mapbox.accessToken = 'pk.eyJ1IjoiZ2FicmllbGVjYW1hcmEiLCJhIjoiY2pmMnJhcjJzMDVuMzJxbjg5aXYydjl5bCJ9.Lt4VQQDajTeH7ksmyzGqsg';
				var map = L.mapbox.map('map').setView([-25.45,-49.26], 14);
				map.options.minZoom = 14;
				L.mapbox.styleLayer('mapbox://styles/mapbox/dark-v9').addTo(map);
				var wmsLayer_user = L.tileLayer.wms('http://localhost:8082/geoserver/smartmob/wms', {
				layers: 'smartmob:rota_selec',
				transparent: 'true',
				format: 'image/png',
				}).addTo(map);
				wmsLayer_user.options.minZoom = 13;
				wmsLayer_user.options.maxZoom = 17;
				</script>"""
		# Com tema selecionado (DB)
		elif tema == 1:
			# Com todas as rotas
			if num_rota == 0:
				# osm_db_rota
				print """  <script>
				L.mapbox.accessToken = 'pk.eyJ1IjoiZ2FicmllbGVjYW1hcmEiLCJhIjoiY2pmMnJhcjJzMDVuMzJxbjg5aXYydjl5bCJ9.Lt4VQQDajTeH7ksmyzGqsg';
				var map = L.mapbox.map('map').setView([-25.45,-49.26], 14);
				map.options.minZoom = 14;
				L.mapbox.styleLayer('mapbox://styles/mapbox/dark-v9').addTo(map);
				/* LINHA */
				var wmsLayer_user = L.tileLayer.wms('http://localhost:8082/geoserver/smartmob/wms', {
				layers: 'smartmob:db_rota',
				transparent: 'true',
				format: 'image/png',
				}).addTo(map);
				wmsLayer_user.options.minZoom = 13;
				wmsLayer_user.options.maxZoom = 17;
				
				/* PONTO */
				var wmsLayer = L.tileLayer.wms('http://localhost:8082/geoserver/smartmob/wms', {
				layers: 'smartmob:db_coletas',
				transparent: 'true',
				format: 'image/png',
				}).addTo(map);
				wmsLayer.options.minZoom = 17;
				wmsLayer.options.maxZoom = 18;
				</script>"""
			# Tema selecionado para rotas especificas
			else: 
				print """  <script>
				L.mapbox.accessToken = 'pk.eyJ1IjoiZ2FicmllbGVjYW1hcmEiLCJhIjoiY2pmMnJhcjJzMDVuMzJxbjg5aXYydjl5bCJ9.Lt4VQQDajTeH7ksmyzGqsg';
				var map = L.mapbox.map('map').setView([-25.45,-49.26], 14);
				map.options.minZoom = 14;
				L.mapbox.styleLayer('mapbox://styles/mapbox/dark-v9').addTo(map);
				/* LINHA */
				var wmsLayer_user = L.tileLayer.wms('http://localhost:8082/geoserver/smartmob/wms', {
				layers: 'smartmob:db_rota_selec',
				transparent: 'true',
				format: 'image/png',
				}).addTo(map);
				wmsLayer_user.options.minZoom = 13;
				wmsLayer_user.options.maxZoom = 17;
				
				/* PONTO */
				var wmsLayer = L.tileLayer.wms('http://localhost:8082/geoserver/smartmob/wms', {
				layers: 'smartmob:db_coletas_selec',
				transparent: 'true',
				format: 'image/png',
				}).addTo(map);
				wmsLayer.options.minZoom = 17;
				wmsLayer.options.maxZoom = 18;
				</script>"""
		# Com tema selecionado (VELOCIDADE)
		else:
			# Com todas as rotas
			if num_rota == 0:
				#osm veloc rota
				print """  <script>
				L.mapbox.accessToken = 'pk.eyJ1IjoiZ2FicmllbGVjYW1hcmEiLCJhIjoiY2pmMnJhcjJzMDVuMzJxbjg5aXYydjl5bCJ9.Lt4VQQDajTeH7ksmyzGqsg';
				var map = L.mapbox.map('map').setView([-25.45,-49.26], 14);
				map.options.minZoom = 14;
				L.mapbox.styleLayer('mapbox://styles/mapbox/dark-v9').addTo(map);
				/* LINHA */
				var wmsLayer_user = L.tileLayer.wms('http://localhost:8082/geoserver/smartmob/wms', {
				layers: 'smartmob:veloc_rota',
				transparent: 'true',
				format: 'image/png',
				}).addTo(map);
				wmsLayer_user.options.minZoom = 13;
				wmsLayer_user.options.maxZoom = 17;
				
				/* PONTO */
				var wmsLayer = L.tileLayer.wms('http://localhost:8082/geoserver/smartmob/wms', {
				layers: 'smartmob:veloc_coletas',
				transparent: 'true',
				format: 'image/png',
				}).addTo(map);
				wmsLayer.options.minZoom = 17;
				wmsLayer.options.maxZoom = 18;
				</script>"""
			else:
				print """  <script>
				L.mapbox.accessToken = 'pk.eyJ1IjoiZ2FicmllbGVjYW1hcmEiLCJhIjoiY2pmMnJhcjJzMDVuMzJxbjg5aXYydjl5bCJ9.Lt4VQQDajTeH7ksmyzGqsg';
				var map = L.mapbox.map('map').setView([-25.45,-49.26], 14);
				map.options.minZoom = 14;
				L.mapbox.styleLayer('mapbox://styles/mapbox/dark-v9').addTo(map);
				/* LINHA */
				var wmsLayer_user = L.tileLayer.wms('http://localhost:8082/geoserver/smartmob/wms', {
				layers: 'smartmob:veloc_rota_selec',
				transparent: 'true',
				format: 'image/png',
				}).addTo(map);
				wmsLayer_user.options.minZoom = 13;
				wmsLayer_user.options.maxZoom = 17;
				
				/* PONTO */
				var wmsLayer = L.tileLayer.wms('http://localhost:8082/geoserver/smartmob/wms', {
				layers: 'smartmob:veloc_coletas_selec',
				transparent: 'true',
				format: 'image/png',
				}).addTo(map);
				wmsLayer.options.minZoom = 17;
				wmsLayer.options.maxZoom = 18;
				</script>"""
	# Modal selecionado - TODOS
	elif num_modal == 1:
		if tema == 0:
			if num_rota == 0:
				print """  <script>
				L.mapbox.accessToken = 'pk.eyJ1IjoiZ2FicmllbGVjYW1hcmEiLCJhIjoiY2pmMnJhcjJzMDVuMzJxbjg5aXYydjl5bCJ9.Lt4VQQDajTeH7ksmyzGqsg';
				var map = L.mapbox.map('map').setView([-25.45,-49.26], 14);
				map.options.minZoom = 14;
				L.mapbox.styleLayer('mapbox://styles/mapbox/dark-v9').addTo(map);
				var wmsLayer_user = L.tileLayer.wms('http://localhost:8082/geoserver/smartmob/wms', {
				layers: 'smartmob:rota_modal',
				transparent: 'true',
				format: 'image/png',
				}).addTo(map);
				wmsLayer_user.options.minZoom = 13;
				wmsLayer_user.options.maxZoom = 17;
				</script>"""
	else:
		if tema == 0:
			if num_rota == 0:
				print """  <script>
				L.mapbox.accessToken = 'pk.eyJ1IjoiZ2FicmllbGVjYW1hcmEiLCJhIjoiY2pmMnJhcjJzMDVuMzJxbjg5aXYydjl5bCJ9.Lt4VQQDajTeH7ksmyzGqsg';
				var map = L.mapbox.map('map').setView([-25.45,-49.26], 14);
				map.options.minZoom = 14;
				L.mapbox.styleLayer('mapbox://styles/mapbox/dark-v9').addTo(map);
				var wmsLayer_user = L.tileLayer.wms('http://localhost:8082/geoserver/smartmob/wms', {
				layers: 'smartmob:rota_modal_selec',
				transparent: 'true',
				format: 'image/png',
				}).addTo(map);
				wmsLayer_user.options.minZoom = 13;
				wmsLayer_user.options.maxZoom = 17;
				</script>"""
# Usuario especifico
else:
	if num_modal == 0:
		# Sem tema selecionado
		if tema == 0:
			if num_rota == 0:
				print """  <script>
				L.mapbox.accessToken = 'pk.eyJ1IjoiZ2FicmllbGVjYW1hcmEiLCJhIjoiY2pmMnJhcjJzMDVuMzJxbjg5aXYydjl5bCJ9.Lt4VQQDajTeH7ksmyzGqsg';
				var map = L.mapbox.map('map').setView([-25.45,-49.26], 14);
				map.options.minZoom = 14;
				L.mapbox.styleLayer('mapbox://styles/mapbox/dark-v9').addTo(map);
				var wmsLayer_user = L.tileLayer.wms('http://localhost:8082/geoserver/smartmob/wms', {
				layers: 'smartmob:usuario_selec',
				transparent: 'true',
				format: 'image/png',
				}).addTo(map);
				wmsLayer_user.options.minZoom = 13;
				wmsLayer_user.options.maxZoom = 17;
				</script>"""
			# Rotas selecionadas dos usuarios selecionados
			else:
				print """  <script>
				L.mapbox.accessToken = 'pk.eyJ1IjoiZ2FicmllbGVjYW1hcmEiLCJhIjoiY2pmMnJhcjJzMDVuMzJxbjg5aXYydjl5bCJ9.Lt4VQQDajTeH7ksmyzGqsg';
				var map = L.mapbox.map('map').setView([-25.45,-49.26], 14);
				map.options.minZoom = 14;
				L.mapbox.styleLayer('mapbox://styles/mapbox/dark-v9').addTo(map);
				var wmsLayer_user = L.tileLayer.wms('http://localhost:8082/geoserver/smartmob/wms', {
				layers: 'smartmob:rota_selec_usuario_selec',
				transparent: 'true',
				format: 'image/png',
				}).addTo(map);
				wmsLayer_user.options.minZoom = 13;
				wmsLayer_user.options.maxZoom = 17;
				</script>"""
		# Com tema selecionado
		elif tema == 1:
			if num_rota == 0:
				print """  <script>
				L.mapbox.accessToken = 'pk.eyJ1IjoiZ2FicmllbGVjYW1hcmEiLCJhIjoiY2pmMnJhcjJzMDVuMzJxbjg5aXYydjl5bCJ9.Lt4VQQDajTeH7ksmyzGqsg';
				var map = L.mapbox.map('map').setView([-25.45,-49.26], 14);
				map.options.minZoom = 14;
				L.mapbox.styleLayer('mapbox://styles/mapbox/dark-v9').addTo(map);
				/* LINHA */
				var wmsLayer_user = L.tileLayer.wms('http://localhost:8082/geoserver/smartmob/wms', {
				layers: 'smartmob:db_rota_usuario_selec',
				transparent: 'true',
				format: 'image/png',
				}).addTo(map);
				wmsLayer_user.options.minZoom = 13;
				wmsLayer_user.options.maxZoom = 17;
				
				/* PONTO */
				var wmsLayer = L.tileLayer.wms('http://localhost:8082/geoserver/smartmob/wms', {
				layers: 'smartmob:db_coletas_usuarios_selec',
				transparent: 'true',
				format: 'image/png',
				}).addTo(map);
				wmsLayer.options.minZoom = 17;
				wmsLayer.options.maxZoom = 18;
				</script>"""
			# Rotas selecionadas com usuarios selecionados
			else:
				print """  <script>
				L.mapbox.accessToken = 'pk.eyJ1IjoiZ2FicmllbGVjYW1hcmEiLCJhIjoiY2pmMnJhcjJzMDVuMzJxbjg5aXYydjl5bCJ9.Lt4VQQDajTeH7ksmyzGqsg';
				var map = L.mapbox.map('map').setView([-25.45,-49.26], 14);
				map.options.minZoom = 14;
				L.mapbox.styleLayer('mapbox://styles/mapbox/dark-v9').addTo(map);
				/* LINHA */
				var wmsLayer_user = L.tileLayer.wms('http://localhost:8082/geoserver/smartmob/wms', {
				layers: 'smartmob:db_rota_selec_usuario_selec',
				transparent: 'true',
				format: 'image/png',
				}).addTo(map);
				wmsLayer_user.options.minZoom = 13;
				wmsLayer_user.options.maxZoom = 17;
				
				/* PONTO */
				var wmsLayer = L.tileLayer.wms('http://localhost:8082/geoserver/smartmob/wms', {
				layers: 'smartmob:db_coletas_selec_usuarios_selec',
				transparent: 'true',
				format: 'image/png',
				}).addTo(map);
				wmsLayer.options.minZoom = 17;
				wmsLayer.options.maxZoom = 18;
				</script>"""
		else:
			# Com todas as rotas
			if num_rota == 0:
				print """  <script>
				L.mapbox.accessToken = 'pk.eyJ1IjoiZ2FicmllbGVjYW1hcmEiLCJhIjoiY2pmMnJhcjJzMDVuMzJxbjg5aXYydjl5bCJ9.Lt4VQQDajTeH7ksmyzGqsg';
				var map = L.mapbox.map('map').setView([-25.45,-49.26], 14);
				map.options.minZoom = 14;
				L.mapbox.styleLayer('mapbox://styles/mapbox/dark-v9').addTo(map);
				/* LINHA */
				var wmsLayer_user = L.tileLayer.wms('http://localhost:8082/geoserver/smartmob/wms', {
				layers: 'smartmob:veloc_rota_usuario_selec',
				transparent: 'true',
				format: 'image/png',
				}).addTo(map);
				wmsLayer_user.options.minZoom = 13;
				wmsLayer_user.options.maxZoom = 17;
				
				/* PONTO */
				var wmsLayer = L.tileLayer.wms('http://localhost:8082/geoserver/smartmob/wms', {
				layers: 'smartmob:veloc_coletas_usuarios_selec',
				transparent: 'true',
				format: 'image/png',
				}).addTo(map);
				wmsLayer.options.minZoom = 17;
				wmsLayer.options.maxZoom = 18;
				</script>"""
			# Rotas selecionadas com usuarios selecionados
			else:
				print """  <script>
				L.mapbox.accessToken = 'pk.eyJ1IjoiZ2FicmllbGVjYW1hcmEiLCJhIjoiY2pmMnJhcjJzMDVuMzJxbjg5aXYydjl5bCJ9.Lt4VQQDajTeH7ksmyzGqsg';
				var map = L.mapbox.map('map').setView([-25.45,-49.26], 14);
				map.options.minZoom = 14;
				L.mapbox.styleLayer('mapbox://styles/mapbox/dark-v9').addTo(map);
				/* LINHA */
				var wmsLayer_user = L.tileLayer.wms('http://localhost:8082/geoserver/smartmob/wms', {
				layers: 'smartmob:veloc_rota_selec_usuario_selec',
				transparent: 'true',
				format: 'image/png',
				}).addTo(map);
				wmsLayer_user.options.minZoom = 13;
				wmsLayer_user.options.maxZoom = 17;
				
				/* PONTO */
				var wmsLayer = L.tileLayer.wms('http://localhost:8082/geoserver/smartmob/wms', {
				layers: 'smartmob:veloc_coletas_selec_usuarios_selec',
				transparent: 'true',
				format: 'image/png',
				}).addTo(map);
				wmsLayer.options.minZoom = 17;
				wmsLayer.options.maxZoom = 18;
				</script>"""

print '</body>'

conn.commit()
cursor.close()
conn.close()