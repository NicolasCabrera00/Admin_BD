""" Importaciones """
import tkinter as tk  
import customtkinter as ctk
import os
from tkinter import messagebox
from PIL import Image,ImageTk #Pil solo voy a usarlo para imagenes
import bd.base_datos as sql  

""" ----> rutas <---- """

principal = os.path.dirname(__file__) #Directorio del proyecto
directorio_imagenes = os.path.join(principal, "img") #directorio con las imagenes usadas en el proyecto
BaseDatos = sql.BaseDatos(**sql.ingreso_bd)  #Ingreso a la base de datos con la clase BaseDatos


class gui():
    #constructor
    def __init__(self, **kwargs):
        """ Ventana de la app """
        self.ventana = ctk.CTk() #Ventana login tipo custom tkinter
        self.ventana.geometry("450x450")
        self.ventana.title("Consultas sql")
        self.ventana.iconbitmap(os.path.join(directorio_imagenes, "icon.ico"))
        

        """ Contenido de la ventana """
        logo = ImageTk.PhotoImage(Image.open(os.path.join(directorio_imagenes, "principal.png")).resize((240,240)))
        tk.Label(self.ventana, image=logo).pack()

        """ Entradas de texto """                    
        #Usuario y contraseña:
        tk.Label(text= "Ingrese su nombre de usuario").pack()
        self.usuario = ctk.CTkEntry(self.ventana)
        self.usuario.insert(0, "Ej Nico")
        self.usuario.bind("<Button-1>", lambda e: self.usuario.delete(0, tk.END))
        self.usuario.pack()

        tk.Label(text= "Ingrese su contraseña").pack()        
        self.contrasena = ctk.CTkEntry(self.ventana, show="*")
        self.contrasena.insert(0, "*****")
        self.contrasena.bind("<Button-1>", lambda e: self.contrasena.delete(0, tk.END))
        self.contrasena.pack()

        boton = ctk.CTkButton(self.ventana, text = "Ingresar", command= self.prueba)
        boton.pack()
        self.ventana.mainloop()

    def prueba(self): #metodo para testear el boton de enviar en la ventana de login. Se puede eliminar
        self.ventana.destroy()
        ventana_opciones()   

        """ Boton de envio """
    def validar(self):
        #Getter de usuario y contraseña ingresados
        self.usuario_ingresado = self.usuario.get()
        self.contrasena_ingresada = self.contrasena.get()
        """ Los comparo con los datos de la base de datos """
        if(sql.ingreso_bd["user"] != self.usuario_ingresado or self.contrasena_ingresada != sql.ingreso_bd["password"]):
            if hasattr(self, "info_login"):
                self.info_login.destroy()
            self.info_login = ctk.CTkLabel(self.ventana, text="Usuario o contraseña ingresado incorrecto")
            self.info_login.pack()
        else:
            self.ventana.destroy()
            ventana_opciones()

class funcionesprograma:
    
    def ventana_consultas(self):
        ventana = ctk.CTkToplevel()
        ventana.title("Ventana de consultas SQL")
        ventana.grab_set() # Pone el foco en la ventana
        #Marco para trabajar dentro de la ventana
        marco = ctk.CTkFrame(ventana)
        marco.pack(padx=10, pady=10)
        
        #Entry donde se ingresa la consulta
        self.entrada = ctk.CTkEntry(marco, width=600)  
        # Posiciona el elemento en grid
        self.entrada.grid(row=0,column=0)

        
        #Caja de texto:
        self.box = ctk.CTkTextbox(marco, width=610, height=300)
        self.box.grid(row=1, column= 0)          

        #botones

        #Para enviar la consulta al servidor
        envio = ctk.CTkButton(marco, text="Enviar", command= lambda : procesar_datos())
        envio.grid(row=0, column= 1)

        #Para borrar el contenido de la caja de texto con los resultados de una consulta anterior
        borrar = ctk.CTkButton(marco,text = "Borrar", command= lambda : self.box.delete('1.0', 'end'))
        borrar.grid(row=0, column=2)

        def procesar_datos():
            try:
                # Borra el contenido de "texto"
                self.box.delete('1.0', 'end')
                #Guardo lo que se ingreso en el Entry "entrada"
                datos = self.entrada.get()
                #Ejecuto la consulta
                resultado = BaseDatos.consulta(datos)
                #Muestro los resultados de manera ordenada
                for r in resultado:
                    self.box.insert('end', r)
                    self.box.insert('end', '\n')
                #Cantidad de resultados obtenidos
                cant = len(resultado)
                #Titulo formal para los resultados obtenidos
                msj = ctk.CTkLabel(marco, text=f"Registros devueltos: {cant}").grid(row=2, column = 0)     
            except Exception:
                #Si se ingresa cualquier cosa que no sea una consulta slq
                messagebox.showerror(title="Erorr", message="Hay un error en tu consulta sql")
                self.box.delete('1.0', 'end')
    
    def ventana_mostrar_bases_datos(self):
        
        """ Nota:
         Debo agregar mas tarde "except" a esta funcion.  """
        
        # Se crea la ventana
        ventana = ctk.CTkToplevel()
        # Se le da un título
        ventana.title("Ventana para mostrar las bases de datos del servidor.")
        # Se le da un tamaño
        ventana.geometry("350x490")
        # Se evita su redimensión
        ventana.resizable(0,0)
        ventana.grab_set() # Pone el foco en la ventana

        #Se crea un marco en la ventana
        marco = ctk.CTkFrame(ventana)
        marco.pack(padx=10, pady=10)
        #Titulo de la ventana
        titulo = ctk.CTkLabel(marco,text="Estas son las bd que hay en el servidor")
        titulo.pack()
        #Textbox donde se muestran los resultados
        self.box = ctk.CTkTextbox(marco, width=250,height=250)
        self.box.pack(padx=10, pady=10)
        #Label para mostrar los resultados
        self.label_res = ctk.CTkLabel(marco, text="")
        self.label_res.pack(pady=10)
        # Se crear la entrada de texto para búsquedas
        self.busqueda_control = tk.StringVar()
        ctk.CTkEntry(marco, textvariable= self.busqueda_control, width=300).pack(padx=10)        
        #Botones
        botonbuscar = ctk.CTkButton(marco, text="buscar", command = lambda : buscar())
        botonbuscar.pack(pady= 10)

        botonact = ctk.CTkButton(marco, text="actualizar", command= lambda : actualizar())
        botonact.pack(pady=10)
        
        #Función interna de actualización SHOW DATABASES 
        def actualizar():
            
            self.busqueda_control.set('')
            self.box.delete('1.0', 'end')

            resultado = BaseDatos.mostrar_bd()
            for bd in resultado:
                self.box.insert('end',bd[0])
                self.box.insert('end', '\n')
            cant = len(resultado)
            self.label_res.configure(text=f"Se encontraron {cant} bases de datos")
        #Funcion para busqueda de una bd
        def buscar():
            self.box.delete('1.0', 'end')
            busqueda = self.busqueda_control.get().lower() 
            
            resultado = BaseDatos.mostrar_bd()
            resultado_filtrado = []

            for bd in resultado:
                if busqueda in bd[0]:
                    resultado_filtrado.append(bd)

            for bd in resultado_filtrado:
                self.box.insert('end', bd[0])

            cant = len(resultado_filtrado)
            self.label_res.configure(text=f"Se encontraron {cant} bases de datos")

    def ventana_eliminar_bases_datos(self):
        ventana = ctk.CTkToplevel()
        ventana.geometry("550x300")
        ventana.title("Ventana para eliminar bases de datos")
        ventana.grab_set() # Pone el foco en la ventana
        #Marco para trabajar dentro de la ventana
        marco =  ctk.CTkFrame(ventana)
        marco.pack(padx=10, pady=10)

        #Entrada de texto
        texto =  ctk.CTkEntry(marco, width= 350)
        texto.grid(row=0 , column= 0)
        texto.insert(0, "Ingrese el nombre de la base de datos que desea borrar")
        texto.bind("<Button-1>", lambda e: texto.delete(0, tk.END))
        

        #botones:
        enviar =  ctk.CTkButton(marco, text="Eliminar", command= lambda : eliminar_actualizar())
        enviar.grid(row= 0, column= 1)       
        

        #muestro lista de las bd
        
        titulo =  ctk.CTkLabel(marco, text="Lista de bases de datos existentes en el servidor")
        titulo.grid(row= 1, column = 0)
        
        box =  ctk.CTkTextbox(marco, width=200,height=200)
        box.grid(row = 2, column= 0)
        lista = BaseDatos.mostrar_bd()
        for bd in lista:
            box.insert('end', bd[0])
            box.insert('end', '\n')
        #Funcion para actualizar la lista de bases
        def eliminar_actualizar():
            box.delete('1.0','end')
            base_borrar = texto.get()
            opcion = messagebox.askyesno(title="Seguro?", message=f"Esta seguro que quiere borrar: '{base_borrar}' ?")
            if opcion:
                eliminar = BaseDatos.eliminar_bd(f"{base_borrar}")
                if eliminar:
                    messagebox.showinfo(title="Error",message="La base de datos ingresada no existe")     
                else:            
                    messagebox.showinfo(title="Operacion existosa",message = f"La base de datos {base_borrar} fue eliminada")
            else:
                pass
            lista = BaseDatos.mostrar_bd()
            for bd in lista:
                box.insert('end', bd[0])
                box.insert('end', '\n')               

    
    def ventana_crear_bases_datos(self):
        ventana =  ctk.CTkToplevel()
        ventana.geometry("650x190")
        ventana.title("Crear bases de datos")
        ventana.grab_set() # Pone el foco en la ventana
        #Marco para trabajar dentro de la ventana
        marco = ctk.CTkFrame(ventana)
        marco.pack()

        #Entrada de texto
        texto = ctk.CTkEntry(marco, width= 350)
        texto.grid(row=0 , column= 0)
        texto.insert(0, "Ingrese el nombre de la base de datos que desea crear")
        texto.bind("<Button-1>", lambda e: texto.delete(0, tk.END))
        
        #botones:
        enviar = ctk.CTkButton(marco, text="Crear", command = lambda : crear_bd())
        enviar.grid(row= 0, column= 1)       

        borrar = ctk.CTkButton(marco,text="borrar", command = lambda : texto.delete(0, tk.END))
        borrar.grid(row= 0, column= 2)


        #muestro lista de las bd    
        titulo = ctk.CTkLabel(marco, text="Lista de bases de datos existentes en el servidor")
        titulo.grid(row= 1, column = 0)

        box = ctk.CTkTextbox(marco, width=600,height=115)
        box.grid(row=2, column=0, columnspan=3, padx=10, pady=10)
        lista = BaseDatos.mostrar_bd()
        for bd in lista:
            box.insert('end', bd[0])
            box.insert('end', '\n')
        
        #creo la base de datos:
        def crear_bd():
            nombre_bd = texto.get()
            opcion = messagebox.askyesno(title="Seguro?", message=f"Estas por agregar la base de datos:  '{nombre_bd}'. Desea continuar?")
            if opcion:
                try:
                    crear = BaseDatos.crear_bd(f"{nombre_bd}")
                    messagebox.showinfo(title="Operacion exitosa", message= f"La base de datos {nombre_bd} fue creada")
                except Exception:
                    messagebox.showerror(title="Error", message="La base de datos no se pudo crear. Verifica que tenga nombre valido")
            else:
                pass
            lista = BaseDatos.mostrar_bd()
            box.delete('1.0', 'end')
            for bd in lista:
                box.insert('end', bd[0])
                box.insert('end', '\n')
        
    def ventana_crear_respaldos(self):
        ventana = ctk.CTkToplevel()
        ventana.title("Ventana para crear respaldos")
        ventana.geometry("360x250")
        ventana.grab_set()
        ctk.CTkLabel(ventana, text="Sigo trabajando en esto").pack()


        
    def ventana_crear_tablas(self):
        """ Nota:
        A esta funcion aun le falta trabajar try and except"""
        #ventana principal
        ventana = ctk.CTkToplevel()
        ventana.title("Crear tablas")
        ventana.geometry("600x120")
        ventana.grab_set() # Pone el foco en la ventana
        
        #Marco para trabajar dentro de la ventana
        marco = ctk.CTkFrame(ventana)
        marco.pack(padx= 10)
        
        """ Para pedir datos de la bd """
        #Pido nombre de la base de datos
        nombre_bd = ctk.CTkEntry(marco, width= 150)
        nombre_bd.grid(row = 1, column = 0)

        titulo_nombre_bd = ctk.CTkLabel(marco, text="¿En que base de datos desea crear la tabla?")
        titulo_nombre_bd.grid(row= 0, column= 0, padx= 10)

        
        """ Para pedir datos de la tabla """
        nombre_tb_titulo = ctk.CTkLabel(marco, text= "¿Que nombre tendra la tabla?")
        nombre_tb = ctk.CTkEntry(marco, width= 150)

        nombre_tb_titulo.grid(row =0, column= 1)
        nombre_tb.grid(row= 1, column= 1, padx= 10, pady = 10)

        """ Boton para ejecutar ir a la segunda ventana donde se pediran los datos de la tabla """
        ir = ctk.CTkButton(marco, text="Ir a crear la tabla", command = lambda : cargar_datos())
        ir.grid(row = 1, column = 2)        
        
        def cargar_datos():
            
            """ Paso a variables los valores ingresados """ 
            bd_ingresada = nombre_bd.get()  #nombre de la base de datos
            tb_ingresada = nombre_tb.get()  #nombre de la tabla

            #Destruyo la ventana anterior 
            ventana.destroy() 

            #Creo una nueva ventana
            ventana_datos = ctk.CTkToplevel()
            ventana_datos.title("Crear tabla")
            ventana_datos.grab_set() #Pongo el foco en la ventana
            ventana_datos.geometry("400x600")

            #Lista con todos los datos necesarios para crear una columna
            campos = ['Nombre de la columna', 
                    'tipo', 
                    'len',
                    'Es clave primaria',
                    'Es clave foranea',
                    'Se autoincrementa']
                               
            """ El siguiente bucle genera 6 campos de entrada con sus respectivos encabezados tomados de campos """
            datos = []
            for i in range(len(campos)):  
                #titulos de las entradas
                encabezado = ctk.CTkLabel(ventana_datos, text = campos[i])  
                    
                #Entrada de datos
                entrada = ctk.CTkEntry(ventana_datos)

                #Varible de control para las entradas de tipo bolean 
                opcion = tk.BooleanVar()
                #Botones para manejar la variable de control.
                opciones = ctk.CTkCheckBox(ventana_datos, text= campos[i], variable = opcion)      
                    
                #Antes de la opcion 3 en la lista opciones, se muestran campos de ingreso, 
                #luego solo checkbutton de tkinter 
                if i < 3:
                    #Los datos ingresados se guardan en la lista datos
                    encabezado.pack()
                    entrada.pack()
                    datos.append(entrada)
                else:
                    opciones.pack()
                    datos.append(opcion)
            #Se ejecuta la funcion crear            
            boton = ctk.CTkButton(ventana_datos, text = "Agregar a la tabla", command = lambda : crear())
            boton.pack()

                    
            """ La siguiente funcion crea un diccionario con los elementos de la lista datos.
                Dicho diccionario , se pasa como parametro a la funcion "crear_tabla" """
            def crear():
                #listas auxiliares vacias
                datos_ingresados = []
                dic_lista = [] 
                    
                #Recorro la lista datos
                for i in datos:
                    #guardo los datos de cada iteracion de la lista datos que guarda elementos tipoo "Entry" 
                    valor = i.get()
                    if type(valor) == str:
                        valor.lower()
                    else:
                        pass
                    datos_ingresados.append(valor)

                #Se arma la sintaxis de un diccionario con la lista datos_ingresados
                dic_lista = [{'name': datos_ingresados[0],
                             'type': datos_ingresados[1],
                             'length': datos_ingresados[2],
                             'primary_key': datos_ingresados[3],
                             'auto_increment': datos_ingresados[4],
                             'not_null': datos_ingresados[5]},]
                try:
                    #Creo la tabla pasando como parametro los datos ingresados y el diccionario
                    BaseDatos.crear_tabla(f"{bd_ingresada}", f"{tb_ingresada}", dic_lista)
                except:
                    messagebox.showerror(title="Datos incorrectos", message="Algun dato que ingresaste es incorrecto.")
                    
    def ventana_eliminar_tablas(self):
        ventana = ctk.CTkToplevel()
        ventana.geometry("600x150")
        ventana.grab_set()
        ventana.title("Ventana para eliminar tablas")

        #titulo principal
        ctk.CTkLabel(ventana, text="Para borrar una tabla, ingrese los siguientes datos")

        #Pido base de datos al usuario:
    
        tit_bd = ctk.CTkLabel(ventana, text="Base de datos donde se encuentra la tabla")
        
        tit_tb = ctk.CTkLabel(ventana, text="Nombre de la tabla a borrar")
        
        #Entrada de texto para la base de datos:
        ingreso_bd = ctk.CTkEntry(ventana, width=150)
        
        #Entrada de texto para la tabla
        ingreso_tb = ctk.CTkEntry(ventana, width=150)
        
        #Boton de envio:
        enviar = ctk.CTkButton(ventana, text="Borrar", command= lambda : eliminar())
        tit_bd.pack()
        ingreso_bd.pack()
        
        tit_tb.pack()
        ingreso_tb.pack()
        ingreso_tb.pack()
        
        enviar.pack()
        
        def eliminar():
            #Guardo los datos ingresados por el usuario
            bd_ingresada = ingreso_bd.get()
            
            tb_ingresada = ingreso_tb.get()
            
            #Destruyo la venta principal
            ventana.destroy()   
            
            try:

                #Me aseguro que la tabla ingresada exista en la base de datos ingresada
                tablas =  BaseDatos.mostrar_tablas(f"{bd_ingresada}")
                if tb_ingresada not in tablas:
                    raise Exception
                else:
                    pass


                #Borro la tabla
                BaseDatos.eliminar_tabla(f"{bd_ingresada}",f"{tb_ingresada}")
                messagebox.showinfo(title="Operacion exitosa", message= f"La tabla {tb_ingresada} se elimino correctamente")

                #Vuelve a ejecutarse el programa
                self.ventana_eliminar_tablas()
            except:
                #Informo del error al ingresar los datos
                messagebox.showerror(title="Erorr", message="Se ingresaron datos incorrectos. Asegurese que la base de datos y la tabla ingresados existan")
                #Vuelve a ejecutarse el programa
                self.ventana_eliminar_tablas()

    """ Nota: No esta funcionando la destruccion de ventana """     
    def ventana_mostrar_tablas(self):
        #Creacion y ajuste de ventana principal
        ventana = ctk.CTkToplevel()
        ventana.title("Mostrar tablas")
        ventana.grab_set()#Pone el foco en la ventana
        ventana.geometry("300x100")
        
        #Pido base de datos al usuario:
        #Encabezado:
        titulo = ctk.CTkLabel(ventana, text="Ingrese la base de datos que necesita ver sus tablas")

        #Entrada de texto:
        bd = ctk.CTkEntry(ventana, width= 150)
        
        #Boton de envio
        boton = ctk.CTkButton(ventana, text= "Ver tablas", command= lambda : ver())

        #Acomodo cada elemento en la ventana:
        titulo.pack()
        bd.pack()
        boton.pack()
        
        
        def ver():
            #Guardo la base de datos ingresada 
            bd_ingresada = bd.get()   
            try:
                #Destruyo y creo una nueva ventana:
                ventana.destroy()
                tablas = ctk.CTkToplevel()
                tablas.grab_set()
                tablas.title("Mostrar tablas")
                tablas.geometry("280x250")

                #Label encabezado
                tit_box = ctk.CTkLabel(tablas, text=f"Estas son las tablas que hay en {bd_ingresada}")

                #Caja de texto
                box = ctk.CTkTextbox(tablas, width= 150, height= 200)

                #Boton para volver al menu:
                #Proximamente
                #Para mostrar las tablas en la caja de texto:

                #Ejecuto la consulta:
                datos = BaseDatos.mostrar_tablas(f"{bd_ingresada}")

                #Cargo los resultados en la caja de texto
                for elementos in datos:
                    box.insert('end', elementos) 
                    box.insert('end', '\n') #salto de linea

                #Acomodo los encabezado y la caja de texto en la ventana:
                tit_box.pack()
                box.pack()
            except:
                """ NOTA:
                 BUGS QUE ARREGALAR EN ESTE EXCEPT.  """
                messagebox.showerror(title="Error", message="La base de datos ingresada no existe. Intente nuevamente") 
                

    """ NOTA:
     HAY BUGS QUE ARREGLAR EN LA SIGUIENTE FUNCION"""    
    def ventana_mostrar_columnas(self):
        #Creacion y ajuste de ventana principal
        ventana = ctk.CTkToplevel()
        ventana.title("Mostrar columnas")
        ventana.grab_set()
        ventana.geometry("400x150")
        
        #Pido base de datos al usuario:
        #Encabezado:
        tit_bd = ctk.CTkLabel(ventana, text="Ingrese la base de datos ")
        tit_tb = ctk.CTkLabel(ventana, text = "Que tabla mostrara sus columnas?")
        #Entrada de texto:
        bd = ctk.CTkEntry(ventana, width= 120)
        tb = ctk.CTkEntry(ventana, width=120)
        
        #Boton de envio
        boton = ctk.CTkButton(ventana, text= "Ver columnas", command= lambda : ver_columnas())

        #Acomodo cada elemento en la ventana:
        
        #Para pedir base de datos:
        tit_bd.pack()
        bd.pack()

        #Para pedir tabla:
        tit_tb.pack()
        tb.pack()

        #Boton de envio
        boton.pack()
        
        def ver_columnas():
            """ Nota:
             Aun falta agregar try y except """
        #try:
            #Guardo los datos ingresados 
            bd_ingresada = bd.get() 
            tb_ingresada = tb.get()
            
            #Borro ventana principal y creo una nueva:
            ventana.destroy()
            columnas = ctk.CTkToplevel()
            columnas.title("Mostrar tablas")
            columnas.geometry("600x350")
            
            #Para mostrar las columnas:
            #Label encabezado
            tit_box = ctk.CTkLabel(columnas, text=f"Estas son las columnas que hay en {tb_ingresada}")

            #Caja de texto
            box = ctk.CTkTextbox(columnas, width= 80, height= 30)          


            #Para mostrar las tablas en la caja de texto:

            #Ejecuto la consulta:
            datos = BaseDatos.mostrar_columnas(f"{bd_ingresada}", f"{tb_ingresada}")

            #Cargo los resultados en la caja de texto:

            #Recorro los elementos de la tabla.
            for elementos in datos:
                
                #Verfico si son claves primarias, foraneas y si admiten valores nulos
                #variable = expresión_verdadera if expresión_condicional else expresión_falsa
                not_null = "No admite valores nulos." if elementos[2] == "NO" else ""
                primary_key = "Es clave primaria." if elementos[3] == "PRI" else ""
                foreign_key = "Es clave externa." if elementos[3] == "MUL" else ""

                #Guardo la cadena con los valores de la sentencia ternaria
                resultado = f": {not_null} {primary_key} {foreign_key}"
                
                box.insert('end', elementos[0], elementos[1], resultado) 
                box.insert('end', '\n') #salto de linea

            #Acomodo los encabezado y la caja de texto en la ventana:
            tit_box.pack()
            box.pack()


        #except:
            # messagebox.showerror(title="Error", message= "Se ingreso algun dato incorrecto. Asegurese que la base de datos y la tabla ingresados existan")
            # self.ventana_mostrar_columnas()
            # columnas.destroy()

    def ventana_insertar_registros(self):
        ventana = ctk.CTkToplevel()
        ventana.title("Ventana para insertar registros")
        ventana.geometry("360x250")
        ventana.grab_set()
        ctk.CTkLabel(ventana, text="Sigo trabajando en esto").pack()
        
    def ventana_eliminar_registros(self):
        """ Nota:
         Falta los try y except """
        ventana = ctk.CTkToplevel()
        ventana.title("Ventana para eliminar registros")
        ventana.grab_set()
        ventana.geometry("480x500")

        #Labels encabezados
        tit_principal = ctk.CTkLabel(ventana , text=f"Ingrese los siguientes datos del registro que desea eliminar")
        tit_bd = ctk.CTkLabel(ventana , text=f"En que base de datos se encuentra la tabla")
        tit_tb = ctk.CTkLabel(ventana , text=f"En que tabla se encuentra el registro")
        tit_condiciones = ctk.CTkLabel(ventana , text=f"Ingrese las condiciones.")
        aviso = ctk.CTkLabel(ventana, text="Ten en cuenta que, las palabras deben ir entre comillas.")
        aviso2 = ctk.CTkLabel(ventana, text="Por ejemplo: nombre = 'Nicolas' ")
        #Entrada de texto para la base de datos:
        ingreso_bd = ctk.CTkEntry(ventana, width=220)
        
        #Entrada de texto para la tabla
        ingreso_tb = ctk.CTkEntry(ventana, width=220)

        #Caja de texto para el ingreso de condiciones
        condiciones = ctk.CTkTextbox(ventana, height= 210, width= 220)
        condiciones.insert('end', "Por ejemplo id = 015")
        condiciones.bind("<Button-1>", lambda e: condiciones.delete('1.0', 'end')) 

        #Boton para el envio de datos 
        enviar = ctk.CTkButton(ventana, text= "Eliminar registro", command= lambda: eliminar())

        def eliminar():
            #Guardo los datos ingresados 
            bd_ingresada = ingreso_bd.get()
            tb_ingresada = ingreso_tb.get()
            #get("inicio", "fin")
            condicion_ingresada  = condiciones.get('1.0', 'end')
            #Elimino el regsitro
            BaseDatos.eliminar_registro(f"{bd_ingresada}", f"{tb_ingresada}", condicion_ingresada)

        tit_principal.pack()
        
        tit_bd.pack()
        ingreso_bd.pack()
        
        tit_tb.pack()
        ingreso_tb.pack()
        
        tit_condiciones.pack()
        condiciones.pack()
        aviso.pack()
        aviso2.pack()
        enviar.pack()
        
    def ventana_vaciar_tablas(self):
        ventana = ctk.CTkToplevel()
        ventana.title("Ventana para vaciar tablas")
        ventana.geometry("360x250")
        ventana.grab_set()
        ctk.CTkLabel(ventana, text="Sigo trabajando en esto").pack()

    def ventana_actualizar_tablas(self):
        ventana = ctk.CTkToplevel()
        ventana.title("Ventana para vaciar tablas")
        ventana.geometry("360x250")
        ventana.grab_set()
        ctk.CTkLabel(ventana, text="Sigo trabajando en esto").pack()
        
objeto_funciones = funcionesprograma()

class ventana_opciones():
    #Diccionario para los botones
    botones = {'Consulta SQL': objeto_funciones.ventana_consultas, 
               'Mostrar Bases de Datos': objeto_funciones.ventana_mostrar_bases_datos,
               'Eliminar Bases de Datos': objeto_funciones.ventana_eliminar_bases_datos,
               'Crear Bases de Datos': objeto_funciones.ventana_crear_bases_datos, 
               'Crear Respaldos': objeto_funciones.ventana_crear_respaldos,
               'Crear Tablas': objeto_funciones.ventana_crear_tablas,
               'Eliminar Tablas': objeto_funciones.ventana_eliminar_tablas,
               'Mostrar Tablas': objeto_funciones.ventana_mostrar_tablas,
               'Mostrar Columnas': objeto_funciones.ventana_mostrar_columnas,
               'Insertar Registros': objeto_funciones.ventana_insertar_registros,
               'Eliminar Registros': objeto_funciones.ventana_eliminar_registros,
               'Vaciar Tablas': objeto_funciones.ventana_vaciar_tablas,
               'Actualizar Registros': objeto_funciones.ventana_actualizar_tablas
               }
    def __init__(self, **kwargs):
        self.root = tk.Tk()
        self.root.title("Opciones para trabajar con Sql")
        self.root.geometry("600x600")
        cont = 0
        for i in self.botones: #es necesario llmar con self a btotnes porque estan dentro de la clase pero no dentro del init
            boton = tk.Button(
                              #master= self.root, 
                              text=i,
                              command=self.botones[i] #Paso como command el value del diccionario botones
                              )
            boton.grid(row=cont//3, column=cont%3, padx=5, pady=5)
            cont+=1

