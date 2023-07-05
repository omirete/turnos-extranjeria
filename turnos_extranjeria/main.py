from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from datetime import datetime
from os import getenv
from dotenv import load_dotenv
from telepybot import Telepybot

load_dotenv()

def log(msg: str) -> None:
    timestamp = datetime.now().isoformat()[:19]
    print(f"{timestamp}: {msg}")

def sleep_minutes(minutes: int) -> None:
    sleep(60*minutes)

# p=28 is for Madrid
# BASE_URL = 'https://icp.administracionelectronica.gob.es/icpplustiem/index'
BASE_URL = 'https://icp.administracionelectronica.gob.es/icpplustiem/citar?p=28&locale=es'

APPOINTMENT_ID = getenv('APPOINTMENT_ID')
NIE = getenv('NIE')
FULL_NAME = getenv('FULL_NAME')
NIE_EXPIRY_DATE = getenv('NIE_EXPIRY_DATE')
USER_ID = getenv('USER_ID')

def check_appointments(driver: WebDriver):
    driver.get(BASE_URL)
    WebDriverWait(driver, 10).until(
        EC.title_contains("Proceso automático para la solicitud de cita previa")
    )
    appointmentType = Select(driver.find_element(By.ID, 'tramiteGrupo[0]'))
    appointmentType.select_by_value(APPOINTMENT_ID)
    btn_accept = driver.find_element(By.ID, 'btnAceptar')
    btn_accept.send_keys(' ')
    WebDriverWait(driver, 10).until(
        EC.title_contains("Informacion de la provincia y trámite")
    )
    btn_enter = driver.find_element(By.ID, 'btnEntrar')
    btn_enter.send_keys(' ')
    WebDriverWait(driver, 10).until(
        EC.title_contains("Rellene los campos siguientes")
    )

    input_nie = driver.find_element(By.ID, 'txtIdCitado')
    input_nie.send_keys(NIE)

    input_name_last_name = driver.find_element(By.ID, 'txtDesCitado')
    input_name_last_name.send_keys(FULL_NAME)

    input_valid_until = driver.find_element(By.ID, 'txtFecha')
    input_valid_until.send_keys(NIE_EXPIRY_DATE)
    
    btn_send = driver.find_element(By.ID, 'btnEnviar')
    btn_send.send_keys(' ')
    
    WebDriverWait(driver, 10).until(
        EC.title_contains("Información")
    )
    
    try:
        info_elem = driver.find_element(By.XPATH, '//*[contains(text(), "En este momento no hay citas disponibles")]')
        log('No appointments found')
    except Exception as e:
        log('Appointment found!')
        telegram.sendMsg(USER_ID, 'Appointment found!')
        sleep(3600*24)


if __name__ == "__main__":
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)
    telegram = Telepybot(getenv('API_TOKEN'))
    while True:
        try:
            driver.delete_all_cookies()
            check_appointments(driver)
        except Exception as e:
            log('Error checking for appointments. See detail below:')
            print(e)
            telegram.sendMsg(USER_ID, str(e))
        sleep_minutes(20)
