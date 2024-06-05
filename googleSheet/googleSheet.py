import gspread
import sys
import os
# Añadir el directorio principal al PYTHONPATH
directorio_principal = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if directorio_principal not in sys.path:
    sys.path.append(directorio_principal)


from sett import credencialesJson
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build



def conexionDriveBuildService():
    scope = ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive']

    try:
        credenciales = ServiceAccountCredentials.from_json_keyfile_dict(credencialesJson, scope) #lee el archivo json con las credenciales y su scope (alcance)
        #from_json_keyfile_dict estamos pidiendo un json en formato de diccionario (dictionary) anteriormente estaba con name pues llamabamos un archivo

        # Crear un servicio de Google Drive
        drive_service = build('drive', 'v3', credentials=credenciales)
        
        print('Se ha realizado la conexion al servicio')

        return drive_service
    except Exception as e:
        print(f"ocurrió un error: {e}")


def conexionDriveCliente():
    scope = ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive']

    try:
        credenciales = ServiceAccountCredentials.from_json_keyfile_dict(credencialesJson, scope) #lee el archivo json con las credenciales y su scope (alcance)
        #from_json_keyfile_dict estamos pidiendo un json en formato de diccionario (dictionary) anteriormente estaba con name pues llamabamos un archivo
        cliente = gspread.authorize(credenciales) #Damos autorizacion para poder acceder a las funciones de la api.

        print('Se ha realizado la conexion al cliente')

        return cliente
    except Exception as e:
        print(f"ocurrió un error: {e}")    

drive_service = conexionDriveBuildService()
cliente = conexionDriveCliente()

def agregarFilasDefault(excel_id):
    rows_to_add = [
        ['Nombre Gasto', 'Valor']
    ]
    excel = cliente.open_by_key(excel_id)
    
    hojaCalculo = excel.get_worksheet(0) #Toma la primera hoja de calculo
    
    hojaCalculo.append_rows(rows_to_add)
    print(f"{len(rows_to_add)} filas agregadas en la hoja de cálculo {excel_id}.")

def agregarNuevasFilas(excel_id, hoja_trabajo_nombre, filas):
    try:
        # Abrir la hoja de cálculo por ID
        excel = cliente.open_by_key(excel_id)

        # Seleccionar la hoja de trabajo por nombre, por ahora solo agrega en la primera hoja de trabajo
        hojaCalculo = excel.get_worksheet(0)

        # Agregar filas una debajo de otra
        hojaCalculo.append_rows(filas)
        print(f"{len(filas)} filas agregadas en la hoja de cálculo {excel_id}.")
    except Exception as e:
        print(f"ocurrió un error: {e}")

def obtenerSheet(nombre_excel): #Con esta funcion puedes obtener la id de un excel para utilizarla en otras funciones
    try:
        query = f"name = '{nombre_excel}' and mimeType = 'application/vnd.google-apps.spreadsheet'" # mimeType es simplemente para definir que tipo de documento/archivo es, puedes poner imagenes, audios, words, etc.
        resultado = drive_service.files().list(q=query, fields="files(id, name)").execute()
        archivos = resultado.get('files', []) #Agarra el archivo y lo guarda en un array

        if archivos:
            objetoExcel = archivos[0]
            return objetoExcel
        else:
            return False
        
    except Exception as e:
        print(f"ocurrió un error: {e}")

def verificarExistenciaSheet(nombre_excel):
    try:
        query = f"name = '{nombre_excel}' and mimeType = 'application/vnd.google-apps.spreadsheet'" # mimeType es simplemente para definir que tipo de documento/archivo es, puedes poner imagenes, audios, words, etc.
        resultado = drive_service.files().list(q=query, fields="files(id, name)").execute()
        archivos = resultado.get('files', [])
    
        if archivos:    
            return True
        else:
            return False
        
    except Exception as e:
        print(f"ocurrió un error: {e}")


def crearExcel(nombre_excel):
    try:
        if verificarExistenciaSheet(nombre_excel):
            print('El excel ya existe, porfavor ingresa otro nombre')
            return False
        else:
            print('Creando excel')
            excelCreado = cliente.create(nombre_excel)
            compartiExcel(excelCreado)
            nuevoExcel = obtenerSheet(nombre_excel)
            agregarFilasDefault(nuevoExcel['id'])

            return True
    except Exception as e:
        print(f"ocurrió un error: {e}")
    

def compartiExcel(hoja_calculo):
    try:
        hoja_calculo.share('felipestorage2@gmail.com', perm_type = 'user', role = 'writer') 
    except Exception as e:
        print(f"ocurrió un error: {e}")

def formateoValoresPorEliminar(excel_id, hoja_trabajo, filas):
    try:
        valores_limpios = []
        mensajes  = ""

        # Abrir la hoja de cálculo por ID
        excel = cliente.open_by_key(excel_id)
       
        # Seleccionar la hoja de trabajo por nombre, por ahora solo agrega en la primera hoja de trabajo
        hoja_calculo = excel.get_worksheet(0)
       
        for fila in filas:
            valores_fila = hoja_calculo.row_values(fila)
            valores_limpios.append(valores_fila)
        
        for index, valor in enumerate(valores_limpios):
            mensaje = "Posición {}: {}\n".format(index, ", ".join(valor))
            mensajes += mensaje 
        
        return mensajes
    
    
    except Exception as e:
        print(f"ocurrió un error: {e}")



def eliminarFilas(excel_id, hoja_trabajo, filas, fila_eliminar):
    try:
        # Abrir la hoja de cálculo por ID
        excel = cliente.open_by_key(excel_id)
       
        # Seleccionar la hoja de trabajo por nombre, por ahora solo agrega en la primera hoja de trabajo
        hoja_calculo = excel.get_worksheet(0)

        if len(filas) > 1:
            hoja_calculo.delete_rows(filas[fila_eliminar])
        elif len(filas) == 1:
            hoja_calculo.delete_rows(filas[0])
        else:
            print('No existen valores en la lista') 

    except Exception as e:
        print(f"ocurrió un error: {e}")
  


def identificarValoresFilasEliminar(excel_id, hoja_trabajo ,contenido_celda):
    try:
        # Abrir la hoja de cálculo por ID
        excel = cliente.open_by_key(excel_id)
       
        # Seleccionar la hoja de trabajo por nombre, por ahora solo agrega en la primera hoja de trabajo
        hoja_calculo = excel.get_worksheet(0)
       
        #Encontrar todas las celdas
        lista_celdas = hoja_calculo.findall(contenido_celda)

        filas_a_eliminar = []

        for celda in lista_celdas:
            filas_a_eliminar.append(celda.row)

        return filas_a_eliminar

    except Exception as e:
        print(f"ocurrió un error: {e}")
 

# Verificar si existe una hoja de cálculo con un nombre específico
nombre_hoja = "algonuevoExcelGood2"


rows_to_add = [
    ['Juan', 'Perez', '30'],
    ['Ana', 'Gomez', '25']
]

#Descubrimos el excel 
objeto = obtenerSheet(nombre_hoja)

#agregarNuevasFilas(objeto['id'], objeto['name'], rows_to_add)

filas = identificarValoresFilasEliminar(objeto['id'], objeto['name'], 'ASD')

#eliminarFilas(objeto['id'], objeto['name'], filas, 0)

if len(filas) > 1:
    print('pedir que valor eliminar dentro del flujo')
    print(formateoValoresPorEliminar(objeto['id'], objeto['name'], filas))
elif len(filas) == 1:
    print('Eliminar el unico valor')
    print(formateoValoresPorEliminar(objeto['id'], objeto['name'], filas))
else:
    print('No existe niuna vaina')
    print(formateoValoresPorEliminar(objeto['id'], objeto['name'], filas))