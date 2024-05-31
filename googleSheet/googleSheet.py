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

def eliminarCeldaFila(excel_id, hoja_trabajo ,contenido_celda):
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

        # Eliminar las filas de la hoja de cálculo
        for fila in reversed(filas_a_eliminar):  # Se recorren en reversa para evitar problemas con los índices, suponte si elminas el primer elemento el siguiente toma el lugar del eliminado haciendo que se eliminen cosas que no se deben ej => [0, 1, 2] elimino el primero => [0(1), 1(2)] Como se puede apreciar se rompe el orden pero si lo hacemos en reversa esto no ocurre ej => [0, 1, 2] elimino el ultimo => [0(0), 1(1)] la posicion corresponde al valor.
            hoja_calculo.delete_rows(fila)

    except Exception as e:
        print(f"ocurrió un error: {e}")
 

# Verificar si existe una hoja de cálculo con un nombre específico
nombre_hoja = "algonuevoExcelGood2"


rows_to_add = [
    ['Juan', 'Perez', '30'],
    ['Ana', 'Gomez', '25']
]

objeto = obtenerSheet(nombre_hoja)

eliminarCeldaFila(objeto['id'], objeto['name'], 'Ana')
#agregarNuevasFilas(objeto['id'], objeto['name'], rows_to_add)