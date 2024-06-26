from flask import Flask, request
import sett
import services

app = Flask(__name__)
#Para correr el sv solo debes correr el codigo de esta carpeta pyhton app.py
@app.route('/bienvenido', methods = ['GET']) 
def bienvenido():
    return 'Hola mundo chatBot, desde Flask'

#Esta funcion es basicamente para conectar el bot a la nube de meta.
@app.route('/webhook', methods = ['GET'])
def verificar_token():
    try:
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if token == sett.token and challenge != None:
            print('challenge => ', challenge)
            return challenge
        else:
            print('token incorrecto')
            return 'token incorrecto', 403
    except Exception as e:
        return e, 403

@app.route('/webhook', methods = ['POST'])
def recibir_mensajes():
    try:
        body = request.get_json()
        entry = body['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        message = value['messages'][0]
        number = message['from']
        messageId = message['id']
        contacts = value['contacts'][0]
        name = contacts['profile']['name']
        
        text = services.obtenerMensajeWsp(message)
        
        services.admChatBot(text, number, messageId, name)
        print('enviado')
        return 'enviado'

    except Exception as e:
        print('No enviado' + str(e))
        return 'no enviado' + str(e)

if __name__ == '__main__':
    app.run()