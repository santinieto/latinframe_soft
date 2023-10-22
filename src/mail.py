import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os

try:
    from src.utils import o_fmt_error
except:
    from utils import o_fmt_error

def send_mail(subject='Subject', message='Body', dest='santi.nieto@live.com', filename=None):

    # Crear un objeto MIMEMultipart
    mail = MIMEMultipart()

    mail['From'] = os.environ["EMAIL_ADRESS"]
    mail['To'] = dest
    mail['Subject'] = subject

    # Evito un error
    if message is None:
        message = ''

    # Adjuntar el archivo, si se proporciona
    if filename is not None:
        try:
            with open(filename, "rb") as adjunto:
                archivo_mime = MIMEApplication(adjunto.read(), _subtype="pdf")  # Cambia "pdf" según el tipo de archivo
                archivo_mime.add_header('Content-Disposition', 'attachment', filename=filename)
                mail.attach(archivo_mime)
        except:
            err_msg = f'Could not find file {filename} for email'
            o_fmt_error('0001', err_msg, 'Function__Send_email')
            message += f'\n\n{err_msg}'

    # Agregar el contenido del correo
    mail.attach(MIMEText(message, 'plain'))

    # Iniciar la conexión con el servidor SMTP de Gmail (puedes cambiar esto para otros proveedores de correo)
    if os.environ["EMAIL_PLATFORM"] == 'outlook':
        server_smtp = smtplib.SMTP('smtp-mail.outlook.com', 587)
        server_smtp.starttls()

    # Mensaje de error
    else:
        msg = f'Could not find platform for email'
        o_fmt_error('0002', msg, 'Function__Send_email')
        return

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

    # Envio un correo y adjunto un archivo
    send_mail(filename='test.pdf')