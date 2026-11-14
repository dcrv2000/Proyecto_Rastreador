import sqlite3

class GestorDB:
    def __init__(self, nombre_bd="radar_espacial.db"):
        self.conexion = sqlite3.connect(nombre_bd, check_same_thread=False)
        self.cursor = self.conexion.cursor()
        self.crear_tablas()
        self.poblar_datos_iniciales()

    def crear_tablas(self):
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS constelaciones (
                    id_constelacion INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL UNIQUE,
                    mejor_mes TEXT NOT NULL
                )
            ''')

            # Agregamos UNIQUE(nombre) para evitar registrar dos veces la misma estrella
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS catalogo_estelar (
                    id_cuerpo INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL UNIQUE,
                    categoria TEXT NOT NULL,
                    tipo_estrella TEXT,
                    equipo TEXT NOT NULL,
                    coordenadas TEXT NOT NULL,
                    orientacion TEXT,
                    id_constelacion INTEGER,
                    FOREIGN KEY (id_constelacion) REFERENCES constelaciones(id_constelacion)
                )
            ''')

            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS historial_avistamientos (
                    id_avistamiento INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_cuerpo INTEGER,
                    fecha TEXT NOT NULL,
                    notas TEXT NOT NULL,
                    FOREIGN KEY (id_cuerpo) REFERENCES catalogo_estelar(id_cuerpo)
                )
            ''')
            self.conexion.commit()
        except Exception as e:
            print(f"Error al crear tablas: {e}")
            self.conexion.rollback()

    def poblar_datos_iniciales(self):
        try:
            self.cursor.execute('SELECT COUNT(*) FROM constelaciones')
            if self.cursor.fetchone()[0] == 0:
                constelaciones = [
                    ('Orión', 'Diciembre a Marzo'), 
                    ('Can Mayor', 'Febrero'),
                    ('Lyra', 'Verano')
                ]
                self.cursor.executemany('INSERT OR IGNORE INTO constelaciones (nombre, mejor_mes) VALUES (?, ?)', constelaciones)
                
                estrellas_iniciales = [
                    ('Betelgeuse', 'Estrella', 'Gigante Roja', 'A simple vista', '05h 55m / +07° 24', 'Hacia el Este / Sureste', 1),
                    ('Sirio', 'Estrella', 'Secuencia Principal', 'A simple vista', '06h 45m / -16° 42', 'Hacia el Sur', 2),
                    ('Vega', 'Estrella', 'Enana Blanca / Principal', 'A simple vista', '18h 36m / +38° 47', 'Hacia el Cenit / Norte', 3)
                ]
                self.cursor.executemany('''
                    INSERT OR IGNORE INTO catalogo_estelar (nombre, categoria, tipo_estrella, equipo, coordenadas, orientacion, id_constelacion) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', estrellas_iniciales)
                self.conexion.commit()
        except Exception as e:
            print(f"Error poblando datos iniciales: {e}")
            self.conexion.rollback()

    def obtener_o_crear_constelacion(self, nombre_constelacion, mejor_mes="Todo el año"):
        """Busca si la constelación ya existe (sin importar mayúsculas/minúsculas). Si no, la crea."""
        try:
            nombre_limpio = nombre_constelacion.strip()
            # Buscamos coincidencias ignorando mayúsculas
            self.cursor.execute('SELECT id_constelacion FROM constelaciones WHERE LOWER(nombre) = LOWER(?)', (nombre_limpio,))
            resultado = self.cursor.fetchone()
            
            if resultado:
                return resultado[0] # Retorna el ID existente
            else:
                # Si no existe, la inserta y retorna el nuevo ID
                self.cursor.execute('INSERT INTO constelaciones (nombre, mejor_mes) VALUES (?, ?)', (nombre_limpio, mejor_mes))
                self.conexion.commit()
                return self.cursor.lastrowid
        except Exception as e:
            print(f"Error gestionando constelación: {e}")
            return None

    def obtener_catalogo(self):
        try:
            self.cursor.execute('''
                SELECT c.id_cuerpo, c.nombre, c.categoria, IFNULL(c.tipo_estrella, '-'), c.equipo, c.coordenadas, c.orientacion, IFNULL(con.nombre, '-')
                FROM catalogo_estelar c
                LEFT JOIN constelaciones con ON c.id_constelacion = con.id_constelacion
            ''')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener catálogo: {e}")
            return []

    def obtener_constelaciones(self):
        try:
            self.cursor.execute('SELECT * FROM constelaciones')
            return self.cursor.fetchall()
        except:
            return []

    def obtener_historial(self):
        try:
            self.cursor.execute('''
                SELECT h.id_avistamiento, ce.nombre, h.fecha, h.notas
                FROM historial_avistamientos h
                INNER JOIN catalogo_estelar ce ON h.id_cuerpo = ce.id_cuerpo
            ''')
            return self.cursor.fetchall()
        except:
            return []

    def insertar_cuerpo(self, nombre, categoria, tipo_estrella, equipo, coordenadas, orientacion, id_constelacion):
        try:
            self.cursor.execute('''
                INSERT INTO catalogo_estelar (nombre, categoria, tipo_estrella, equipo, coordenadas, orientacion, id_constelacion)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (nombre.strip(), categoria, tipo_estrella, equipo, coordenadas, orientacion, id_constelacion))
            self.conexion.commit()
            return True
        except sqlite3.IntegrityError:
            print("Error: Este cuerpo celeste ya se encuentra registrado en el catálogo.")
            return False
        except Exception as e:
            print(f"Error al insertar en base de datos: {e}")
            self.conexion.rollback()
            return False

    def insertar_avistamiento(self, id_cuerpo, fecha, notas):
        try:
            self.cursor.execute('''
                INSERT INTO historial_avistamientos (id_cuerpo, fecha, notas)
                VALUES (?, ?, ?)
            ''', (id_cuerpo, fecha, notas))
            self.conexion.commit()
            return True
        except Exception as e:
            print(f"Error al registrar avistamiento: {e}")
            self.conexion.rollback()
            return False

    def eliminar_cuerpo(self, id_cuerpo):
        try:
            self.cursor.execute('DELETE FROM catalogo_estelar WHERE id_cuerpo = ?', (id_cuerpo,))
            self.conexion.commit()
            return True
        except Exception as e:
            print(f"Error al eliminar registro: {e}")
            self.conexion.rollback()
            return False

    def obtener_cuerpo_por_id(self, id_cuerpo):
        try:
            self.cursor.execute('''
                SELECT id_cuerpo, nombre, categoria, tipo_estrella, equipo, coordenadas, orientacion, id_constelacion
                FROM catalogo_estelar
                WHERE id_cuerpo = ?
            ''', (id_cuerpo,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error al buscar cuerpo celeste: {e}")
            return None

    def actualizar_cuerpo(self, id_cuerpo, nombre, categoria, tipo_estrella, equipo, coordenadas, orientacion, id_constelacion):
        try:
            self.cursor.execute('''
                UPDATE catalogo_estelar
                SET nombre = ?, categoria = ?, tipo_estrella = ?, equipo = ?, coordenadas = ?, orientacion = ?, id_constelacion = ?
                WHERE id_cuerpo = ?
            ''', (nombre.strip(), categoria, tipo_estrella, equipo, coordenadas, orientacion, id_constelacion, id_cuerpo))
            self.conexion.commit()
            return True
        except sqlite3.IntegrityError:
            print("Error: Ya existe otro cuerpo celeste con ese nombre.")
            return False
        except Exception as e:
            print(f"Error al actualizar registro: {e}")
            self.conexion.rollback()
            return False