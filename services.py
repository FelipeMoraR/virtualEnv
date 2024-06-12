import json
import time
import requests
import sett
import sys
import os

# Añadir el directorio raíz del proyecto al PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Ahora puedes importar googleSheet.py
from googleSheet import googleSheet

sheet_service = googleSheet.conexionSheetBuildService()
drive_service = googleSheet.conexionDriveBuildService()
cliente = googleSheet.conexionDriveCliente()


estadoUsuario = {}
elementosGuardar = [] #Lo que se mandará a la función.
filaGuardar = [] #fila que tiene la finalidad de ser guardada dentro de elementosGuardar 
filasEliminar = 0
MensajeFilasEliminar = ""
objectoExcel = {} #obtenerSheet() hay que utilizar esta funcion dentro de #Flujo de modificar un excel
excelModificar = {}
hojaModificar = ""
#Reconoce el tipo de mensaje y retorna el texto(mensaje).
def obtenerMensajeWsp(message):
    if 'type' not in message:
        text = 'mensaje no reconocido'
        return text
    
    #Se adentra a la estructura del json y ve que tipo de mensaje es el que se recibe, dependiendo que sea typeMessage se apunta a una parte especifica del json
    typeMessage = message['type']
    if typeMessage == 'text':
        text = message['text']['body']
    elif typeMessage == 'button':
        text = message['button']['text']
    elif typeMessage == 'interactive' and message['interactive']['type'] == 'list_reply':
        text = message['interactive']['list_reply']['title']
    elif typeMessage == 'interactive' and message['interactive']['type'] == 'button_reply':
        text = message['interactive']['button_reply']['title']
    else:
        text = 'mensaje no reconocido'
    print('este es el texto => ', text)
    return text

#Esto es basicamente el metodo post de meta, con esta función el bot puede mandar los mensajes.
def enviarMensajeWsp(data):
    try:
        wsp_token = sett.wspToken
        wsp_url = sett.wspUrl
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer ' + wsp_token}
        response = requests.post(wsp_url, headers = headers, data = data)
        
        print('status =>', response.status_code)
        print('status =>', response.text)

        if response.status_code == 200:
            print('se manda =>', data )
            return 'mensaje enviado', 200
        else:
            return 'error al enviar mensaje', response.status_code
    
    except Exception as e:
        return e, 403

#Esta funcion estructura el mensaje para que el bot lo envie, por eso sus parametros tienen el numero y el texto, estas estructuras se encuentran en el postman que provee la documentacion
def formatearMensajeTexto(number, text):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",    
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "body": text
            }
        }
    )
    return data

def generarMensajeConBotones(number, options, body, footer, sedd, messageId):
    buttons = []
    for i, option in enumerate(options): #Enumerate combierte los elementos en tuplas los cuales tienen 2 valores, el indice y el elemento en si, en este caso estamos especificando que i es el indice y option el elemento en si.
        buttons.append( #Rellenamos la estructura de las opciones(botones) en una lista para luego pasarla al json "padre"
            {
                "type": "reply",
                "reply": {
                    "id": sedd + "_btn_" + str(i + 1),
                    "title": option
                }
            }
        )

    data = json.dumps( #Json padre
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": body
                },
                "footer": {
                    "text": footer
                },
                "action": {
                    "buttons": buttons
                }
            }
        }
    )
    return data

#Genera una lista de opciones dentro de wsp
def listadoOpcionesMjs(number, options, body, footer, sedd, messageId):
    rows = []
    for i, option in enumerate(options):
        rows.append(
            {
                "id": sedd + "_row_" + str(i + 1),
                "title": option,
                "description": ""
            }
        )

    data = json.dumps(
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": number,
                "type": "interactive",
                "interactive": {
                    "type": "list",
                    "body": {
                        "text": body
                    },
                    "footer": {
                        "text": footer
                    },
                    "action": {
                        "button": "Ver opciones",
                        "sections": [
                            {
                                "title": "Secciones",
                                "rows": rows
                                            
                                            
                                        
                            }
                            
                        ]
                    }
                }
            }

        
    )

    return data

def generarDocumento(number, url, caption, fileName):
    #dumps transforma un diccionario o una lista en un texto formato JSON
    data = json.dumps(
        
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": number,
                "type": "document",
                "document": {
                    "link": url,
                    "caption": caption,
                    "filename": fileName
                    }
            }
        
    )
    
    return data

def reaccionarMensaje(number, messageId, emoji):
    data = json.dumps(
        {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": number,
                "type": "reaction",
                "reaction": {
                    "message_id": messageId,
                    "emoji": emoji
                }
        }
    )

    return data

#No la he usado pero por la estructura puedo intuir que toma un mensaje especifico en base a su id y lo responde
def responderMensaje(number, messageId, text):
    data = json.dumps(        
        {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": number,
                "context": { "message_id": messageId },
                "type": "text",
                "text": {
                    "body": text
                }
        }
    )
    return data

#Marca el visto
def marcarVisto(messageId):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": messageId
        }
    )

    return data


def transformarStringToInt(text):
    try:
        numero = int(text)
        return numero >= 0
    except ValueError:
        return False


#Control del flujo del bot
def admChatBot(text, number, messageId, name):
    text = text.lower()
    list = []
    global excelModificar
    global hojaModificar
    global filasEliminar 

    if number not in estadoUsuario:
        estadoUsuario[number] = {'estado': 'inicio'}

    estado = estadoUsuario[number]['estado']

    if estado == 'inicio':
        if 'hola' in text:
            body = 'Hola, ¿qué necesitas?'
            footer = 'AsistenteWsp'
            options = ['Ver un excel', 'Crear un excel', 'Modificar un excel']
            listReplyData = generarMensajeConBotones(number, options, body, footer, 'sed1', messageId)
            replyReaction = reaccionarMensaje(number, messageId, '💜')
            list.append(listReplyData)
            list.append(replyReaction)
            estadoUsuario[number]['estado'] = 'espera_opcion'
        else:
            data = formatearMensajeTexto(number, 'No entiendo, primero SALUDAME')
            list.append(data)
            
            
            
    
    #Flujo que define que opcion va a tomar, si crear , ver o modificar
    elif estado == 'espera_opcion':
        if text == 'salir':
            estadoUsuario[number]['estado'] = 'inicio' 
            data = formatearMensajeTexto(number, 'Apagando...')
            enviarMensajeWsp(data)
            
        
        elif 'ver un excel' in text:
            estadoUsuario[number]['estado'] = 'ver_excel_pedir_nombre'
            textMsg = formatearMensajeTexto(number, 'Dime el nombre del excel')
            list.append(textMsg)
        elif 'crear un excel' in text:
            estadoUsuario[number]['estado'] = 'crear_excel'
            textMsg = formatearMensajeTexto(number, 'Vamos a crear un excel. ¿Cómo quieres nombrarlo?')
            list.append(textMsg)

        elif 'modificar un excel' in text:
            estadoUsuario[number]['estado'] = 'modificar_excel'
            textMsg = formatearMensajeTexto(number, 'Dime el nombre del excel que quieres modificar')
            list.append(textMsg)

        elif text == 'no necesito nada':
            estadoUsuario[number]['estado'] = 'inicio'
            data = formatearMensajeTexto(number, 'Hasta luego...')
            enviarMensajeWsp(data)

        else:
            data = formatearMensajeTexto(number, 'No entiendo')
            body = 'Solo entiendo estas opciones, ¿Que necesitas?'
            footer = 'AsistenteWsp'
            options = ['Ver un excel', 'Crear un excel', 'Modificar un excel']
            buttonsReplyData = generarMensajeConBotones(number, options, body, footer, 'sed2', messageId)
            list.append(data)
            list.append(buttonsReplyData)
            
            
    
    #Flujo ver excel
    elif estado == 'ver_excel_pedir_nombre':
        nombre_excel = text
        if text == 'salir':
            estadoUsuario[number]['estado'] = 'inicio' 
            data = formatearMensajeTexto(number, 'Apagando...')
            enviarMensajeWsp(data)

        elif googleSheet.verificarExistenciaExcel(nombre_excel, drive_service):
            estadoUsuario[number]['estado'] = 'otra_accion' 
            data = formatearMensajeTexto(number, 'El excel existe')
            enviarMensajeWsp(data)

            time.sleep(1)

            excel = googleSheet.obtenerExcel(nombre_excel, drive_service)
            urlExcel = googleSheet.obtener_url_archivo(excel['id'], drive_service)
            msjUrl = formatearMensajeTexto(number, urlExcel)
            enviarMensajeWsp(msjUrl)
            
            time.sleep(1)


            body = '¿Necesita otra cosa mas?'
            footer = 'AsistenteWsp'
            options = ['Si', 'No']
            listReplyData = generarMensajeConBotones(number, options, body, footer, 'sed10', messageId)
            list.append(listReplyData)  


        else:
            estadoUsuario[number]['estado'] = 'ver_excel_volver_intentar'
            data = formatearMensajeTexto(number, 'El excel NO existe')
            body = '¿Quieres volver a intentar?'
            footer = 'AsistenteWsp'
            options = ['Si', 'No']
            listReplyData = generarMensajeConBotones(number, options, body, footer, 'sed3', messageId)
            list.append(data)
            list.append(listReplyData)    
    
    #Estado si desea volver a intentarlo de ver un excel
    elif estado == 'ver_excel_volver_intentar':
        if text == 'si':
            estadoUsuario[number]['estado'] = 'ver_excel_pedir_nombre'
            data = formatearMensajeTexto(number, 'Ingrese el nombre del excel')
            list.append(data)

        elif text == 'no':
            estadoUsuario[number]['estado'] = 'inicio'
            data = formatearMensajeTexto(number, 'Chau me voy a dormir')
            list.append(data)
        else:
            data = formatearMensajeTexto(number, 'Mensaje erroneo')
            list.append(data)

            body = '¿Quieres volver a intentar?'
            footer = 'AsistenteWsp'
            options = ['Si', 'No']
            listReplyData = generarMensajeConBotones(number, options, body, footer, 'sed4', messageId)
            list.append(listReplyData)
    
    #Flujo crear un excel
    elif estado == 'crear_excel':
        nombre_crear_excel = text

        data = formatearMensajeTexto(number, 'Espere un momento...')
        enviarMensajeWsp(data)
            
        time.sleep(1)

        if text == 'salir':
            estadoUsuario[number]['estado'] = 'inicio' 
            data = formatearMensajeTexto(number, 'Apagando...')
            enviarMensajeWsp(data)

        elif googleSheet.crearExcel(nombre_crear_excel, cliente, drive_service, sheet_service):
            estadoUsuario[number]['estado'] = 'otra_accion' 
            

            mensajeCreacion = formatearMensajeTexto(number, 'Documento se ha creado, enviando url...')
            enviarMensajeWsp(mensajeCreacion) 

            time.sleep(1)
            objExcelTmp = googleSheet.obtenerExcel(nombre_crear_excel, drive_service)
            urlExcelCreado = googleSheet.obtener_url_archivo(objExcelTmp['id'], drive_service)


            mensajeUrl = formatearMensajeTexto(number, urlExcelCreado)
            enviarMensajeWsp(mensajeUrl) 

            body = '¿Necesita otra cosa mas?'
            footer = 'AsistenteWsp'
            options = ['Si', 'No']
            listReplyData = generarMensajeConBotones(number, options, body, footer, 'sed12', messageId)
            list.append(listReplyData) 

        else:
            estadoUsuario[number]['estado'] = 'espera_opcion'
            data = formatearMensajeTexto(number, 'Ya existe un excel con ese nombre')
            enviarMensajeWsp(data)

            time.sleep(1)

            body = 'Hola, ¿qué necesitas?'
            footer = 'AsistenteWsp'
            options = ['Ver un excel', 'Crear un excel', 'Modificar un excel']
            listReplyData = generarMensajeConBotones(number, options, body, footer, 'sed5', messageId)
           
            list.append(listReplyData)
    
    #Flujo de modificar un excel
    elif estado == 'modificar_excel':
        nombre_buscar_excel = text
        if text == 'salir':
            estadoUsuario[number]['estado'] = 'inicio' 
            data = formatearMensajeTexto(number, 'Apagando...')
            enviarMensajeWsp(data)

        elif googleSheet.verificarExistenciaExcel(nombre_buscar_excel, drive_service):
            estadoUsuario[number]['estado'] = 'modificar_excel_elegir_hoja' 
            data = formatearMensajeTexto(number, 'Excel encontrado')
            enviarMensajeWsp(data)

            time.sleep(1)

            #Aqui habría que crear el objetoExcel
            excelModificar = googleSheet.obtenerExcel(nombre_buscar_excel, drive_service)
            
            data2 = formatearMensajeTexto(number, '¿Que hoja de trabajo quieres afectar?')
            enviarMensajeWsp(data2)



            
        else:
            estadoUsuario[number]['estado'] = 'modificar_excel_volver_intentar'
            data = formatearMensajeTexto(number, 'El excel NO existe')
            body = '¿Quieres volver a intentar modificar un excel?'
            footer = 'AsistenteWsp'
            options = ['Si', 'No']
            listReplyData = generarMensajeConBotones(number, options, body, footer, 'sed6', messageId)
            list.append(data)
            list.append(listReplyData) 

    elif estado == 'modificar_excel_elegir_hoja':
        if googleSheet.obtenerHojaCalculo(excelModificar['id'], text, sheet_service):
            
            data = formatearMensajeTexto(number, 'Hoja encontrada')
            enviarMensajeWsp(data)

            hojaModificar = googleSheet.obtenerHojaCalculo(excelModificar['id'], text, sheet_service)
            estadoUsuario[number]['estado'] = 'modificar_excel_elegir_accion' 
            
            time.sleep(1)
            
            print('esta es la hoja => ', hojaModificar)
            body = '¿Que deseas realizar en la hoja?'
            footer = 'AsistenteWsp'
            options = ['Eliminar un gasto', 'Agregar un gasto']
            listReplyData = generarMensajeConBotones(number, options, body, footer, 'sed13', messageId)
           
            list.append(listReplyData) 
        else:
            estadoUsuario[number]['estado'] = 'modificar_excel_volver_intentar_hoja' 
            data = formatearMensajeTexto(number, 'Hoja NO encontrada')
            enviarMensajeWsp(data)

            time.sleep(1)

            body = '¿Desea volver a intentar ingresar un nombre de una hoja?'
            footer = 'AsistenteWsp'
            options = ['Si', 'No']
            listReplyData = generarMensajeConBotones(number, options, body, footer, 'sed13', messageId)
           
            list.append(listReplyData) 

    elif estado == 'modificar_excel_volver_intentar_hoja':
        if text == 'si':
            estadoUsuario[number]['estado'] = 'modificar_excel_elegir_hoja'
            data2 = formatearMensajeTexto(number, '¿Que hoja de trabajo quieres afectar?')
            enviarMensajeWsp(data2)

        elif text == 'no':
            excelModificar.clear() #Limpiamos
            hojaModificar.clear() #Limpiamos
            estadoUsuario[number]['estado'] = 'otra_accion'

            print('ESTADO DE LA HOJA LUEGO DE UN NO => ', hojaModificar)

            body = '¿Necesita otra cosa mas?'
            footer = 'AsistenteWsp'
            options = ['Si', 'No']
            listReplyData = generarMensajeConBotones(number, options, body, footer, 'sed24', messageId)
            list.append(listReplyData) #Esto es para mandar mensajes
        else:
            data = formatearMensajeTexto(number, 'Mensaje erroneo')
            list.append(data)

            body = '¿Desea volver a intentar ingresar un nombre de una hoja?'
            footer = 'AsistenteWsp'
            options = ['Si', 'No']
            listReplyData = generarMensajeConBotones(number, options, body, footer, 'sed40', messageId)
            list.append(listReplyData)


    #Flujo modificar un excel, eleccion de funcion 
    elif estado == 'modificar_excel_elegir_accion':
        
        if text == 'salir':
            estadoUsuario[number]['estado'] = 'inicio' 
            data = formatearMensajeTexto(number, 'Apagando...')
            enviarMensajeWsp(data)
        elif 'eliminar un gasto' in text:
            estadoUsuario[number]['estado'] = 'modificar_excel_eliminar_nombre_gasto' #AQUI DEBERIA PEDIR EL NOMBRE DE LA HIJO DE CALCULO
            data = formatearMensajeTexto(number, 'Ingrese el nombre a eliminar.')
            list.append(data)
        elif 'agregar un gasto' in text:
            estadoUsuario[number]['estado'] = 'modificar_excel_agregar_nombre_gasto'
            data = formatearMensajeTexto(number, 'Ingrese el nombre a agregar.')
            list.append(data)
        else:
            body = 'No entendí, seleccione una de las siguientes opciones'
            footer = 'AsistenteWsp'
            options = ['Eliminar un gasto', 'Agregar un gasto']
            listReplyData = generarMensajeConBotones(number, options, body, footer, 'sed14', messageId)
           
            list.append(listReplyData)

    #Flujo eliminar un gasto
    elif estado == 'modificar_excel_eliminar_nombre_gasto':
        nombreGasto = text
        filasEliminar = googleSheet.identificarValoresFilasEliminar(excelModificar['id'], hojaModificar, nombreGasto, cliente) #Esto trae las filas de lo buscado

        if len(filasEliminar) > 1:
            MensajeFilasEliminar = googleSheet.formateoValoresPorEliminar(excelModificar['id'], hojaModificar, filasEliminar, cliente)
            data = formatearMensajeTexto(number, MensajeFilasEliminar)
            enviarMensajeWsp(data)

            time.sleep(1)

            msj2 = formatearMensajeTexto(number, 'Seleccione una opcion mediante el numero de su posicion')
            enviarMensajeWsp(msj2)
            estadoUsuario[number]['estado'] = 'modificar_excel_eliminar_listado_gastos' #RECORDAR AQUI PONR UN ESTADO PARA QUE EL USUARIO SELECCIONE UNA OPCION
        elif len(filasEliminar) == 1:
            data = formatearMensajeTexto(number, 'Eliminando fila...')
            enviarMensajeWsp(data)
            googleSheet.eliminarFilas(excelModificar['id'], hojaModificar, filasEliminar, 0, cliente) #Esto ya funciona

            time.sleep(1)             

            data2 = formatearMensajeTexto(number, 'Fila eliminada')
            enviarMensajeWsp(data2)

            time.sleep(1)

            body = '¿Necesita otra cosa mas?'
            footer = 'AsistenteWsp'
            options = ['Si', 'No']
            listReplyData = generarMensajeConBotones(number, options, body, footer, 'sed18', messageId)
            list.append(listReplyData) #Esto es para mandar mensajes


            estadoUsuario[number]['estado'] = 'otra_accion' 
        else:
            
            data = formatearMensajeTexto(number, 'No existe el valor')
            enviarMensajeWsp(data)

            time.sleep(1)

            body = '¿Quieres volver a intentar eliminar un gasto?'
            footer = 'AsistenteWsp'
            options = ['Si', 'No']
            listReplyData = generarMensajeConBotones(number, options, body, footer, 'sed7', messageId)
            list.append(listReplyData)

            estadoUsuario[number]['estado'] = 'modificar_excel_eliminar_volver_intentar' 
     
    elif estado == 'modificar_excel_eliminar_listado_gastos':

        if transformarStringToInt(text):
            text_num = int(text)
            data = formatearMensajeTexto(number, f'Intenando eliminar la posicion {text_num}')
            enviarMensajeWsp(data)

            estadoEliminar = googleSheet.eliminarFilas(excelModificar['id'], hojaModificar, filasEliminar, text_num, cliente)
            
            time.sleep(1)

            if estadoEliminar:
                data2 = formatearMensajeTexto(number, f'Posicion {text_num} eliminada')
                enviarMensajeWsp(data2)
                
                time.sleep(1)

                body = '¿Necesita eliminar otro gasto?'
                footer = 'AsistenteWsp'
                options = ['Si', 'No']
                listReplyData = generarMensajeConBotones(number, options, body, footer, 'sed18', messageId)
                list.append(listReplyData) #Esto es para mandar mensajes

                estadoUsuario[number]['estado'] = 'modificar_excel_eliminar_volver_intentar'
            else: 
                estadoUsuario[number]['estado'] = 'modificar_excel_eliminar_volver_intentar'

                data3 = formatearMensajeTexto(number, 'Valor ingresado fuera del rango')
                enviarMensajeWsp(data3)

                time.sleep(1)

                body = '¿Quieres volver a intentar eliminar un gasto?'
                footer = 'AsistenteWsp'
                options = ['Si', 'No']
                listReplyData = generarMensajeConBotones(number, options, body, footer, 'sed20', messageId)
                list.append(listReplyData)
        else:
            estadoUsuario[number]['estado'] = 'modificar_excel_eliminar_volver_intentar'

            data = formatearMensajeTexto(number, 'Valor ingresado invalido')
            enviarMensajeWsp(data)

            time.sleep(1)

            body = '¿Quieres volver a intentar eliminar un gasto?'
            footer = 'AsistenteWsp'
            options = ['Si', 'No']
            listReplyData = generarMensajeConBotones(number, options, body, footer, 'sed20', messageId)
            list.append(listReplyData)

    elif estado == 'modificar_excel_eliminar_volver_intentar':
        if text == 'si':
            estadoUsuario[number]['estado'] = 'modificar_excel_eliminar_nombre_gasto'
            data = formatearMensajeTexto(number, 'Ingrese el nombre del gasto a eliminar')
            list.append(data)

        elif text == 'no':
            filasEliminar = 0 #Limpiamos
            estadoUsuario[number]['estado'] = 'otra_accion'

            body = '¿Necesita otra cosa mas?'
            footer = 'AsistenteWsp'
            options = ['Si', 'No']
            listReplyData = generarMensajeConBotones(number, options, body, footer, 'sed24', messageId)
            list.append(listReplyData) #Esto es para mandar mensajes
        else:
            data = formatearMensajeTexto(number, 'Mensaje erroneo')
            list.append(data)

            body = '¿Quieres volver a intentar eliminar un gasto?'
            footer = 'AsistenteWsp'
            options = ['Si', 'No']
            listReplyData = generarMensajeConBotones(number, options, body, footer, 'sed7', messageId)
            list.append(listReplyData)

    #Flujo AGREGAR GASTO
    elif estado == 'modificar_excel_agregar_nombre_gasto':
        
        filaGuardar.append(text)

        data = formatearMensajeTexto(number, 'Ingrese el precio')
        enviarMensajeWsp(data)

        estadoUsuario[number]['estado'] = 'modificar_excel_agregar_precio_gasto' 

    elif estado == 'modificar_excel_agregar_precio_gasto':
        filaGuardar.append(text)
        elementosGuardar.append(filaGuardar.copy())
        filaGuardar.clear()
        
        data = formatearMensajeTexto(number, 'Se agregó el gasto a la lista')
        enviarMensajeWsp(data)

        print('elementos a guardar => ', elementosGuardar)
        
        time.sleep(1)

        body = '¿Desea agregar otro gasto?'
        footer = 'AsistenteWsp'
        options = ['Si', 'No']
        listReplyData = generarMensajeConBotones(number, options, body, footer, 'sed15', messageId)
           
        list.append(listReplyData) 

        estadoUsuario[number]['estado'] = 'modificar_excel_agregar_otro_gasto'

    elif estado == 'modificar_excel_agregar_otro_gasto':
        if text == 'si':
            estadoUsuario[number]['estado'] = 'modificar_excel_agregar_nombre_gasto'
            data = formatearMensajeTexto(number, 'Ingrese el nombre a agregar.')
            list.append(data)
        elif text == 'no': #IMPORTANTE !!! AQUI DEBES EJECUTAR LAS FUNCIONES PARA AGREGAR LAS FILAS DENTRO DEL EXCEL
            estadoUsuario[number]['estado'] = 'otra_accion'
            data = formatearMensajeTexto(number, 'Agregando los elementos al excel....')
            enviarMensajeWsp(data) 
            
            googleSheet.agregarNuevasFilas(excelModificar['id'], hojaModificar, elementosGuardar,cliente)

            elementosGuardar.clear() #Esto se limpia para una proxima inyeccion de filas.
            excelModificar.clear() #Esto limpia el objeto para usarlo en otro excel

            time.sleep(1)

            body = '¿Necesita otra cosa mas?'
            footer = 'AsistenteWsp'
            options = ['Si', 'No']
            listReplyData = generarMensajeConBotones(number, options, body, footer, 'sed17', messageId)
            list.append(listReplyData) #Esto es para mandar mensajes
            
        else:
            body = 'No entendi, selecciona una opcion, ¿Desea agregar otro gasto?'
            footer = 'AsistenteWsp'
            options = ['Si', 'No']
            listReplyData = generarMensajeConBotones(number, options, body, footer, 'sed16', messageId)
           
            list.append(listReplyData) 

        

    elif estado == 'modificar_excel_volver_intentar':
        if text == 'si':
            estadoUsuario[number]['estado'] = 'modificar_excel'
            data = formatearMensajeTexto(number, 'Ingrese el nombre del excel a modificar')
            list.append(data)

        elif text == 'no':
            estadoUsuario[number]['estado'] = 'inicio'
            data = formatearMensajeTexto(number, 'Chau me voy a dormir, gil.')
            list.append(data)
        else:
            data = formatearMensajeTexto(number, 'Mensaje erroneo')
            list.append(data)

            body = '¿Quieres volver a intentar modificar un excel?'
            footer = 'AsistenteWsp'
            options = ['Si', 'No']
            listReplyData = generarMensajeConBotones(number, options, body, footer, 'sed7', messageId)
            list.append(listReplyData)
        
    elif estado == 'otra_accion':
        if text == 'si':
            estadoUsuario[number]['estado'] = 'espera_opcion'
            body = 'Hola de nuevo, ¿Qué necesitas?'
            footer = 'AsistenteWsp'
            options = ['Ver un excel', 'Crear un excel', 'Modificar un excel']
            listReplyData = generarMensajeConBotones(number, options, body, footer, 'sed11', messageId)
            list.append(listReplyData)
            

        elif text == 'no':
            estadoUsuario[number]['estado'] = 'inicio'
            data = formatearMensajeTexto(number, 'Chau me voy a dormir, gil.')
            list.append(data)
        else:
            data = formatearMensajeTexto(number, 'Mensaje erroneo')
            list.append(data)

            body = 'No entendí, seleccione una opcion. ¿Necesita algo mas?'
            footer = 'AsistenteWsp'
            options = ['Si', 'No']
            listReplyData = generarMensajeConBotones(number, options, body, footer, 'sed8', messageId)
            list.append(listReplyData)

    for item in list:
        time.sleep(1)
        enviarMensajeWsp(item)



