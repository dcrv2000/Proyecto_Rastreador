import math

# --- CLASE BASE (POO) ---
class CuerpoCeleste:
    def __init__(self, nombre, categoria, equipo, orientacion):
        self.nombre = nombre
        self.categoria = categoria
        self.equipo = equipo
        self.orientacion = orientacion

    def obtener_info_base(self):
        return f"{self.nombre} ({self.categoria}) - Guía: {self.orientacion}"

# --- CLASE HIJA QUE HEREDA DE CuerpoCeleste (Herencia en POO) ---
class Satelite(CuerpoCeleste):
    def __init__(self, nombre, categoria, equipo, orientacion, latitud, longitud, altitud):
        super().__init__(nombre, categoria, equipo, orientacion)
        self.latitud = latitud
        self.longitud = longitud
        self.altitud = altitud # En kilómetros

    def obtener_estado_orbita(self):
        return f"Lat: {self.latitud}, Lon: {self.longitud}, Alt: {self.altitud} km"

# --- MOTOR DE CÁLCULO MATRICIAL (Matrices y Bucles) ---
class MotorRastreo:
    def __init__(self):
        self.matriz_objetos = []

    def cargar_matriz(self, lista_objetos):
        """Carga una matriz bidimensional con los objetos espaciales y sus coordenadas"""
        self.matriz_objetos = []
        for obj in lista_objetos:
            # Estructura de la fila de la matriz: [Nombre, Latitud, Longitud, Altitud/Distancia]
            fila = [obj.get('nombre'), obj.get('lat', 0.0), obj.get('lon', 0.0), obj.get('alt', 0.0)]
            self.matriz_objetos.append(fila)

    def calcular_objeto_mas_cercano(self, base_lat, base_lon):
        """
        Recorre la matriz usando bucles en Python para calcular 
        cuál objeto en órbita está más cerca de una coordenada base (ej. Tierra/Caracas).
        """
        if not self.matriz_objetos:
            return None

        objeto_cercano = None
        menor_distancia = float('inf')

        for fila in self.matriz_objetos:
            nombre, lat, lon, alt = fila
            # Fórmula matemática simple de distancia euclidiana aproximada
            distancia = math.sqrt((lat - base_lat)**2 + (lon - base_lon)**2)
            
            if distancia < menor_distancia:
                menor_distancia = distancia
                objeto_cercano = {
                    "nombre": nombre,
                    "lat": lat,
                    "lon": lon,
                    "distancia_aprox": round(menor_distancia, 2)
                }
                
        return objeto_cercano