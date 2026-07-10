import serial
import time
import re
from serial.tools import list_ports

from serial.tools import list_ports

def detectar_arduino():

    for porta in list_ports.comports():

        descricao = porta.description.lower()
        fabricante = (porta.manufacturer or "").lower()

        print(porta.device, "-", descricao)

        if "arduino" in descricao:
            return porta.device

        if "ch340" in descricao:
            return porta.device

        if "usb serial" in descricao:
            return porta.device

        if "arduino" in fabricante:
            return porta.device

    return None

print("Porta detectada:", detectar_arduino())

class ArduinoService:

    def __init__(self, porta=None, baudrate=9600):

        if porta is None:
            porta = detectar_arduino()

        if porta is None:
            raise RuntimeError("Nenhum Arduino encontrado.")

        self.conexao = serial.Serial(
            port=porta,
            baudrate=baudrate,
            timeout=0.1
        )

        time.sleep(2)

        print(f"Arduino conectado em {porta}")

        self.regex = re.compile(r"([0-9.]+)\s*(ppm|uS/cm)")

        self.ppm = None
        self.condutividade = None

        self.tem_ppm = False
        self.tem_condutividade = False


    def enviar(self, comando):

        comando = comando.strip() + "\n"

        self.conexao.write(
            comando.encode("utf-8")
        )

    ######################################################

    def ler(self):

        while self.conexao.in_waiting:

            linha = (
                self.conexao
                .readline()
                .decode("utf-8", errors="ignore")
                .strip()
            )

            if linha == "":
                continue

            match = self.regex.search(linha)

            if match is None:
                continue

            valor = float(match.group(1))
            unidade = match.group(2)

            ##############################################

            if unidade == "ppm":

                self.ppm = valor
                self.tem_ppm = True

            ##############################################

            elif unidade == "uS/cm":

                self.condutividade = valor
                self.tem_condutividade = True

            ##############################################

            # Só devolve quando possui os DOIS valores

            if self.tem_ppm and self.tem_condutividade:

                leitura = (
                    self.ppm,
                    self.condutividade
                )

                self.tem_ppm = False
                self.tem_condutividade = False

                return leitura

        return None

    ######################################################

    def limpar_buffer(self):

        self.conexao.reset_input_buffer()

    ######################################################

    def fechar(self):

        if self.conexao.is_open:
            self.conexao.close()