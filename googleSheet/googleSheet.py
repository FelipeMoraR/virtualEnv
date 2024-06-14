import gspread
import sys
import os
# Añadir el directorio principal al PYTHONPATH
directorio_principal = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if directorio_principal not in sys.path:
    sys.path.append(directorio_principal)


from sett import credencialesJson
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build



def conexionSheetBuildService():
    scope = ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive']

    try:
        credenciales = ServiceAccountCredentials.from_json_keyfile_dict(credencialesJson, scope) #lee el archivo json con las credenciales y su scope (alcance)
        #from_json_keyfile_dict estamos pidiendo un json en formato de diccionario (dictionary) anteriormente estaba con name pues llamabamos un archivo

        # Crear un servicio de Google Drive
        sheet_service = build('sheets', 'v4', credentials=credenciales)
        
        print('Se ha realizado la conexion al servicio de google sheet')

        return sheet_service
    except Exception as e:
        print(f"ocurrió un error: {e}")


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

def agregarFilasDefault(excel_id, hoja_trabajo_nombre, cliente):
    rows_to_add = [
        ['Nombre Gasto', 'Valor']
    ]
    excel = cliente.open_by_key(excel_id)
    
    hojaCalculo = excel.worksheet(hoja_trabajo_nombre)
    
    hojaCalculo.append_rows(rows_to_add)
    print(f"{len(rows_to_add)} filas agregadas en la hoja de cálculo {excel_id}.")

def agregarNuevasFilas(excel_id, hoja_trabajo_nombre, filas, cliente):
    try:
        # Abrir la hoja de cálculo por ID
        excel = cliente.open_by_key(excel_id)

        # Seleccionar la hoja de trabajo por nombre, por ahora solo agrega en la primera hoja de trabajo
        hojaCalculo = excel.worksheet(hoja_trabajo_nombre)
       
        # Agregar filas una debajo de otra
        hojaCalculo.append_rows(filas)
        print(f"{len(filas)} filas agregadas en la hoja de cálculo {excel_id}.")
    except Exception as e:
        print(f"ocurrió un error: {e}")

def obtenerExcel(nombre_excel, drive_service): #Con esta funcion puedes obtener la id de un excel para utilizarla en otras funciones
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

def verificarExistenciaExcel(nombre_excel, drive_service):
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

def obtenerHojaCalculo(excel_id, nombre_hoja, sheets_service):
    try:
        hojas_resultado = sheets_service.spreadsheets().get(spreadsheetId=excel_id).execute()
        hojas = hojas_resultado.get('sheets', [])

        for hoja in hojas:
            if hoja['properties']['title'] == nombre_hoja:
                return hoja['properties']['title']
        
        print(f"No se encontró una hoja con el nombre '{nombre_hoja}'.")
        return None

    except Exception as e:
        print(f'Ocurrió un error: {e}')
        return None



def cambiarNombreHoja(excel_id, nombre_hoja, sheets_service):
    try:
        # Obtener la hoja de cálculo
        hoja_calculo = sheets_service.spreadsheets().get(spreadsheetId=excel_id).execute()
        hoja = hoja_calculo['sheets'][0]
        hoja_id = hoja['properties']['sheetId']
        
        # Cambiar el nombre de la hoja
        solicitud = {
            'requests': [
                {
                    'updateSheetProperties': {
                        'properties': {
                            'sheetId': hoja_id,
                            'title': nombre_hoja
                        },
                        'fields': 'title'
                    }
                }
            ]
        }
        
        sheets_service.spreadsheets().batchUpdate(spreadsheetId=excel_id, body=solicitud).execute()
        print(f"El nombre de la hoja se cambió a '{nombre_hoja}'")
    
    except Exception as e:
        print(f"ocurrió un error al cambiar el nombre de la hoja: {e}")

def obtenerIdHoja(excel_id, nombre_hoja, sheets_service):
    try:
        # Obtener todas las hojas del archivo
        spreadsheet = sheets_service.spreadsheets().get(spreadsheetId=excel_id).execute()
        hojas = spreadsheet.get('sheets', [])
        
        # Buscar la hoja por su nombre y devolver su ID si se encuentra
        for hoja in hojas:
            if hoja['properties']['title'] == nombre_hoja:
                return hoja['properties']['sheetId']
        
        # Si no se encuentra la hoja, retornar None
        return None
    
    except Exception as e:
        print(f"Ocurrió un error al obtener el ID de la hoja '{nombre_hoja}': {e}")
        return None
    

def crearNuevaHoja(excel_id, nombre_nueva_hoja, sheets_service, cliente):
    try:
        # Crear la solicitud para añadir una nueva hoja
        solicitud = {
            'requests': [
                {
                    'addSheet': {
                        'properties': {
                            'title': nombre_nueva_hoja
                        }
                    }
                }
            ]
        }
        
        # Ejecutar la solicitud para añadir la nueva hoja
        response = sheets_service.spreadsheets().batchUpdate(spreadsheetId=excel_id, body=solicitud).execute()
        nueva_hoja_id = response['replies'][0]['addSheet']['properties']['sheetId']
        
        print(f"Se creó una nueva hoja con el nombre '{nombre_nueva_hoja}' y el ID {nueva_hoja_id}")

        try:
            agregarFilasDefault(excel_id, nombre_nueva_hoja, cliente)
        except Exception as e: 
            print(f'Ocurrio un error {e}')

        return nueva_hoja_id
    
    except Exception as e:
        print(f"Ocurrió un error al crear la nueva hoja: {e}")
        return None

def listarHojas(excel_id, sheets_service):
    try:
        # Obtener la información del documento
        spreadsheet = sheets_service.spreadsheets().get(spreadsheetId=excel_id).execute()
        hojas = spreadsheet.get('sheets', [])

        # Extraer y mostrar los nombres de las hojas
        nombres_hojas = [hoja['properties']['title'] for hoja in hojas]
        
        print("Lista de hojas en el documento:")
        for nombre in nombres_hojas:
            print(f"- {nombre}")
        
        return nombres_hojas

    except Exception as e:
        print(f"Ocurrió un error al intentar listar las hojas: {e}")
        return None



def formateoValoresPorEliminarHojas(hojas_calculo):
    try:
        valores_limpios = []
        mensajes  = ""

        for hoja in hojas_calculo:
            valores_limpios.append(hoja)
        
        for index, valor in enumerate(valores_limpios):
        
            mensaje = "Posición {}: {}\n".format(index, valor)
            mensajes += mensaje 
        
        return mensajes
    
    
    except Exception as e:
        print(f"ocurrió un error: {e}")


def eliminarHoja(excel_id, nombre_hoja, sheets_service):
    try:
        # Obtener el ID de la hoja que queremos eliminar
        hoja_id = obtenerIdHoja(excel_id, nombre_hoja, sheets_service)
        
        if hoja_id is None:
            print(f"No se encontró la hoja '{nombre_hoja}' en el documento con ID '{excel_id}'")
            return False
        
        # Crear la solicitud para eliminar la hoja
        solicitud = {
            'requests': [
                {
                    'deleteSheet': {
                        'sheetId': hoja_id
                    }
                }
            ]
        }
        
        # Ejecutar la solicitud para eliminar la hoja
        response = sheets_service.spreadsheets().batchUpdate(spreadsheetId=excel_id, body=solicitud).execute()
        
        print('response => ',response)
        print(f"Se eliminó la hoja '{nombre_hoja}' del documento con ID '{excel_id}'")
        return True
    
    except Exception as e:
        print(f"Ocurrió un error al intentar eliminar la hoja '{nombre_hoja}': {e}")
        return False

def existeHoja(excel_id, nombre_hoja, sheets_service):
    try:
        # Obtener todas las hojas del archivo
        spreadsheet = sheets_service.spreadsheets().get(spreadsheetId=excel_id).execute()
        hojas = spreadsheet.get('sheets', [])
        
        # Verificar si alguna hoja tiene el nombre especificado
        for hoja in hojas:
            if hoja['properties']['title'] == nombre_hoja:
                return True
        return False
    
    except Exception as e:
        print(f"Ocurrió un error al verificar la existencia de la hoja: {e}")
        return False

def crearExcel(nombre_excel, cliente, drive_service, sheet_service):
    try:
        if verificarExistenciaExcel(nombre_excel, drive_service):
            print('El excel ya existe, porfavor ingresa otro nombre')
            return False
        else:
            print('Creando excel')
            excelCreado = cliente.create(nombre_excel)
            compartiExcel(excelCreado)
            nuevoExcel = obtenerExcel(nombre_excel, drive_service)
            cambiarNombreHoja(nuevoExcel['id'], 'inicio', sheet_service)
            agregarFilasDefault(nuevoExcel['id'], 'inicio', cliente)
            return True
    except Exception as e:
        print(f"ocurrió un error: {e}")
    

def compartiExcel(hoja_calculo):
    try:
        hoja_calculo.share('felipestorage2@gmail.com', perm_type = 'user', role = 'writer') 
    except Exception as e:
        print(f"ocurrió un error: {e}")

def formateoValoresPorEliminar(excel_id, hoja_trabajo_nombre, filas, cliente):
    try:
        valores_limpios = []
        mensajes  = ""

        # Abrir la hoja de cálculo por ID
        excel = cliente.open_by_key(excel_id)
       
        # Seleccionar la hoja de trabajo por nombre, por ahora solo agrega en la primera hoja de trabajo
        hoja_calculo = excel.worksheet(hoja_trabajo_nombre)
       
        for fila in filas:
            valores_fila = hoja_calculo.row_values(fila)
            valores_limpios.append(valores_fila)
        
        for index, valor in enumerate(valores_limpios):
            mensaje = "Posición {}: {}\n".format(index, ", ".join(valor))
            mensajes += mensaje 
        
        return mensajes
    
    
    except Exception as e:
        print(f"ocurrió un error: {e}")



def eliminarFilas(excel_id, hoja_trabajo_nombre, filas, numero_fila_eliminar, cliente):
    try:
        # Abrir la hoja de cálculo por ID
        excel = cliente.open_by_key(excel_id)
       
        # Seleccionar la hoja de trabajo por nombre, por ahora solo agrega en la primera hoja de trabajo
        hoja_calculo = excel.worksheet(hoja_trabajo_nombre)

        if len(filas) > 1:
            hoja_calculo.delete_rows(filas[numero_fila_eliminar])
        elif len(filas) == 1:
            hoja_calculo.delete_rows(filas[0])
        else:
            print('No existen valores en la lista') 
            return False
        
        return True
    
    except Exception as e:
        print(f"ocurrió un error: {e}")
        return False
  


def identificarValoresFilasEliminar(excel_id, hoja_trabajo_nombre ,contenido_celda, cliente):
    try:
        # Abrir la hoja de cálculo por ID
        excel = cliente.open_by_key(excel_id)
       
        # Seleccionar la hoja de trabajo por nombre, por ahora solo agrega en la primera hoja de trabajo
        hoja_calculo = excel.worksheet(hoja_trabajo_nombre)
       
        #Encontrar todas las celdas
        lista_celdas = hoja_calculo.findall(contenido_celda)

        filas_a_eliminar = []

        for celda in lista_celdas:
            filas_a_eliminar.append(celda.row)

        return filas_a_eliminar

    except Exception as e:
        print(f"ocurrió un error: {e}")
 

def obtener_url_archivo(id_excel, drive_service):
    try:
        # Obtener la información del archivo
        archivo = drive_service.files().get(fileId=id_excel, fields='webViewLink').execute()

        # Extraer la URL del archivo
        url_archivo = archivo.get('webViewLink')

        return url_archivo

    except Exception as e:
        print(f"Ocurrió un error al obtener la URL del archivo: {e}")
        return None


# Conexion
#drive_service = conexionDriveBuildService()
#sheet_service = conexionSheetBuildService()
#cliente = conexionDriveCliente()

# Verificar si existe una hoja de cálculo con un nombre específico
#nombre_excel = "pedrito"
#nombre_hoja = 'pedrotestjajaja'


#rows_to_add = [
    #['Juan', 'Perez', '30'],
    #['Ana', 'Gomez', '25']
#]

#Descubrimos el excel 
#objeto = obtenerExcel(nombre_excel, drive_service)
#print(obtenerHojaCalculo(objeto['id'], nombre_hoja, sheet_service))
#print(obtener_url_archivo(objeto['id'], drive_service))
#crearNuevaHoja(objeto['id'], 'sexito2', sheet_service, cliente)
#print(existeHoja(objeto['id'], 'pruebaAlgoNoExiste', sheet_service))
#crearExcel('testV4', cliente, drive_service, sheet_service)
#IMPORTANTE PARA ELIMINAR DEBES EJECUTAR ESTA FUNCION QUE MUESTRA LA POSICION DE LOS ELEMENTOS QUE QUIERES ELIMINAR
#filas = identificarValoresFilasEliminar(objeto['id'], objeto['name'], 'Juan', cliente) #Esto da el numero de las filas del excel
#hojas = listarHojas(objeto['id'], sheet_service)
#print(formateoValoresPorEliminarHojas(hojas))
#print(formateoValoresPorEliminar(objeto['id'], objeto['name'], filas, cliente))

#eliminarFilas(objeto['id'], objeto['name'], filas, 0, cliente)

#eliminarFilas(objeto['id'], objeto['name'], filas, 0)

#if len(filas) > 1:
    #print('pedir que valor eliminar dentro del flujo')
    #print(formateoValoresPorEliminar(objeto['id'], objeto['name'], filas))
#elif len(filas) == 1:
    #print('Eliminar el unico valor')
    #print(formateoValoresPorEliminar(objeto['id'], objeto['name'], filas))
#else:
    #print('No existe niuna vaina')
    #print(formateoValoresPorEliminar(objeto['id'], objeto['name'], filas))