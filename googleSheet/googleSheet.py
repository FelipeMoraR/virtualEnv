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

def verificarExistenciaSheet(nombreExcel):
    query = f"name = '{nombreExcel}' and mimeType = 'application/vnd.google-apps.spreadsheet'" # mimeType es simplemente para definir que tipo de documento/archivo es, puedes poner imagenes, audios, words, etc.
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])
    
    if files:
        print(files)
        return True
    else:
        return False

def compartiExcel(hojaCalculo, correo):
    hojaCalculo.share(correo, perm_type = 'user', role = 'writer') 
    return

def crearExcel(nombreExcel, correo):
    if verificarExistenciaSheet(nombreExcel):
        print('El excel ya existe, porfavor ingresa otro nombre')
        return False
    else:
        print('Creando excel')
        sheet = cliente.create(nombreExcel, correo)
        compartiExcel(sheet)
        return True
    

# Verificar si existe una hoja de cálculo con un nombre específico
nombre_hoja = "testNuevo"
correo = 'felipestorage2@gmail.com'
crearExcel(nombre_hoja, correo)
