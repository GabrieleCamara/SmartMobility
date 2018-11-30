#!/usr/bin/python
#-*-encoding:utf-8-*-

import psycopg2
try:
	conn = psycopg2.connect("dbname = 'smartmob' port = '5432'  user= 'user' password = 'user' host='localhost'")
	cursor = conn.cursor()
except:
	print 'Erro'

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

print """  <script>
	L.mapbox.accessToken = 'pk.eyJ1IjoiZ2FicmllbGVjYW1hcmEiLCJhIjoiY2pmMnJhcjJzMDVuMzJxbjg5aXYydjl5bCJ9.Lt4VQQDajTeH7ksmyzGqsg';
	var map = L.mapbox.map('map').setView([-25.45,-49.26], 14);
	map.options.minZoom = 14;
	L.mapbox.styleLayer('mapbox://styles/mapbox/dark-v9').addTo(map);

	var wmsLayer = L.tileLayer.wms('http://localhost:8082/geoserver/smartmob/wms', {
	    layers: 'smartmob:rotas_todos_usuario',
		transparent: 'true',
		format: 'image/png',
	}).addTo(map);
	
	wmsLayer.options.minZoom = 13;
	wmsLayer.options.maxZoom = 17;

  </script>"""
print '</body>'

conn.commit()
cursor.close()
conn.close()