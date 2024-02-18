import subprocess
import mysql.connector
import os


ingreso_bd = {"host":"localhost",
              "user": "admin1",
              "password": "1234"}

""" -------------------->> RUTAS  <<------------"""

carpeta_principal = os.path.dirname(__file__)
carpeta_respaldo = os.path.join(carpeta_principal, "respaldo")


class BaseDatos:
    #Constructor
    def __init__(self, **kwargs):
        #Cursor y conector.
        self.conector = mysql.connector.connect(**kwargs)
        self.cursor = self.conector.cursor()
        
        #getter de la contraseña y el usuario de la base de datos pasada como parametro:
        self.host = kwargs['host']
        self.user = kwargs['user']
        self.password = kwargs['password']

        self.conexion = True #True = conexion abierta. Le doy uso en el metodo decorador cerrar_conexion
        print("Se abrio conexion con el servidor")

    """ --------------> DECORADORES <-------------- """
   
    #Decorador para mostrar todas las bases de datos que hay en el servidor:
    def reporte_bd(funcion_parametro):
        def interno(self, nombre_bd):
            try:
                funcion_parametro(self, nombre_bd) 
            except:
                print(f"Ocurrio un error y no se pudo ejecutar {funcion_parametro}")
            finally:
                BaseDatos.mostrar_bd(self) #Muestro la lista de las bases de datos que hay en el server
        return interno
    
    #Para verificar si la base de datos pasada como parametro existe
    def verificar_bd(funcion_parametro):
        def interno(self, nombre_bd, *args):
            self.cursor.execute(f"SHOW DATABASES LIKE '{nombre_bd}'") #Busco bases de datos con el nombre pasado como parametro
            r = self.cursor.fetchone() 
            if not r: #Si fetchone retorna false quiere decir que no hay bases de datos con {nombre_bd} 
                print("La base de datos ingresada no existe") 
            else: #Si fetchone retorna algun resultado, quiere decir que la base de datos existe
                funcion_parametro(self, nombre_bd, *args) #Ejecuto el metodo            
        return interno 

    #Para cerrar conexion. NOTA: ESTE METODO DEPENDE DE LA VARIABLE BOOLEANA "conexion" QUE SE ENCUENTRA EN EL CONSTRUCTOR
    def cerrar_conexion(funcion_parametro):
        def interno(self, *args, **kwargs): 
            try:
                if not self.conexion: #Si la conexion esta cerrada

                    #Usando las variables del constructor, en las que estan los datos
                    # de acceso a la conexion, ingreso nuevamente al servidor
                    self.conector = mysql.connector.connect(  
                        host = self.host, #obtengo el nombre del host
                        user = self.user, #Nombre de usuario
                        password = self.password) #La constraseña
                    
                    self.cursor = self.conector.cursor() #Me conecto al cursor usando la variable conector
                    self.conexion = True #Conexion en true es conexion abierta   
                    print("Se abrió la conexion con el servidor")
                funcion_parametro(self, *args, **kwargs) #Ejecuto el metodo
            except Exception as e:
                print(f"Ocurrio un error al intentar ejecutar {funcion_parametro}") #Informo que ocurrio algun tipo de error 
                raise e # Cuando se ejecuta la instrucción raise, el programa detiene su ejecución y busca un bloque except que pueda manejar la excepción generada
            finally: #una vez que la conexion esta abierta o si ya lo estaba desde un principio:
                if self.conexion: #True = conexion abierta
                    self.cursor.close() # cierro el cursor
                    self.conector.close() #cierro la conexion
                    self.conexion = False #Conexion en false es conexion cerrada
                    print("Se cerro la conexion con el servidor") 
            return self.resultado #este return nos devuelve el valor de la variable resultado que tenga cualquier método decorado con el decorador "conexion".
        return interno


        """ ------------>> FIN DE LOS DECORADORES <<------------ """
        
        
        
        
        
        
        
        
        
    """-------------> METODOS <-------------- """

    #Para hacer una consulta:
    @cerrar_conexion
    def consulta(self, consulta):
      self.cursor.execute(consulta)
      self.resultado = self.cursor.fetchall()

    #Para mostrar las bases de datos:
    @cerrar_conexion
    def mostrar_bd(self):
        
        self.cursor.execute("SHOW DATABASES") #Consulto las bases de datos del server
        self.resultado = self.cursor.fetchall()

    #Para crear bases de datos:
    @cerrar_conexion
    def crear_bd(self, nombre_bd):
       self.resultado = self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {nombre_bd}") #Creo una base de datos con el nombre pasado como parametro


    #Para eliminar bases de datos.
    @cerrar_conexion
    @verificar_bd
    def eliminar_bd(self, nombre_bd):
        self.resultado = self.cursor.execute(f"DROP DATABASE IF EXISTS {nombre_bd}") #Elimino la bd con el nombre pasado como parametro


    #Crear backups/copia de bases de datos.
    def copia_bd(self, nombre_bd):
        pass
    
    #Para crear tablas:
    """ ESTE METODO FUE CREADO ESPERANDO QUE SE LE PASE UNA LISTA CON ESTA SINTAXIS: 
                        columnas = [
                        {
                            'name': 'id',
                            'type': 'INT',
                            'length': 10,
                            'primary_key': True,
                            'auto_increment': True,
                            'not_null': True
                        },
                        {
                            'name': 'nombre',
                            'type': 'VARCHAR',
                            'length': 32,
                            'primary_key': False,
                            'auto_increment': False,
                            'not_null': True
                        }, """
    @cerrar_conexion
    @verificar_bd
    def crear_tabla(self, nombre_bd, nombre_tb, columnas_lista):

        string_aux = ""
        for columnas in columnas_lista:
            string_aux += f"{columnas['name']} {columnas['type']}({columnas['length']})"#uso la notación corchete para obtener el "value" de la "key"
                
            #Si es clave primaria, auto_increment o no adminte valores nulos, lo añade al string:
            if columnas['primary_key']:
                string_aux += " PRIMARY KEY"
            else:
                pass
            if columnas['auto_increment']:
                string_aux += " AUTO_INCREMENT"
            else:
                pass
            if columnas['not_null']:
                string_aux += " NOT NULL  "
            else:
                pass
            #Hace un salto de línea después de cada diccionario    
                string_aux += ",\n"
            #Elimina al final del string el salto de línea y la coma    
            string_aux = string_aux[:-2] #cadena[inicio:fin:paso]
            print(string_aux)
            #Hago uso de la base de datos pasada como parametro:
            self.cursor.execute(f"USE {nombre_bd}")
            #Creo la tabla
            self.resultado = self.cursor.execute(f"CREATE TABLE {nombre_tb} ({string_aux});")
            
            print("Se creo correctamente la tabla")
            #Hago efectiva la instruccion y cierro la conexion con el server
            self.conector.commit()
            return self.resultado   
    
    
    #Para elimnar una tabla de una base de datos
    @cerrar_conexion
    @verificar_bd
    def eliminar_tabla(self, nombre_bd, nombre_tb):
        self.cursor.execute(f"USE {nombre_bd}")
        try:
            self.resultado = self.cursor.execute(f"DROP TABLE {nombre_tb} ") #Elimino la tabla
            return self.resultado
        except:
            print(f"Ocurrio un error al eliminar.")
            self.mostrar_tablas(nombre_bd) #Muestro las tablas que aun quedan en la bd
    
    #Para mostrar tablas:
    @cerrar_conexion
    @verificar_bd
    def mostrar_tablas(self, nombre_bd):
        self.cursor.execute(f"USE {nombre_bd}") 
        self.cursor.execute("SHOW TABLES") #Muestro una lista de todas las tablas 
        self.resultado = self.cursor.fetchall() #Guardo todas las tablas en r 
        return self.resultado

    #Para mostrar columnas de una tabla:
    @cerrar_conexion
    @verificar_bd
    def mostrar_columnas(self, nombre_bd, nombre_tb):
        self.cursor.execute(f"USE {nombre_bd}")
        self.cursor.execute(f"SHOW COLUMNS FROM {nombre_tb}") #Muestro todas las columnas de la tabla
        self.resultado = self.cursor.fetchall() #Guardo la lista de todas las columnas en r
        return self.resultado
        # print(f"Estas son las columnas que tiene la tabla {nombre_tb}")
            

            #Sintaxis de sentencias ternarias que estoy usando dentro del for.
            #variable = expresión_verdadera if expresión_condicional else expresión_falsa
        #     for columna in resultado: #Recorro r
        #         not_null = "No admite valores nulos." if columna[2] == "NO" else ""
        #         primary_key = "Es clave primaria." if columna[3] == "PRI" else ""
        #         foreign_key = "Es clave externa." if columna[3] == "MUL" else ""
        #         print(f"{columna[0]}, {columna[1]},{not_null}, {primary_key}, {foreign_key}")
        # except:
        #     print("Ocurrio un error. No se puede mostrar las columnas de la tabla")

    #Para insertar registros: #Nota 1: este metodo hay que revisarlo y mejorarlo
        """     #NOTA 2 : ESTE METODO ESTA ESPERA RECIBIR UNA LISTA/REGISTRO DEL ESTILO: registro = [{"nombre": "Enrique",
                                                                                            "apellidos" : "Barros Fernández",
                                                                                            "telefono" : "786959404",
                                                                                            "direccion" : "C/cualquiera"}] """
   
    @cerrar_conexion
    @verificar_bd
    def insertar_registro(self, nombre_bd, nombre_tb, registro):
        self.cursor.execute(f"USE {nombre_bd}")

        columnas = [] 
        valores = []    
        try:
        
            for indice in registro: #Recorro el diccionario pasado como parametro
                columnas.extend(indice.keys()) #Agrego las "keys" del diccionario a una lista 
                valores.extend(indice.values()) #Agrego los "values" del diccionario a otra lista

            string_columnas = "" 
            string_valores = ""

            for i in columnas: #Recorro la lista con las "keys" y los agrego a una sola cadena de string (uno detras de otro)
                string_columnas += f"{i}, "  
            string_columnas = string_columnas[:-2]  # Quitar la última coma y espacio. cadena[inicio:fin:paso]
            
            for i in valores: #Recorro la lista con las "values" y los agrego a otra cadena de string
                string_valores += f"'{i}', "
            string_valores = string_valores[:-2] #cadena[inicio:fin:paso]

            self.cursor.execute(f"INSERT INTO {nombre_tb} ({string_columnas}) VALUES ({string_valores})") #Uso los string que arme, para formar la consulta correctamente
            self.conector.commit() #Confirmo la consulta en el conector

            print("Registro añadido a la tabla")
        
        except:
            print("Ocurrio un error. No pudo añadirse el registro a la tabla")

    #Para mostrar registros/filas en tablas (NO usa where por ahora)
    @cerrar_conexion
    @verificar_bd
    def mostrar_registros(self, nombre_bd, nombre_tb):
        self.cursor.execute(f"USE {nombre_bd}")

        sql = f"SELECT * FROM {nombre_tb};"  
        #Muestro todas las filas de la tabla y las guardo en "r"
        self.cursor.execute(sql) 
        r = self.cursor.fetchone()
        if not r: #Si "r" retorna "none" quiere decir que no hay filas que mostrar.
            print(f"La tabla {nombre_tb} no tiene registros/filas") #Informo que la tabla no tiene filas
            raise Exception
        try:
            self.cursor.execute(sql) #Muestro las filas que hay en las tablas
            resultado = self.cursor.fetchall() #Guardo una lista con todas las filas de la tabla 
            return resultado
        except:
            print(f"Ocurrio un error. No se pudo mostrar los registros de la tabla {nombre_tb}")
            return
    #Para eliminar registros. 
    #Nota: este metodo espera una consulta con esta sintaxis -> self.eliminar_registro("pruebas","usuarios", "nombre = 'Enrique'")
    @cerrar_conexion
    @verificar_bd
    def eliminar_registro(self, nombre_bd, nombre_tb, condiciones):
        self.cursor.execute(f"USE {nombre_bd}")
        #Elimino las filas(que cumplan con las condiciones) de la tabla pasada como parametro
        try:
            self.resultado = self.cursor.execute(f"DELETE FROM {nombre_tb} WHERE {condiciones};") 
            self.conector.commit() #Hago efectiva la consulta en el conector
            return self.resultado
        except:
            print(f"Ocurrio un error o el registro ingresado no existe")

    #Para consultar registros:
    @cerrar_conexion
    @verificar_bd
    def mostrar_registro(self, nombre_bd, nombre_tb, condiciones):
        self.cursor.execute(f"USE {nombre_bd}")
        sql = f"SELECT * FROM {nombre_tb} WHERE {condiciones}"  #Consulta para mostrar todas las filas(que cumplan con las condiciones) de la tabla
        try:
            self.cursor.execute(sql) #Ejecuto la consulta
            r = self.cursor.fetchall() #Guardo la lista de las filas en "r"
            print(f"Estas son las filas de la tabla {nombre_tb}")
            for i in r: #Recorro la lista de "r" y muestro sus elementos
                print(i)
        except:
            print("Error.")
        
    #Para modificar/actualizar registros:
    #Nota: este metodo espera una consulta con esta sintaxis -> base_datos.mod_registro("pruebas", 
    # "usuarios",
    #  "apellidos = 'Barros Fernández', 
    # direccion = 'Avenida nº 7'",
    #  "id = '1';")
    @cerrar_conexion
    @verificar_bd
    def mod_registro(self, nombre_bd, nombre_tb, columna, condiciones):
        self.cursor.execute(f"USE {nombre_bd}")
        sql = f"UPDATE {nombre_tb} SET {columna} WHERE {condiciones}"#Consulta para modificar aquellas filas que cumplan con las condiciones
        try: 
            # Se ejecuta la instrucción de actualización y se hace efectiva
            self.cursor.execute(sql)
            self.conector.commit()
            print("Se actualizó el registro correctamente.")
        except:
            print("Ocurrió un error al intentar actualizar el registro.")





