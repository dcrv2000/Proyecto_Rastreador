import requests

class APIEspacial:
    def __init__(self):
        self.url_iss = "http://api.open-notify.org/iss-now.json"
        self.url_nasa = "https://api.nasa.gov/neo/rest/v1/feed?api_key=DEMO_KEY"

    def obtener_posicion_iss(self):
        """Consulta la posición exacta de la ISS y su ubicación geográfica aproximada"""
        try:
            respuesta = requests.get(self.url_iss, timeout=4)
            if respuesta.status_code == 200:
                datos = respuesta.json()
                lat = float(datos['iss_position']['latitude'])
                lon = float(datos['iss_position']['longitude'])
                
                # API secundaria para traducir coordenadas a texto legible
                ubicacion_texto = "Sobre aguas internacionales u océano"
                try:
                    url_geo = f"https://api.bigdatacloud.net/data/reverse-geocode-client?latitude={lat}&longitude={lon}&localityLanguage=es"
                    res_geo = requests.get(url_geo, timeout=3)
                    if res_geo.status_code == 200:
                        geo_data = res_geo.json()
                        pais = geo_data.get('countryName')
                        continente = geo_data.get('continent')
                        if pais:
                            ubicacion_texto = f"Sobre / Cerca de: {pais}"
                        elif continente:
                            ubicacion_texto = f"Región de: {continente}"
                except:
                    pass

                return {
                    "exito": True, 
                    "lat": lat, 
                    "lon": lon, 
                    "alt": 420.0, 
                    "ubicacion_aproximada": ubicacion_texto
                }
        except Exception as e:
            print(f"Error conectando con API ISS: {e}")
        return {"exito": False, "error": "Sin conexión a ISS"}

    def obtener_asteroides_nasa(self):
        """Consume la API de la NASA (NeoWs) para obtener asteroides cercanos"""
        try:
            respuesta = requests.get(self.url_nasa, timeout=5)
            if respuesta.status_code == 200:
                datos = respuesta.json()
                fechas = datos.get('near_earth_objects', {})
                primera_fecha = list(fechas.keys())[0] if fechas else None
                
                if primera_fecha:
                    lista_asteroides = []
                    for neo in fechas[primera_fecha][:3]: # Tomamos 3 asteroides
                        nombre = neo.get('name')
                        peligroso = neo.get('is_potentially_hazardous_asteroid', False)
                        km_distancia = float(neo['close_approach_data'][0]['miss_distance']['kilometers'])
                        lista_asteroides.append({
                            "nombre": nombre,
                            "peligroso": peligroso,
                            "distancia_km": round(km_distancia, 2)
                        })
                    return {"exito": True, "asteroides": lista_asteroides}
        except Exception as e:
            print(f"Error conectando con API NASA: {e}")
        return {"exito": False, "asteroides": []}