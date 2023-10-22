import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os

def send_mail(subject='Subject', message='Body', dest='santi.nieto@live.com', filename=None):

    # Crear un objeto MIMEMultipart
    mail = MIMEMultipart()

    mail['From'] = os.environ["EMAIL_ADRESS"]
    mail['To'] = dest
    mail['Subject'] = subject

    # Agregar el contenido del correo
    mail.attach(MIMEText(message, 'plain'))

    # Adjuntar el archivo, si se proporciona
    if filename is not None:
        with open(filename, "rb") as adjunto:
            archivo_mime = MIMEApplication(adjunto.read(), _subtype="pdf")  # Cambia "pdf" según el tipo de archivo
            archivo_mime.add_header('Content-Disposition', 'attachment', filename=filename)
            mail.attach(archivo_mime)

    # Iniciar la conexión con el servidor SMTP de Gmail (puedes cambiar esto para otros proveedores de correo)
    if os.environ["EMAIL_PLATFORM"] == 'outlook':
        server_smtp = smtplib.SMTP('smtp-mail.outlook.com', 587)
        server_smtp.starttls()

    # Iniciar sesión en la cuenta de Gmail
    server_smtp.login(os.environ["EMAIL_ADRESS"], os.environ["EMAIL_PASSWORD"])

    # Enviar el correo electrónico
    texto_del_correo = mail.as_string()
    server_smtp.sendmail(os.environ["EMAIL_ADRESS"], dest, texto_del_correo)

    # Cerrar la conexión con el servidor SMTP
    server_smtp.quit()

if __name__ == '__main__':

    # Seteo variables de entorno
    os.environ["EMAIL_ADRESS"] = 'santi.nieto@live.com'
    os.environ["EMAIL_PASSWORD"] = 'N32hq7.003s'
    os.environ["EMAIL_PLATFORM"] = 'outlook'

    #
    send_mail(filename='test.pdf')