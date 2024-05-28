import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

scope = ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive']

credenciales = ServiceAccountCredentials.from_json_keyfile_name('credenciales.json', scope) #lee el archivo json con las credenciales y su scope (alcance)

cliente = gspread.authorize(credenciales) #Damos autorizacion dando credenciales, puede descargar , compartir, crear.


sheet = cliente.create("PrimeraBase")


# Crear un servicio de Google Drive
drive_service = build('drive', 'v3', credentials=credenciales)

# sheet.share('felipestorage2@gmail.com', perm_type = 'user', role = 'writer')

def sheet_exists(sheet_name):
    query = f"name = '{sheet_name}' and mimeType = 'application/vnd.google-apps.spreadsheet'"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])
    
    if files:
        print(f"Sheet '{sheet_name}' exists.")
        return True
    else:
        print(f"Sheet '{sheet_name}' does not exist.")
        return False

# Verificar si existe una hoja de cálculo con un nombre específico
nombre_hoja = "PrimeraBase2"
existe = sheet_exists(nombre_hoja)

print(existe)