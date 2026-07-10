from services.arduino import ArduinoService

arduino = ArduinoService("COM4")

print("Conectado ao Arduino!")

while True:

    dado = arduino.ler()

    if dado is not None:

        print(dado)