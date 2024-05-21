import json
import time
import requests
import sett

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

    if 'hola' in text:
        body = 'wenapo, que quieres'
        footer = 'chatBotGod'
        options = ['servicio 1', 'servicio 2']

        replyButtonData = generarMensajeConBotones(number, options, body, footer, 'sed1', messageId)
        replyReaction = reaccionarMensaje(number, messageId, '💜')
        list.append(replyButtonData)
        list.append(replyReaction)
    
    elif 'servicio 1' in text:
        body = 'estas son las opciones del servicio 1'
        footer = 'chatBotGod'
        options = ['servicio corneta', 'servicio poronga', 'otros servicios']

        listReplyData = listadoOpcionesMjs(number, options, body, footer, 'sed2', messageId)
        
        list.append(listReplyData)

    elif 'servicio corneta' in text:
        body = 'Estas en servicio corneta'
        footer = 'chatBotGod'
        options = ['si quiero corneta', 'no quiero corneta']

        replyButtonData = generarMensajeConBotones(number, options, body, footer, 'sed3', messageId)
        print('esta es tu reply =>', replyButtonData)
        list.append(replyButtonData)

    elif 'si quiero corneta' in text: 
        textMsg = formatearMensajeTexto(number, 'wena loco ya te voy a contactar')
        
        enviarMensajeWsp(textMsg)
        
        time.sleep(3)

        document = generarDocumento(number, sett.documentUrl, 'ahora va', 'servicio corneta.pdf')
        enviarMensajeWsp(document)
        time.sleep(3)

        body = 'te gustaria hacer otra cosa?'
        footer = 'chatBotGod'
        options = ['12345678912345678912', 'no'] #Las respuestas no pueden ser muy largas, el sistema se cae pero no te avisa, el limite es 22.

        replyButtonData = generarMensajeConBotones(number, options, body, footer, 'sed4', messageId)
        
        list.append(replyButtonData)

    elif 'si' in text:
        body = 'que otra cosa quieres hacer ?'
        footer = 'chatBotGod'
        options = ['opcion a', 'opcion b']

        listReplyData = listadoOpcionesMjs(number, options, body, footer, 'sed5', messageId)
        
        list.append(listReplyData)

    elif 'opcion a' in text:
        body = 'opcion a seleccinada, algo mas?'
        footer = 'chatBotGod'
        options = ['si, otra cosa', 'no, otra cosa']

        buttonReply = generarMensajeConBotones(number, options, body, footer, 'sed6', messageId)
        
        list.append(buttonReply)

    elif 'no, otra cosa' in text:
        textMsg = formatearMensajeTexto(number, 'wena loco te aburriste')
        list.append(textMsg)
    else :
        data = formatearMensajeTexto(number, 'no caché, que quieres?')
        list.append(data)
        
    for item in list:
        enviarMensajeWsp(item)

