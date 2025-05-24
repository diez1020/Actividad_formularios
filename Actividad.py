import streamlit as st 
import pandas as pd
import datetime
import sqlite3
import re

st.set_page_config(page_title='ACTIVIDAD', page_icon='📋')
st.title('ACTIVIDAD')

# crear la BBDD y la tabla si no existe
def inicializar_db():
    conexion = sqlite3.connect('Registros.db')
    cursor = conexion.cursor()
    cursor.execute('''
                CREATE TABLE IF NOT EXISTS DATOS(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   nombre TEXT,
                   apellido TEXT,
                   usuario TEXT,
                   password TEXT,
                   fecha_registro TEXT
                )
                   ''') 
    conexion.commit()
    conexion.close()

def inicializar_historial():
    conexion = sqlite3.connect('Registros.db')
    cursor = conexion.cursor()
    cursor.execute('''
                CREATE TABLE IF NOT EXISTS HISTORIAL(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   usuario TEXT,
                   accion TEXT,
                   fecha_hora TEXT
                    )
                   ''')
    conexion.commit()
    conexion.close()

def registrar_clientes(nombre, apellido, usuario, password):
    conexion = sqlite3.connect('Registros.db')
    cursor = conexion.cursor()
    fecha = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    cursor.execute("SELECT id FROM DATOS WHERE usuario = ? AND password = ?", (usuario, password))
    if cursor.fetchone():
        conexion.close()
        return False
    
    # insertar nuevo cliente
    cursor.execute("INSERT INTO DATOS (nombre, apellido, usuario, password, fecha_registro) VALUES ( ?, ?, ?, ?, ?)", (nombre, apellido, usuario, password, fecha))
    conexion.commit()
    conexion.close()
    return True

def verificar_cliente(usuario, password):
    conexion = sqlite3.connect('Registros.db')
    cursor = conexion.cursor()
    cursor.execute("SELECT id, password FROM DATOS WHERE usuario = ?", (usuario,))
    resultado = cursor.fetchone()
    conexion.close()
    if resultado:
        return resultado[1] == password # ¿la contraseña que esta guardada es igual a la que escribio el usuario?
    else:
        return None

def registrar_accion(usuario, accion):
    conexion = sqlite3.connect('Registros.db')
    cursor = conexion.cursor()
    fecha = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    cursor.execute("INSERT INTO HISTORIAL (usuario, accion, fecha_hora) VALUES (?, ?, ?)", (usuario, accion, fecha))
    conexion.commit()
    conexion.close()

def verificar_requisitos_contrasena(password):
    requisitos = {
        "Al menos 8 caracteres": len(password)>=8,
        "Al menos una minuscula": bool(re.search(r"[a-z]", password)),
        "Al menos una mayuscula": bool(re.search(r"[A-Z]", password)),
        "Al menos un numero": bool(re.search(r"[0-9]", password)),
        "Al menos un caracter especial": bool(re.search(r"[!@#$%^&*(),]", password))
    }
    return requisitos

def cargar_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>",unsafe_allow_html=True)

def color_db(columnas):
        colores = []
        for i in range(len(columnas)):
            if i%2 == 0:
                colores.append('background-color:rgb(79, 101, 155)')
            else:
                colores.append('background-color: rgb(117, 133, 255)')
        return colores



inicializar_db()
inicializar_historial()
cargar_css("style.css")
#menu lateral
menu = ['INICIO','LOGIN', 'ACCESO A BBDD','REGISTRO DE ACCIONES']
seleccion = st.sidebar.selectbox('Selecciona un tema', menu)

if seleccion == 'INICIO':
    st.header('BIENVENIDO')
    st.write(
        '''
        Aqui encontraras:
        - INICIO DE SESION 🔓
        - Registro de usuario y contraseña 🔑
        - Visualización y descarga de la BBDD 📋
        '''
    )


elif seleccion == 'LOGIN':
    st.title('LOGIN')

    if "mostrar_registro" not in st.session_state:
        st.session_state.mostrar_registro = False
    
    # login
    if not st.session_state.mostrar_registro:
        with st.form(key='login_form'):
            usario_login = st.text_input('USER')
            contrasena_login = st.text_input('PASSWORD',type='password')
            enviar_login = st.form_submit_button(label='Iniciar sesion')

        if enviar_login:
            if usario_login.strip() == '' or contrasena_login.strip() == '':
                st.warning('Por favor completa todos los campos')
                registrar_accion(usario_login, "Intento de inicio de sesion con campos vacios")
            else:
                validacion = verificar_cliente(usario_login, contrasena_login)
                if validacion is None:
                    st.error('Usuario no registrado')
                    registrar_accion(usario_login, "Intento de sesion con usuario no registrado")
                elif validacion:
                    
                    st.success(f'Bienvenid@ {usario_login}!')
                    st.image('thumb_up.png',caption='thumb up',width=500)
                    registrar_accion(usario_login, "sesion iniciada con exito")
                else:
                    st.error('Usuario o contraseña incorrecta')
        if st.button("No tienes cuenta? Registrate"):
            st.session_state.mostrar_registro = True
            st.rerun()

    # registro
    else:
        st.subheader('Formulario de registro')
        with st.form(key='registro_form'):
            nuevo_nombre = st.text_input('Nombre')
            nuevo_apellido = st.text_input('Apellido')
            nuevo_usuario = st.text_input('Elige un nombre de usuario')
            nueva_contrasena = st.text_input('Elige una contraseña', type='password')
            if nueva_contrasena:
                st.markdown('Requisitos de la contraseña:')
                requisitos = verificar_requisitos_contrasena(nueva_contrasena)
                for k,v in requisitos.items():
                    if v:
                        st.markdown(f"✔️{k}")
                    else:
                        st.markdown(f"❌{k}")
            enviar_registro = st.form_submit_button(label='Registrarse')
        if enviar_registro:
            if nuevo_nombre.strip() == '' or nuevo_apellido.strip() == '' or nuevo_usuario.strip() == '' or nueva_contrasena.strip() == '':
                st.warning('Por favor completa todos los campos')
            elif not all(verificar_requisitos_contrasena(nueva_contrasena).values()):
                st.error('Requisitos no cumplidos')
            elif registrar_clientes(nuevo_nombre,nuevo_apellido,nuevo_usuario,nueva_contrasena):
                st.success(f'Usuario {nuevo_usuario} creado con exito')
                st.session_state.mostrar_registro = False
            else:
                st.error('El usuario ya existe en la BBDD')
        
        if st.button('¿Ya tienes una cuenta? Inicia sesion'):
            st.session_state.mostrar_registro = False
elif seleccion == 'ACCESO A BBDD':
    st.markdown('---')
    st.header('🔐 Acceso a base de datos')

    # contraseña para ver la base de datos
    clave_correcta = "gaydier1011"

    constrasena_visualizar = st.text_input('Ingresa la contraseña para ver la base de datos', type='password')
    archivo_db = st.file_uploader('Sube el archivo .db de sqlite3', type=['db'])

    if archivo_db and constrasena_visualizar:
        if constrasena_visualizar == clave_correcta:
            # guardar el archivo subido
            ruta_temporal = 'subida_temp.db'
            with open(ruta_temporal, 'wb') as f:
                f.write(archivo_db.read())
            
            # conectarse y mostrar las tablas
            conn = sqlite3.connect(ruta_temporal)
            cursor = conn.cursor()

            # obtener las tablas
            cursor.execute('SELECT name FROM sqlite_master WHERE type = "table"')
            tablas = cursor.fetchall()

            if tablas:
                st.success('✔️ Acceso concedido. Mostrando tablas:')
                for nombre_tabla in tablas:
                    nombre = nombre_tabla[0]
                    st.subheader(f'📋 Tabla: {nombre}')
                    df = pd.read_sql(f'SELECT * FROM {nombre}', conn)
                    st.dataframe(df.style.apply(color_db, axis=0))
            else:
                st.info('La base de datos no contiene tablas')
            conn.close()
        else:
            st.error('❌ Contraseña incorrecta. BOBO')

elif seleccion == 'REGISTRO DE ACCIONES':
    st.header('🗃️ Acciones que han realizado los usuarios')
    clave_correcta = "gaydier1011"

    constrasena_visualizar = st.text_input('Ingresa la contraseña para ver la base de datos', type='password')
    

    if constrasena_visualizar:
        if constrasena_visualizar == clave_correcta:

            conexion = sqlite3.connect('Registros.db')
            df_historial = pd.read_sql_query("SELECT * FROM HISTORIAL ORDER BY fecha_hora DESC", conexion) # ordena todo en orden descente segun la fecha y hora
            conexion.close()

            if not df_historial.empty:
                st.dataframe(df_historial.style.apply(color_db, axis=0))
            else:
                st.info('No hay acciones registradas aun')

