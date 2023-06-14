import time
from machine import Pin, PWM
import network
import socket
import usocket
try:
  import urequests as requests
except:
  import requests

import esp
esp.osdebug(None)

import gc
gc.collect()

class Servo:
    # these defaults work for the standard TowerPro SG90
    __servo_pwm_freq = 50
    __min_u10_duty = 26 - 0  # offset for correction
    __max_u10_duty = 123 - 0  # offset for correction
    min_angle = 0
    max_angle = 180
    current_angle = 0.001

    def __init__(self, pin):
        self.__initialise(pin)

    def update_settings(
        self, servo_pwm_freq, min_u10_duty, max_u10_duty, min_angle, max_angle, pin
    ):
        self.__servo_pwm_freq = servo_pwm_freq
        self.__min_u10_duty = min_u10_duty
        self.__max_u10_duty = max_u10_duty
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.__initialise(pin)

    def move(self, angle):
        # round to 2 decimal places, so we have a chance of reducing unwanted servo adjustments
        angle = round(angle, 2)
        # do we need to move?
        if angle == self.current_angle:
            return
        self.current_angle = angle
        # calculate the new duty cycle and move the motor
        duty_u10 = self.__angle_to_u10_duty(angle)
        self.__motor.duty(duty_u10)

    def __angle_to_u10_duty(self, angle):
        return (
            int((angle - self.min_angle) * self.__angle_conversion_factor)
            + self.__min_u10_duty
        )

    def __initialise(self, pin):
        self.current_angle = -0.001
        self.__angle_conversion_factor = (self.__max_u10_duty - self.__min_u10_duty) / (
            self.max_angle - self.min_angle
        )
        self.__motor = PWM(Pin(pin))
        self.__motor.freq(self.__servo_pwm_freq)


motor = Servo(pin=18)
pir = Pin(4, Pin.IN, Pin.PULL_DOWN)
pir2 = Pin(33, Pin.IN, Pin.PULL_DOWN)
phone_number = '+573175903095'
#Your callmebot API key
api_key = '7493810'


ssid = 'Manuel'
password = '01071999'
wlan = network.WLAN(network.STA_IF)

def send_message(phone_number, api_key, message):
  #set your host URL
  url = 'https://api.callmebot.com/whatsapp.php?phone='+phone_number+'&text='+message+'&apikey='+api_key

  #make the request
  response = requests.get(url)
  #check if it was successful
  if response.status_code == 200:
    print('Success!')
  else:
    print('Error')
    print(response.text)

wlan.active(True)
wlan.connect(ssid, password)

while wlan.isconnected() == False:
    pass

print('Conexion con el WiFi %s establecida' % ssid)
print(wlan.ifconfig())

a = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
a.bind(('', 80))
a.listen(3)

IFTTT_URL = '/trigger/Lista de activacion/with/key/bR9uNIoiSMN5JGO12Zz_Jklg76qFGU-zwOxMy1CHLoe'
server = 'maker.ifttt.com'
valor = 'Se activo el sensor'
ser= 'Tener en cuenta'
inf = 'para sus encuentas'

def make_ifttt_request():
    print('Connecting to', server)
    json_data = '{"value1":"' + valor + '","value2":"' + ser +'","value3":"' + inf + '"}'
    headers = {'Content-Type': 'application/json'}
    response = urequests.post('https://' + server + IFTTT_URL , data=json_data, headers=headers)
    print('Response:', response.content.decode())
    response.close()
    print('Closing Connection')
    
def web_page():

  html =  """
        <style>
            body{
                background-color: rgb(9, 145, 199);
            }
        </style>
        <center>
        <h1><b>Dispensador de Alimento</h1></b><br>
        </center>
            <body>
                <center>
                <b>Dispensador</b>
                <br>
                <div>
                    <br>
                    <a href="/?Dispensador=on"> <button style='width:100px; height:50px; background-color: #00ff00'>Encender</button></a>&nbsp;&nbsp;
                    <a href="/?Validar"> <button style='width:100px; height:50px; background-color: rgb(22, 206, 46)'>Validar Dispensador </button></a><br><br>
                </div>
                <div>
                    <a href=""><button style='width:100px; height:50px; background-color: rgb(15, 221, 77)'>Seguimiento en Excell</button></a>
                </div>
                </center>
            </body>
    """
  return html
message = 'Tu%20mascota%20necesita%20alimento'
message2 = 'Dispensador%20vac%C3%ADo'
while True: 
    conn,addr = a.accept()
    print('Nueva conexion desde:  %s' % str(addr))
    request = conn.recv(1024)
    print('Solicitud = %s' % str(request))
    request = str(request)
  
    if (request.find('/?Validar') == 6):
        print('Validando sensores')
        if pir.value() == 0:
            print('Estado: Enviando Mensaje Plato Vacio')
            send_message(phone_number, api_key, message)
            make_ifttt_request()

        if pir2.value() == 0:
            print('Estado: Enviando Mensaje Dispensador Vacio')
            send_message(phone_number, api_key, message2)
            make_ifttt_request()

    if (request.find('/?Dispensador=on') == 6):
        print('Estado: Servo Encendido')
        motor.move(0)
        time.sleep(0.1)
        motor.move(90)
        time.sleep(0.1)
        motor.move(0)
        time.sleep(0.1)
        motor.move(90)
        time.sleep(0.1)
        motor.move(0)
        time.sleep(0.1)
        motor.move(90)
        time.sleep(3)
        motor.move(180)
        time.sleep(0.1)
        motor.move(90)
        motor.move(180)
        time.sleep(0.1)
        motor.move(90)
        motor.move(180)
        time.sleep(0.1)
        motor.move(90)
        
    if (request.find('/?Dispensador=off') == 6):
        print('Estado: Servo Apagado')

    response = web_page()
    conn.send('HTTP/1.1 200 OK\n')
    conn.send('Content-Type: text/html\n')
    conn.send('Connection: close\n\n')
    conn.sendall(response)
    conn.close()