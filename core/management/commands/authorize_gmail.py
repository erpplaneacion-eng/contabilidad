
import os
from django.core.management.base import BaseCommand
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from django.conf import settings

# Define los alcances (scopes) necesarios. Para enviar correos, usamos 'https://www.googleapis.com/auth/gmail.send'
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

class Command(BaseCommand):
    help = 'Autoriza la aplicación para acceder a la API de Gmail y guarda las credenciales.'

    def handle(self, *args, **options):
        creds = None
        token_path = os.path.join(settings.BASE_DIR, 'gmail_token.json')
        client_secret_path = os.path.join(settings.BASE_DIR, 'client_secret.json')

        # Verifica si ya existe un token
        if os.path.exists(token_path):
            self.stdout.write(self.style.SUCCESS('Las credenciales ya existen en gmail_token.json. No se necesita re-autorización.'))
            self.stdout.write('Si necesitas forzar la re-autorización, elimina el archivo gmail_token.json y vuelve a ejecutar este comando.')
            return

        # Si no hay credenciales válidas, inicia el flujo de autorización
        if not os.path.exists(client_secret_path):
            self.stdout.write(self.style.ERROR(
                'No se encuentra el archivo client_secret.json en el directorio raíz del proyecto.'
            ))
            self.stdout.write('Por favor, descárgalo desde Google Cloud Console y colócalo en la raíz del proyecto.')
            return

        flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, SCOPES)
        
        self.stdout.write(self.style.WARNING('Se iniciará el proceso de autorización en tu navegador.'))
        self.stdout.write('Por favor, sigue las instrucciones en la ventana del navegador que se abrirá.')

        try:
            creds = flow.run_local_server(port=0)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ocurrió un error durante el flujo de autorización: {e}'))
            self.stdout.write('Asegúrate de haber configurado correctamente el URI de redirección en tus credenciales de Google Cloud (http://localhost:XXXX/...).')
            return

        # Guarda las credenciales para el próximo uso
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

        self.stdout.write(self.style.SUCCESS(
            f'¡Autorización completada! Las credenciales se han guardado en: {token_path}'
        ))
