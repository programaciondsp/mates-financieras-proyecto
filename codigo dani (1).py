#Código Python para consulta de series en Banxico
""""
V3 
Autor: Daniela Santos Pichardo
Fecha: 07 de octubre de 2026
Solicitud: Consulta de Banxico en tiempo real de alguna serie y cálculo de Interés Simple.
Haciendo requests en Banxico, obtener el interés simple con tasa de cetes a 28 días, enviando por gmail el reporte
de resultados. Versión extendida SMS o Whatsapp solo si no conecta por email.
"""
import time as t
import requests
import os
from dotenv import load_dotenv
from smtplib import SMTP 
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
load_dotenv()
"""
Funcion 1 conexion a banxico 1
Funcion 2 conexion a banxico series oportuno 
Funcion 3 cálculo del interés simple
Funcion 4 conexion y envio de email
Funcion 5 ménu de opciones 
"""

TOKEN= os.getenv("TOKEN_BANXICO")
EMAIL_USER= os.getenv("EMAIL_USER")
PASSWORD= os.getenv("PASSWORD")
PORTMAIL= os.getenv("PORTMAIL")
def verificar_estado(response):
    """
    Verifica si el código de estado de la respuesta es 200-
    """
    if response.status_code == 200:
        return True
    else:
        print(f"Lo siento hubo un error en la consulta a Banxico. Código de status: {response.status_code}")
        return False

def mostrar_serie(response):
    """
    Procesa el JSON y muestra los datos obtenidos de la serie.
    """
    data = response.json()
    serie = data["bmx"]["series"][0]
    titulo = serie["titulo"]
    dato = serie["datos"][0]["dato"]
    fecha = serie["datos"][0]["fecha"]

    print(f"Serie: {titulo}")
    print(f"Fecha: {fecha}")
    print(f"Valor actual: {dato}")

def consulta_de_serie_aleatoria():
    """
    Consulta de serie aleatoria de Banxico 
    (por ejemplo: Tasa de rendimiento de CETES)
    """
    print("\n ---Consultando serie aleatoria de Bnaxico---")
    #Se utilizara la serie de la Tasa de rendimiento de CETES 
    headers= {"Bmx-Token":TOKEN}
    serie= "SF43936"
    enlace= f"https://www.banxico.org.mx/SieAPIRest/service/v1/series/{serie}/datos/oportuno"
    
    try: 
        response = requests.get(url=enlace, headers = headers)
        """
        Validar el estado con la otra función
        """
        if verificar_estado(response):
            mostrar_serie(response)
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión con la API de Banxico: {e}")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

def calcular_interes_cetes (capital_inicial, tasa_cetes, plazo):
    """
    Calcula el monto final y el rendimiento de una inversión en CETES
    ocupando la formula: Capital * (1+ interes*tiempo)
    """
    #Conversión de interés en decimal y de plazo (de años a días)
    interes_decimal = tasa_cetes/100
    tiempo_años = plazo/360
    monto_final = capital_inicial * (1+ interes_decimal * tiempo_años)
    rendimiento = monto_final - capital_inicial
    return rendimiento , monto_final
def generar_reporte(tasa_cetes, capital_inicial,plazo,rendimiento,monto_final):
    """
    Genera un informe detallado en texto.
    """
    informe = f"""--- REPORTE DE CETES ---
    Estimado cliente, a continuación se mostrará un reporte de tu financiamiento en el sistema.
    - Tasa de Referencia CETES: {tasa_cetes}% anual 
    - Capital Inicial (invertida): ${capital_inicial:,.2f} MXN
    - Plazo: A 28 días
    - Monto final: ${monto_final:,.2f} MXN
    
    Este fue tu reporte. Gracias por usar Consulta de Series de Banxico. """
    return informe

def enviar_correo_reporte(destinatario, cuerpo_reporte):
    """
    Envía el reporte generado por correo electrónico utilizando SMTP de Gmail.
    """
    if not EMAIL_USER or not PASSWORD:
        print("\n Error. No se han configurado el email o password en el archivo .env")
        return
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = destinatario
        msg['Subject'] = "Reporte de Inversión  CETES  / Banxico"
        msg.attach(MIMEText(cuerpo_reporte, 'plain'))
        print("\n Conectando al servidor de correo ... ")
        puerto= int(PORTMAIL) if PORTMAIL else 587
        servidor= SMTP("smtp.gmail.com", puerto)
        servidor.starttls()
        servidor.login(EMAIL_USER, PASSWORD)
        servidor.sendmail(EMAIL_USER, destinatario, msg.as_string())
        servidor.quit()
        print(f"Correo enviado exitosamente a {destinatario}!!")
    except Exception as e:
        print(f"Hubo un error al intentar el enviar el reporte por correoelectrónico:{e}")

def opcion_cetes_correo ():
    """
    Controla la lógica para consultar CETES, calcular intereses, mostrar y enviar por correo.
    """
    headers= {"Bmx-Token": TOKEN}
    serie = "SF43936"
    enlace= f"https://www.banxico.org.mx/SieAPIRest/service/v1/series/{serie}/datos/oportuno"
    print("\n --- Cálculo de Inversiónen CETES (Banxico) ---")
    try:
        response = requests.get(url=enlace, headers=headers) 
        if verificar_estado(response):
            data=response.json()
            tasa_cetes= float(data["bmx"]["series"][0]["datos"][0]["dato"])

            capital = float(input("Ingresa el capital inicial a invertir: "))
            plazo = 28
            rendimiento, monto_final= calcular_interes_cetes(capital, tasa_cetes, plazo)
            reporte= generar_reporte(tasa_cetes, capital, plazo, rendimiento, monto_final)
            print("\n" + reporte)
            print("\n Enviando el reporte por correo electrónico...")
            correo_destino= input("Ingresa el correo al que seas que sea enviado el reporte: ").strip()
            enviar_correo_reporte(correo_destino, reporte)
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión con la API de Banxico: {e}")
    except ValueError:
        print("Error: Ingresa valores númericos válidos")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

def menu():
    """
    Despliega al usuario el menú de opciones.
    """
    while True: 
        print("----- Bienvenido a Consulta de Series de Banxico ------")
        print("1. Consulta una serie de Banxico aleatoria")
        print("2. Consulta Banxico (CETES) y calcula el interés simple")
        print("3. Salir")

        opcion= input("Selecciona una opción entre 1-3: ")
        if opcion == "1":
            consulta_de_serie_aleatoria()
        elif opcion == "2":
            opcion_cetes_correo()
        elif opcion == "3":
            print("Gracias por usar Consulta de Series de Banxico :)! ")
            break
        else: 
            print("Opción inválida, por favor ingresa una opción entre el 1 y 3")

if __name__== "__main__":
    menu()
