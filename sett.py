from decouple import config

token = 'ChatBot'

wspToken = 'EAAEOme1CvT8BO6SGqVjgYEZA9fLEtwoPDA34A8NUKZB9se6x4F3L53KACaNy4ZCwIL2Aphh5LtZBQFU9OLDKJq4y4IqHeclSf7zuRb155I7Cdek8BiOv270fZB6ZABvRnGEqL0mReYA3FC8mo8JJiUWOMBA9ZCG8TB8sGks4st8UaxsHsZA18ld27j9KSyJXMKwZA'


wspUrl = 'https://graph.facebook.com/v19.0/331286213394604/messages'



credencialesJson = {
    "type": config('GOOGLE_TYPE'),
    "project_id": config('GOOGLE_PROJECT_ID'),
    "private_key_id": config('GOOGLE_PRIVATE_KEY_ID'),
    "private_key": config('GOOGLE_PRIVATE_KEY').replace('\\n', '\n'), #Validamos los saltos de linia haciendo reemplazando los saltos falsos(strings) por reales.
    "client_email": config('GOOGLE_CLIENT_EMAIL'),
    "client_id": config('GOOGLE_CLIENT_ID'),
    "auth_uri": config('GOOGLE_AUTH_URI'),
    "token_uri": config('GOOLE_TOKEN_URI'),
    "auth_provider_x509_cert_url": config('GOOGLE_AUTH_PROVIDER_X509'),
    "client_x509_cert_url": config('GOOGLE_CLIENT_X509'),
    "universe_domain": config('GOOGLE_UNIVERSE_DOMAIN')
}

#print(config('GOOGLE_PRIVATE_KEY')) Lo que pasa es que cuando cargas un string en un .env los saltos de linea los interpreta como \\n pero en python los saltos de linea son \n por eso se hace el replace
#La verdad no entiendo como funciona pero seh, ahora si, basicamente "re-arma" los saltos de linea para que pyhton entienda que lo son y que no son parte del string