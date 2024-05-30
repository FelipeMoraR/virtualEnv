import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

scope = ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive']

credenciales = ServiceAccountCredentials.from_json_keyfile_name('credenciales.json', scope) #lee el archivo json con las credenciales y su scope (alcance)

cliente = gspread.authorize(credenciales) #Damos autorizacion para poder acceder a las funciones de la api.



# Crear un servicio de Google Drive
drive_service = build('drive', 'v3', credentials=credenciales)

def agregarFilasDefault(excel_id):
    rows_to_add = [
        ['Nombre Gasto', 'Valor']
    ]
    sheet = cliente.open_by_key(excel_id)
    
    worksheet = sheet.get_worksheet(0)
    
    worksheet.append_rows(rows_to_add)
    print(f"{len(rows_to_add)} filas agregadas en la hoja de cálculo {excel_id}.")


def agregarNuevasFilas(excel_id, hoja_trabajo_nombre, filas):
    # Abrir la hoja de cálculo por ID
    sheet = cliente.open_by_key(excel_id)
    # Seleccionar la hoja de trabajo por nombre, por ahora solo agrega en la primera hoja de trabajo
    worksheet = sheet.get_worksheet(0)
    # Agregar filas una debajo de otra
    worksheet.append_rows(filas)
    print(f"{len(filas)} filas agregadas en la hoja de cálculo {excel_id}.")

def obtenerSheet(nombreExcel):
    query = f"name = '{nombreExcel}' and mimeType = 'application/vnd.google-apps.spreadsheet'" # mimeType es simplemente para definir que tipo de documento/archivo es, puedes poner imagenes, audios, words, etc.
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', []) #Agarra el archivo y lo guarda en un array

    if files:
        objetoExcel = files[0]
        return objetoExcel
    else:
        return False

def verificarExistenciaSheet(nombreExcel):
    query = f"name = '{nombreExcel}' and mimeType = 'application/vnd.google-apps.spreadsheet'" # mimeType es simplemente para definir que tipo de documento/archivo es, puedes poner imagenes, audios, words, etc.
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])
    
    if files:    
        return True
    else:
        return False

def compartiExcel(hojaCalculo):
    hojaCalculo.share('felipestorage2@gmail.com', perm_type = 'user', role = 'writer') 
    return

def crearExcel(nombreExcel):
    if verificarExistenciaSheet(nombreExcel):
        print('El excel ya existe, porfavor ingresa otro nombre')
        return False
    else:
        print('Creando excel')
        sheet = cliente.create(nombreExcel)
        compartiExcel(sheet)
        nuevoExcel = obtenerSheet(nombreExcel)
        agregarFilasDefault(nuevoExcel['id'])

        return True
    

# Verificar si existe una hoja de cálculo con un nombre específico
nombre_hoja = "algonuevoExcelGood2"


rows_to_add = [
    ['Nombre', 'Apellido', 'Edad'],
    ['Juan', 'Perez', '30'],
    ['Ana', 'Gomez', '25']
]

#if obtenerSheet(nombre_hoja):
    #objExcelEncontrado = obtenerSheet(nombre_hoja)
    #agregarNuevasFilas(objExcelEncontrado['id'], objExcelEncontrado['name'], rows_to_add)
    
#else:
    #print('no pasa nah')
crearExcel(nombre_hoja)
