#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QSizePolicy, QStackedWidget, QDoubleSpinBox
)
from PySide6.QtGui import QFont, QPainter, QPen, QColor
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis, QScatterSeries

HEX_BG           = "#F5F5F3"
HEX_SURFACE      = "#FFFFFF"
HEX_BORDER       = "#D1D1CD"
HEX_TEXT         = "#212121"
HEX_TEXT_MUTED   = "#6B6B6B"
HEX_ACTION       = "#2E5284"
HEX_ALARM        = "#C62828"
HEX_OK           = "#2E7D32"
HEX_SURFACE_PRES = "#2E5284"

class MedicaoScreen(QWidget):

    # Estados da tela
    ESTADO_INICIAL     = 0
    ESTADO_COLETA      = 1
    ESTADO_FINALIZADO  = 2

    def __init__(self, app_instance, parent=None):
        super().__init__(parent)
        self.app_app = app_instance
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Cabeçalho ────────────────────────────────────────────────────
        header_frame = QFrame()
        header_frame.setFixedHeight(48)
        header_frame.setStyleSheet("background-color: #202225; border: none;")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(16, 0, 16, 0)

        title_lbl = QLabel("MEDIÇÃO DE CTC")
        title_lbl.setFont(QFont("Sans-Serif", 11, QFont.Bold))
        title_lbl.setStyleSheet("color: #FFFFFF;")

        self.status_arduino = QLabel("ARDUINO CONECTADO")
        self.status_arduino.setFont(QFont("Courier New", 10, QFont.Bold))
        self.status_arduino.setStyleSheet(f"color: {HEX_OK};")
        self.status_arduino.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        header_layout.addWidget(title_lbl)
        header_layout.addWidget(self.status_arduino)
        main_layout.addWidget(header_frame)

        # ── Corpo: um QStackedWidget com as 3 telas de estado ───────────
        self.stack_estados = QStackedWidget()
        self.stack_estados.addWidget(self._build_pagina_inicial())      # 0
        self.stack_estados.addWidget(self._build_pagina_coleta())       # 1
        self.stack_estados.addWidget(self._build_pagina_finalizado())   # 2
        main_layout.addWidget(self.stack_estados, stretch=1)

        # ── Rodapé: botões que existem em qualquer estado ───────────────
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(12, 0, 12, 12)
        footer_layout.setSpacing(8)

        self.btn_parar = QPushButton("Parar")
        self.btn_processar = QPushButton("Processar")
        self.btn_salvar = QPushButton("Salvar")
        self.btn_voltar = QPushButton("Voltar")

        for btn in (self.btn_parar, self.btn_processar, self.btn_salvar, self.btn_voltar):
            btn.setFixedHeight(54)
            btn.setFont(QFont("Sans-Serif", 10, QFont.Bold))
            btn.setStyleSheet(self.get_button_style())
            footer_layout.addWidget(btn)

        self.btn_parar.clicked.connect(self.app_app.parar_teste)
        self.btn_processar.clicked.connect(self.app_app.detectar_cmc)
        self.btn_voltar.clicked.connect(self.app_app.voltar_home)

        main_layout.addLayout(footer_layout)
        self.setStyleSheet(f"background-color: {HEX_BG};")

        self.mostrar_estado_inicial()

    # ════════════════════════════════════════════════════════════════════
    # ESTADO 0 - INICIAL: pede a massa da amostra e inicia a coleta
    # ════════════════════════════════════════════════════════════════════
    def _build_pagina_inicial(self):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(16)

        titulo = QLabel("Nova Medição de CTC")
        titulo.setFont(QFont("Sans-Serif", 16, QFont.Bold))
        titulo.setStyleSheet(f"color: {HEX_TEXT};")
        titulo.setAlignment(Qt.AlignCenter)

        subtitulo = QLabel("Informe a massa seca da amostra de argila antes de iniciar")
        subtitulo.setFont(QFont("Sans-Serif", 10))
        subtitulo.setStyleSheet(f"color: {HEX_TEXT_MUTED};")
        subtitulo.setAlignment(Qt.AlignCenter)

        rotulo_massa = QLabel("MASSA DA AMOSTRA (g)")
        rotulo_massa.setFont(QFont("Sans-Serif", 9, QFont.Bold))
        rotulo_massa.setStyleSheet(f"color: {HEX_TEXT_MUTED};")
        rotulo_massa.setAlignment(Qt.AlignCenter)

        self.spin_massa_amostra = QDoubleSpinBox()
        self.spin_massa_amostra.setDecimals(1)
        self.spin_massa_amostra.setRange(0, 100)
        self.spin_massa_amostra.setSingleStep(1.0)
        self.spin_massa_amostra.setSuffix(" g")
        self.spin_massa_amostra.setFixedWidth(220)
        self.spin_massa_amostra.setStyleSheet(
            f"background-color: {HEX_SURFACE}; border: 1px solid {HEX_BORDER}; "
            "border-radius: 4px; padding: 8px; font-size: 20px;"
        )
        self.spin_massa_amostra.setAlignment(Qt.AlignCenter)

        btn_iniciar_coleta = QPushButton("Iniciar Coleta")
        btn_iniciar_coleta.setFixedSize(220, 56)
        btn_iniciar_coleta.setFont(QFont("Sans-Serif", 11, QFont.Bold))
        btn_iniciar_coleta.setStyleSheet(self.get_button_style(is_action=True))
        btn_iniciar_coleta.clicked.connect(self._on_iniciar_coleta_clicado)

        layout.addWidget(titulo)
        layout.addWidget(subtitulo)
        layout.addSpacing(20)
        layout.addWidget(rotulo_massa, alignment=Qt.AlignCenter)
        layout.addWidget(self.spin_massa_amostra, alignment=Qt.AlignCenter)
        layout.addSpacing(20)
        layout.addWidget(btn_iniciar_coleta, alignment=Qt.AlignCenter)
        return pagina

    def _on_iniciar_coleta_clicado(self):
        massa_amostra_g = self.spin_massa_amostra.value()
        self.app_app.iniciar_teste(massa_amostra_g)

    # ════════════════════════════════════════════════════════════════════
    # ESTADO 1 - COLETA: gráfico ao vivo + titulação manual
    # ════════════════════════════════════════════════════════════════════
    def _build_pagina_coleta(self):
        pagina = QWidget()
        body_layout = QHBoxLayout(pagina)
        body_layout.setContentsMargins(12, 12, 12, 12)
        body_layout.setSpacing(12)

        # Painel esquerdo: cards + controle de titulação
        left_panel = QVBoxLayout()
        left_panel.setSpacing(8)

        self.card_cond = self.create_numeric_card("CONDUTIVIDADE", "0.00 µS/cm", "26px")
        self.card_leituras = self.create_numeric_card("LEITURAS RECEBIDAS", "0", "22px")
        self.card_volume = self.create_numeric_card("VOLUME TOTAL ADICIONADO", "0.00 mL", "22px")

        left_panel.addWidget(self.card_cond)
        left_panel.addWidget(self.card_leituras)
        left_panel.addWidget(self.card_volume)

        titulacao_frame = QFrame()
        titulacao_frame.setStyleSheet(
            f"background-color: {HEX_SURFACE}; border: 1px solid {HEX_BORDER}; border-radius: 4px;"
        )
        titulacao_layout = QVBoxLayout(titulacao_frame)
        titulacao_layout.setContentsMargins(8, 6, 8, 6)
        titulacao_layout.setSpacing(4)

        titulacao_titulo = QLabel("VOLUME DESTA ADIÇÃO (mL)")
        titulacao_titulo.setFont(QFont("Sans-Serif", 8, QFont.Bold))
        titulacao_titulo.setStyleSheet(f"color: {HEX_TEXT_MUTED}; border: none;")

        self.spin_volume_adicao = QDoubleSpinBox()
        self.spin_volume_adicao.setDecimals(2)
        self.spin_volume_adicao.setRange(0.01, 100.0)
        self.spin_volume_adicao.setValue(2.00)
        self.spin_volume_adicao.setSingleStep(0.5)
        self.spin_volume_adicao.setStyleSheet(
            f"background-color: {HEX_BG}; border: 1px solid {HEX_BORDER}; "
            "border-radius: 4px; padding: 4px; font-size: 16px;"
        )

        btn_registrar_adicao = QPushButton("Registrar Adição")
        btn_registrar_adicao.setFixedHeight(44)
        btn_registrar_adicao.setFont(QFont("Sans-Serif", 9, QFont.Bold))
        btn_registrar_adicao.setStyleSheet(self.get_button_style(is_action=True))
        btn_registrar_adicao.clicked.connect(self._on_registrar_adicao)

        titulacao_layout.addWidget(titulacao_titulo)
        titulacao_layout.addWidget(self.spin_volume_adicao)
        titulacao_layout.addWidget(btn_registrar_adicao)

        left_panel.addWidget(titulacao_frame)
        left_panel.addStretch(1)

        # Painel direito: gráfico ao vivo Condutividade x Tempo
        chart_frame = QFrame()
        chart_frame.setStyleSheet(
            f"background-color: {HEX_SURFACE}; border: 1px solid {HEX_BORDER}; border-radius: 4px;"
        )
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.setContentsMargins(4, 4, 4, 4)

        self.series = QLineSeries()
        self.chart_tempo = QChart()
        self.chart_tempo.addSeries(self.series)
        self.chart_tempo.legend().hide()
        self.chart_tempo.setTitle("Gráfico Condutividade × Tempo")
        self.chart_tempo.setTitleFont(QFont("Sans-Serif", 10, QFont.Bold))
        self.chart_tempo.setBackgroundVisible(False)

        self.axis_x = QValueAxis()
        self.axis_x.setTitleText("Tempo (s)")
        self.axis_x.setLabelFormat("%.1f")
        self.chart_tempo.addAxis(self.axis_x, Qt.AlignBottom)
        self.series.attachAxis(self.axis_x)

        self.axis_y = QValueAxis()
        self.axis_y.setTitleText("Condutividade (µS/cm)")
        self.axis_y.setLabelFormat("%.2f")
        self.chart_tempo.addAxis(self.axis_y, Qt.AlignLeft)
        self.series.attachAxis(self.axis_y)

        chart_view_tempo = QChartView(self.chart_tempo)
        chart_view_tempo.setRenderHint(QPainter.Antialiasing)
        chart_layout.addWidget(chart_view_tempo)

        body_layout.addLayout(left_panel, stretch=35)
        body_layout.addWidget(chart_frame, stretch=65)
        return pagina

    def _on_registrar_adicao(self):
        volume_mL = self.spin_volume_adicao.value()
        self.app_app.registrar_adicao(volume_mL)

    # ════════════════════════════════════════════════════════════════════
    # ESTADO 2 - FINALIZADO: amostra coletada, pronta pra processar/resultado
    # ════════════════════════════════════════════════════════════════════
    def _build_pagina_finalizado(self):
        pagina = QWidget()
        body_layout = QHBoxLayout(pagina)
        body_layout.setContentsMargins(12, 12, 12, 12)
        body_layout.setSpacing(12)

        left_panel = QVBoxLayout()
        left_panel.setSpacing(10)

        self.card_cmc = self.create_numeric_card("CMC", "-- (aperte Processar)", "16px")
        self.card_ctc = self.create_numeric_card("CTC", "-- mEq/100g", "24px")
        self.card_tipo = self.create_numeric_card("TIPO DE ARGILA", "serviço do modelo!", "18px")

        left_panel.addWidget(self.card_cmc)
        left_panel.addWidget(self.card_ctc)
        left_panel.addWidget(self.card_tipo)

        btn_novo_ensaio = QPushButton("Nova Amostra")
        btn_novo_ensaio.setFixedHeight(48)
        btn_novo_ensaio.setFont(QFont("Sans-Serif", 9, QFont.Bold))
        btn_novo_ensaio.setStyleSheet(self.get_button_style())
        btn_novo_ensaio.clicked.connect(self.app_app.novo_ensaio)
        left_panel.addWidget(btn_novo_ensaio)
        left_panel.addStretch(1)

        chart_frame = QFrame()
        chart_frame.setStyleSheet(
            f"background-color: {HEX_SURFACE}; border: 1px solid {HEX_BORDER}; border-radius: 4px;"
        )
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.setContentsMargins(4, 4, 4, 4)

        self.series_titulacao_todos = QScatterSeries()
        self.series_titulacao_todos.setName("Dados")
        self.series_titulacao_todos.setMarkerSize(10)
        self.series_titulacao_todos.setColor(QColor(HEX_ACTION))

        self.series_titulacao_linear = QScatterSeries()
        self.series_titulacao_linear.setName("Trecho Linear")
        self.series_titulacao_linear.setMarkerSize(10)
        self.series_titulacao_linear.setColor(QColor(HEX_OK))

        self.series_ajuste_rls = QLineSeries()
        self.series_ajuste_rls.setName("Ajuste RLS")
        pen = QPen(QColor(HEX_ALARM))
        pen.setStyle(Qt.DashLine)
        pen.setWidth(2)
        self.series_ajuste_rls.setPen(pen)

        self.chart_molar = QChart()
        self.chart_molar.addSeries(self.series_titulacao_todos)
        self.chart_molar.addSeries(self.series_titulacao_linear)
        self.chart_molar.addSeries(self.series_ajuste_rls)
        self.chart_molar.legend().setVisible(True)
        self.chart_molar.setTitle("CMC: Condutividade Molar × Concentração Molar")
        self.chart_molar.setTitleFont(QFont("Sans-Serif", 10, QFont.Bold))
        self.chart_molar.setBackgroundVisible(False)

        self.axis_molar_x = QValueAxis()
        self.axis_molar_x.setTitleText("Concentração molar (mol/L)")
        self.axis_molar_x.setLabelFormat("%.5f")
        self.axis_molar_x.setRange(0, 1)
        self.chart_molar.addAxis(self.axis_molar_x, Qt.AlignBottom)

        self.axis_molar_y = QValueAxis()
        self.axis_molar_y.setTitleText("Condutividade molar Ω (µS·cm²/mol)")
        self.axis_molar_y.setLabelFormat("%.1f")
        self.axis_molar_y.setRange(0, 1)
        self.chart_molar.addAxis(self.axis_molar_y, Qt.AlignLeft)

        for serie in (self.series_titulacao_todos, self.series_titulacao_linear, self.series_ajuste_rls):
            serie.attachAxis(self.axis_molar_x)
            serie.attachAxis(self.axis_molar_y)

        chart_view_molar = QChartView(self.chart_molar)
        chart_view_molar.setRenderHint(QPainter.Antialiasing)
        chart_layout.addWidget(chart_view_molar)

        body_layout.addLayout(left_panel, stretch=35)
        body_layout.addWidget(chart_frame, stretch=65)
        return pagina

    # ── Controle de Estado (chamado pelo main.py) ───────────────────────
    def mostrar_estado_inicial(self):
        self.stack_estados.setCurrentIndex(self.ESTADO_INICIAL)
        self.btn_parar.setEnabled(False)
        self.btn_processar.setEnabled(False)
        self.btn_salvar.setEnabled(False)

    def mostrar_estado_coleta(self):
        self.stack_estados.setCurrentIndex(self.ESTADO_COLETA)
        self.btn_parar.setEnabled(True)
        self.btn_processar.setEnabled(False)
        self.btn_salvar.setEnabled(False)

    def mostrar_estado_finalizado(self):
        self.stack_estados.setCurrentIndex(self.ESTADO_FINALIZADO)
        self.btn_parar.setEnabled(False)
        self.btn_processar.setEnabled(True)
        self.btn_salvar.setEnabled(True)

    # ── Auxiliar para Criação Dinâmica dos Cards Numéricos ──────────────
    def create_numeric_card(self, title, initial_value, font_size):
        frame = QFrame()
        frame.setStyleSheet(
            f"background-color: {HEX_SURFACE}; border: 1px solid {HEX_BORDER}; border-radius: 4px;"
        )
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(2)

        title_lbl = QLabel(title)
        title_lbl.setFont(QFont("Sans-Serif", 9, QFont.Bold))
        title_lbl.setStyleSheet(f"color: {HEX_TEXT_MUTED}; border: none;")

        val_lbl = QLabel(initial_value)
        val_lbl.setFont(QFont("Courier New", int(font_size.replace("px", "")), QFont.Bold))
        val_lbl.setStyleSheet(f"color: {HEX_TEXT}; border: none;")
        val_lbl.setAlignment(Qt.AlignCenter)
        val_lbl.setWordWrap(True)

        layout.addWidget(title_lbl)
        layout.addWidget(val_lbl)

        setattr(self, f"lbl_{title.lower().replace(' ', '_').replace('çã', 'ca')}", val_lbl)
        return frame

    # ── Interface Pública chamada pelo main.py ──────────────────────────
    @Slot(float, float)
    def add_point(self, tempo, condutividade):
        self.series.append(tempo, condutividade)
        if self.series.count() == 1:
            self.axis_x.setRange(0, max(tempo, 1))
            self.axis_y.setRange(0, condutividade + 10)
        else:
            if tempo > self.axis_x.max():
                self.axis_x.setMax(tempo * 1.1)
            if condutividade > self.axis_y.max():
                self.axis_y.setMax(condutividade * 1.1)

    def reiniciar_graficos(self):
        """Limpa os dois gráficos -- chamado ao iniciar um novo ensaio."""
        self.series.clear()
        self.axis_x.setRange(0, 10)
        self.axis_y.setRange(0, 10)

        self.series_titulacao_todos.clear()
        self.series_titulacao_linear.clear()
        self.series_ajuste_rls.clear()

        self.lbl_volume_total_adicionado.setText("0.00 mL")
        self.lbl_leituras_recebidas.setText("0")
        self.lbl_cmc.setText("-- (aperte Processar)")
        self.lbl_ctc.setText("-- mEq/100g")
        self.lbl_tipo_de_argila.setText("--")

    def atualizar_volume_total(self, volume_mL):
        self.lbl_volume_total_adicionado.setText(f"{volume_mL:.2f} mL")

    def plotar_ajuste_cmc_joao(self, resultado_joelho, interseccao):
        """
        Atualiza o gráfico mostrando as duas retas (pré e pós joelho)
        e o ponto de intersecção que define a CMC.
        """
        concentracoes = resultado_joelho["concentracoes"]
        omegas = resultado_joelho["omegas"]
        indice_joelho = resultado_joelho["indice_joelho"]
        
        # Limpa séries antigas
        self.series_titulacao_todos.clear()
        self.series_titulacao_linear.clear()
        self.series_ajuste_rls.clear()

        # 1. Plotar todos os pontos originais
        for c, o in zip(concentracoes, omegas):
            self.series_titulacao_todos.append(float(c), float(o))

        # 2. Desenhar Reta 1 (Pré-micelização)
        a1, b1 = interseccao["reta_pre"]
        c_pre_ini = float(concentracoes[0])
        c_pre_fim = float(concentracoes[indice_joelho - 1])
        # Criamos uma série temporária ou apenas usamos a RLS para a reta 1
        # Para simplificar, vou usar a series_ajuste_rls como a Reta 1 e 
        # sugerir adicionar uma segunda série de linha se desejar.
        # Aqui, desenharemos as retas de intersecção:
        
        # Reta Pré
        self.series_ajuste_rls.append(c_pre_ini, a1 * c_pre_ini + b1)
        self.series_ajuste_rls.append(c_pre_fim, a1 * c_pre_fim + b1)

        # 3. Desenhar Reta 2 (Pós-micelização)
        a2, b2 = interseccao["reta_pos"]
        c_pos_ini = float(concentracoes[indice_joelho])
        c_pos_fim = float(concentracoes[-1])
        
        # Como o QLineSeries conecta os pontos, adicionaremos um ponto "quebra"
        # para que a série não trace uma linha entre o fim da reta 1 e início da reta 2
        self.series_ajuste_rls.append(c_pos_ini, a2 * c_pos_ini + b2)
        self.series_ajuste_rls.append(c_pos_fim, a2 * c_pos_fim + b2)

        # Ajuste de eixos
        self.axis_molar_x.setRange(0, float(concentracoes.max()) * 1.1)
        self.axis_molar_y.setRange(0, float(omegas.max()) * 1.1)

    def atualizar_resultado(self, cmc, ctc, tipo_argila):
        self.lbl_cmc.setText(f"{cmc:.6f} mol/L")
        self.lbl_ctc.setText(f"{ctc:.2f} mEq/100g")
        self.lbl_tipo_de_argila.setText(tipo_argila)

    def get_button_style(self, is_action=False):
        if is_action:
            return f"""
                QPushButton {{ background-color: {HEX_ACTION}; color: white; border: 1px solid #1F375B; border-radius: 4px; }}
                QPushButton:pressed {{ background-color: #1F375B; }}
                QPushButton:disabled {{ background-color: #9AA7B5; border: 1px solid #8A97A5; }}
            """
        return f"""
            QPushButton {{ background-color: {HEX_SURFACE}; color: {HEX_TEXT}; border: 1px solid {HEX_BORDER}; border-radius: 4px; }}
            QPushButton:pressed {{ background-color: {HEX_SURFACE_PRES}; }}
            QPushButton:disabled {{ color: #B0B0B0; background-color: #EDEDEB; }}
        """