import json
import time
import requests
import sett
import app

estadoUsuario = {}

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

    return text

#Esto es basicamente el metodo post de meta, con esta función el bot puede mandar los mensajes.
def enviarMensajeWsp(data):
    try:
        wsp_token = sett.wspToken
        wsp_url = sett.wspUrl
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer ' + wsp_token}
        print('se manda =>', data )
        response = requests.post(wsp_url, headers = headers, data = data)
        if response.status_code == 200:
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

#Control del flujo del bot
def admChatBot(text, number, messageId, name):
    text = text.lower()
    list = []

    if number not in estadoUsuario:
        estadoUsuario[number] = {'estado': 'inicio'}

    estado = estadoUsuario[number]['estado']

    if estado == 'inicio':
        if 'hola' in text:
            body = 'Hola, ¿qué necesitas?'
            footer = 'AsistenteWsp'
            options = ['ver un excel', 'crear un excel', 'Modificar un excel']
            listReplyData = listadoOpcionesMjs(number, options, body, footer, 'sed2', messageId)
            replyReaction = reaccionarMensaje(number, messageId, '💜')
            list.append(listReplyData)
            list.append(replyReaction)
            estadoUsuario[number]['estado'] = 'espera_opcion'
        else:
            data = formatearMensajeTexto(number, 'No entiendo, vuelve a repetir')
            list.append(data)
    
    elif estado == 'espera_opcion':
        if 'ver un excel' in text:
            estadoUsuario[number]['estado'] = 'espera_nombre_excel'
            textMsg = formatearMensajeTexto(number, 'Dime el nombre del excel')
            list.append(textMsg)
        elif 'crear un excel' in text:
            estadoUsuario[number]['estado'] = 'creando_excel'
            textMsg = formatearMensajeTexto(number, 'Vamos a crear un excel. ¿Cómo quieres nombrarlo?')
            list.append(textMsg)
        elif 'modificar un excel' in text:
            estadoUsuario[number]['estado'] = 'modificando_excel'
            textMsg = formatearMensajeTexto(number, 'Dime el nombre del excel que quieres modificar')
            list.append(textMsg)
        else:
            data = formatearMensajeTexto(number, 'No entiendo, vuelve a repetir')
            list.append(data)
    
    elif estado == 'espera_nombre_excel':
        nombre_excel = text
        estadoUsuario[number]['estado'] = 'inicio'
        textMsg = formatearMensajeTexto(number, f'El nombre del excel es: {nombre_excel}')
        list.append(textMsg)
       
    
    for item in list:
        enviarMensajeWsp(item)



