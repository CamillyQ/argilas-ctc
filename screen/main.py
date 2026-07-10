#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from datetime import datetime
from time import perf_counter

from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget

from services.arduino import ArduinoService
from services.analises import (
    calcular_concentracao_molar,
    detectar_cmc_joao,
    cmc_para_ctc,
    classificar_tipo_argila,
    calcular_interseccao_cmc,
    concentracao_para_volume
)
from interface.home import HomeScreen
from interface.medicao import MedicaoScreen


def configurar_ambiente_rpi():
    os.environ["QT_QPA_EGLFS_HIDECURSOR"] = "1"
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"


class ScadaApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SCADA - Estação de Medição")
        self.setFixedSize(800, 480)

        # Estado do ensaio em andamento
        self.coletando = False
        self.pontos = []                 # (tempo, condutividade) -- gráfico ao vivo
        self.titulacao = []              # [{'volume_acumulado_mL', 'concentracao_molar', 'condutividade'}]
        self.volume_acumulado_mL = 0.0
        self.massa_amostra_g = None      # definida pelo usuário no Estado Inicial
        self.inicio = 0.0

        self.arduino = ArduinoService()

        self.screen_manager = QStackedWidget()
        self.setCentralWidget(self.screen_manager)

        self.medicao_screen = MedicaoScreen(app_instance=self)
        self.home_screen = HomeScreen(app_instance=self)

        self.screen_manager.addWidget(self.home_screen)
        self.screen_manager.addWidget(self.medicao_screen)

        self.setup_timers()

    def setup_timers(self):
        self.timer_tick = QTimer(self)
        self.timer_tick.timeout.connect(self._tick)
        self.timer_tick.start(1000)

        self.timer_serial = QTimer(self)
        self.timer_serial.timeout.connect(self.receber_dados)
        self.timer_serial.start(50)

        self._tick()

    @Slot()
    def _tick(self):
        data_hora_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.home_screen.clock_lbl.setText(data_hora_str)

    @Slot()
    def receber_dados(self):
        """Coleta contínua para o gráfico ao vivo -- só roda no Estado Coleta."""
        if not self.coletando:
            return

        leitura = self.arduino.ler()
        if leitura is None:
            return

        ppm, condutividade = leitura
        tempo = perf_counter() - self.inicio

        self.pontos.append((tempo, condutividade))
        total_amostras = len(self.pontos)

    
        self.medicao_screen.lbl_condutividade.setText(f"{condutividade:.2f} µS/cm")
        self.medicao_screen.lbl_leituras_recebidas.setText(str(total_amostras))
        self.medicao_screen.add_point(tempo, condutividade)

    # ── Titulação manual (botão "Registrar Adição", só existe no Estado Coleta) ─
    @Slot(float)
    def registrar_adicao(self, volume_mL):
        if volume_mL <= 0 or not self.coletando:
            return

        self.volume_acumulado_mL += volume_mL
        concentracao_molar = calcular_concentracao_molar(self.volume_acumulado_mL)
        condutividade_atual = self.pontos[-1][1] if self.pontos else 0.0

        self.titulacao.append({
            "volume_acumulado_mL": self.volume_acumulado_mL,
            "concentracao_molar": concentracao_molar,
            "condutividade": condutividade_atual,
        })

        self.medicao_screen.atualizar_volume_total(self.volume_acumulado_mL)
        print(
            f"[TITULAÇÃO] Volume total: {self.volume_acumulado_mL:.2f} mL | "
            f"Concentração: {concentracao_molar:.6f} mol/L | "
            f"Condutividade: {condutividade_atual:.2f} µS/cm"
        )

    # ── Processamento (botão "Processar", só habilitado no Estado Finalizado) ──
    @Slot()
    def detectar_cmc(self):
            if self.massa_amostra_g is None:
                print("[PROCESSAMENTO] Massa da amostra não definida.")
                return

            try:
                # 1. Busca o "joelho" da curva
                resultado_joelho = detectar_cmc_joao(self.titulacao)
                
                # 2. Refina calculando a intersecção exata (o valor científico da CMC)
                interseccao = calcular_interseccao_cmc(
                    resultado_joelho['concentracoes'], 
                    resultado_joelho['omegas'], 
                    resultado_joelho['indice_joelho']
                )
                
                # 3. Converte a concentração da intersecção de volta para o volume exato
                volume_exato = concentracao_para_volume(interseccao['x_cmc'])
                
                # 4. Calcula a CTC final usando o volume refinado pela intersecção
                ctc_final = cmc_para_ctc(
                    volume_no_corte_mL=volume_exato, 
                    massa_amostra_g=self.massa_amostra_g, 
                    normalidade_titulante=0.01
                )
                
                # 5. Classificação
                tipo_argila = classificar_tipo_argila(ctc_final)

                # 6. Atualização da Interface
                # Passamos a interseccao para o plot, assim ele desenha a CMC matemática
                self.medicao_screen.plotar_ajuste_cmc_joao(resultado_joelho, interseccao)
                self.medicao_screen.atualizar_resultado(interseccao['x_cmc'], ctc_final, tipo_argila)

            except Exception as erro:
                print(f"[PROCESSAMENTO] Erro ao processar CMC/CTC: {erro}")
                return

    # ── Transições de estado ────────────────────────────────────────────
    @Slot(float)
    def iniciar_teste(self, massa_amostra_g):
        """Estado Inicial -> Estado Coleta."""
        self.massa_amostra_g = massa_amostra_g
        self.coletando = True
        self.pontos = []
        self.titulacao = []
        self.volume_acumulado_mL = 0.0
        self.inicio = perf_counter()

        self.arduino.limpar_buffer()
        self.arduino.enviar("START")

        self.home_screen.status_pill.set_status("COLETANDO", "#B78103")
        self.medicao_screen.reiniciar_graficos()
        self.medicao_screen.mostrar_estado_coleta()

    @Slot()
    def parar_teste(self):
        """Estado Coleta -> Estado Finalizado."""
        self.coletando = False
        self.arduino.enviar("STOP")
        self.home_screen.status_pill.set_status("PARADO", "#6B6B6B")
        self.medicao_screen.mostrar_estado_finalizado()

    @Slot()
    def novo_ensaio(self):
        """Estado Finalizado -> Estado Inicial (para uma nova amostra)."""
        self.massa_amostra_g = None
        self.pontos = []
        self.titulacao = []
        self.volume_acumulado_mL = 0.0
        self.medicao_screen.mostrar_estado_inicial()

    # ── Navegação do Sistema SCADA ───────────────────────────────────────
    @Slot()
    def acao_iniciar_medicao(self):
        self.screen_manager.setCurrentWidget(self.medicao_screen)
        self.medicao_screen.mostrar_estado_inicial()

    @Slot()
    def acao_historico(self):
        print("[NAVEGAÇÃO] Mudando para tela de Histórico")

    @Slot()
    def acao_configuracoes(self):
        print("[NAVEGAÇÃO] Mudando para tela de Configurações")

    @Slot()
    def voltar_home(self):
        self.screen_manager.setCurrentWidget(self.home_screen)

    @Slot()
    def calibrar_condutivimetro(self):
        print("[CALIBRAÇÃO] Executando rotina de ajuste do sensor.")

    def closeEvent(self, event):
        if hasattr(self, "arduino") and self.arduino:
            print("[SHUTDOWN] Fechando conexão serial de forma segura...")
            self.arduino.fechar()
        event.accept()


if __name__ == "__main__":
    configurar_ambiente_rpi()
    app = QApplication(sys.argv)
    scada_sistema = ScadaApp()
    scada_sistema.show()
    sys.exit(app.exec())