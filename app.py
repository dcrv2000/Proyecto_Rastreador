from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from base_datos import GestorDB
from clases import Satelite, MotorRastreo
from api import APIEspacial

app = Flask(__name__)

db = GestorDB()
motor = MotorRastreo()
api_espacial = APIEspacial()

@app.route('/')
def index():
    catalogo_db = db.obtener_catalogo()
    datos_iss = api_espacial.obtener_posicion_iss()
    datos_nasa = api_espacial.obtener_asteroides_nasa()

    objetos_para_matriz = []
    if datos_iss["exito"]:
        satelite_iss = Satelite("ISS", "Satélite Habitado", "Radar Orbital", "Órbita Baja", 
                                datos_iss["lat"], datos_iss["lon"], datos_iss["alt"])
        objetos_para_matriz.append({
            "nombre": satelite_iss.nombre, 
            "lat": satelite_iss.latitud, 
            "lon": satelite_iss.longitud, 
            "alt": satelite_iss.altitud
        })

    motor.cargar_matriz(objetos_para_matriz)
    objeto_mas_cercano = motor.calcular_objeto_mas_cercano(10.5, -66.9)

    return render_template('index.html', 
                           catalogo=catalogo_db, 
                           iss=datos_iss, 
                           nasa=datos_nasa,
                           mas_cercano=objeto_mas_cercano)

@app.route('/control')
def control():
    catalogo_db = db.obtener_catalogo()
    constelaciones = db.obtener_constelaciones()
    historial = db.obtener_historial()
    
    return render_template('control.html', 
                           catalogo=catalogo_db, 
                           constelaciones=constelaciones,
                           historial=historial)

@app.route('/agregar', methods=['POST'])
def agregar():
    nombre = request.form['nombre']
    categoria = request.form['categoria']
    tipo_estrella = request.form.get('tipo_estrella') or "-"
    equipo = request.form['equipo']
    orientacion = request.form['orientacion']
    coordenadas = request.form.get('coordenadas') or "No especificada"
    
    # Lógica inteligente para la constelación
    id_constelacion = None
    selector_constelacion = request.form.get('id_constelacion')
    
    if selector_constelacion == 'nueva':
        # Si eligió agregar una nueva, capturamos el texto escrito por el usuario
        nueva_constel = request.form.get('nueva_constelacion_nombre')
        if nueva_constel:
            id_constelacion = db.obtener_o_crear_constelacion(nueva_constel)
    elif selector_constelacion:
        id_constelacion = int(selector_constelacion)

    # Intentamos insertar (si la estrella ya existe, el try...except de la BD lo frena limpiamente)
    db.insertar_cuerpo(nombre, categoria, tipo_estrella, equipo, coordenadas, orientacion, id_constelacion)
    return redirect(url_for('control'))

@app.route('/registrar_avistamiento', methods=['POST'])
def registrar_avistamiento():
    id_cuerpo = request.form['id_cuerpo']
    notas = request.form['notas']
    fecha = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    db.insertar_avistamiento(id_cuerpo, fecha, notas)
    return redirect(url_for('control'))

@app.route('/eliminar/<int:id_cuerpo>')
def eliminar(id_cuerpo):
    db.eliminar_cuerpo(id_cuerpo)
    return redirect(url_for('control'))

@app.route('/editar/<int:id_cuerpo>', methods=['GET', 'POST'])
def editar(id_cuerpo):
    if request.method == 'POST':
        nombre = request.form['nombre']
        categoria = request.form['categoria']
        tipo_estrella = request.form.get('tipo_estrella') if categoria == 'Estrella' else "-"
        if not tipo_estrella:
            tipo_estrella = "-"
        equipo = request.form['equipo']
        orientacion = request.form['orientacion']
        coordenadas = request.form.get('coordenadas') or "No especificada"

        id_constelacion = None
        selector_constelacion = request.form.get('id_constelacion')
        if selector_constelacion == 'nueva':
            nueva_constel = request.form.get('nueva_constelacion_nombre')
            if nueva_constel:
                id_constelacion = db.obtener_o_crear_constelacion(nueva_constel)
        elif selector_constelacion:
            id_constelacion = int(selector_constelacion)

        db.actualizar_cuerpo(id_cuerpo, nombre, categoria, tipo_estrella, equipo, coordenadas, orientacion, id_constelacion)
        return redirect(url_for('control'))

    astro = db.obtener_cuerpo_por_id(id_cuerpo)
    if not astro:
        return redirect(url_for('control'))
    constelaciones = db.obtener_constelaciones()
    return render_template('editar.html', astro=astro, constelaciones=constelaciones)

if __name__ == '__main__':
    app.run(debug=True)