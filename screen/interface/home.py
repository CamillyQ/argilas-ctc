import sys
from PySide6.QtCore import Qt, QTime, QTimer, Slot
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QPushButton, QLabel, QFrame, QSizePolicy
)
from PySide6.QtGui import QFont, QPalette, QColor

# ════════════════════════════════════════════════════════════════════════════
# DIRETRIZES DE DESIGN & PALETA ISA-101 (Convertido para Hex/QSS)
# ════════════════════════════════════════════════════════════════════════════
HEX_BG           = "#F5F5F3"  # Fundo neutro dominante (~90%)
HEX_SURFACE      = "#FFFFFF"  # Cards e botões secundários
HEX_SURFACE_PRES = "#EBEEF2"  # Feedback de toque sutil
HEX_BORDER       = "#D1D1CD"  # Linhas técnicas finas

HEX_TEXT         = "#212121"  # Leitura principal
HEX_TEXT_MUTED   = "#6B6B6B"  # Dados de apoio

HEX_ACTION       = "#2E5284"  # Única ação primária
HEX_ACTION_PRES  = "#1F375B"

# Estados Fixos do Sistema
HEX_NORMAL       = "#6B6B6B"
HEX_OK           = "#2E7D32"
HEX_WARN         = "#B78103"
HEX_ALARM        = "#C62828"


class SCADAButton(QPushButton):
    """
    Botão industrial robusto otimizado para telas touchscreen de 7 polegadas.
    Design retilíneo técnico e alto contraste.
    """
    def __init__(self, text, is_primary=False, parent=None):
        super().__init__(text, parent)
        self.is_primary = is_primary
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(64)  # Garantindo conformidade ISO 9241-9 para toque
        self.setFont(QFont("Monospace" if is_primary else "Sans-Serif", 11, QFont.Bold))


class StatusPill(QWidget):
    """
    Indicador de estado técnico associando Cor + Texto (Redundância p/ Daltonismo)
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(8)
        
        # Indicador visual geométrico (LED simulado)
        self.led = QLabel("●")
        self.led.setFont(QFont("Sans-Serif", 14, QFont.Bold))
        
        self.label = QLabel("SISTEMA PRONTO")
        self.label.setFont(QFont("Courier New", 10, QFont.Bold))
        
        layout.addWidget(self.led)
        layout.addWidget(self.label)
        layout.addStretch()
        
        self.set_status("NORMAL", HEX_NORMAL)

    def set_status(self, text, color_hex):
        self.label.setText(text.upper())
        self.label.setStyleSheet(f"color: {HEX_TEXT};")
        self.led.setStyleSheet(f"color: {color_hex};")


class HomeScreen(QWidget):
    def __init__(self, app_instance, parent=None):
        super().__init__(parent)
        self.app_app = app_instance
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 12, 16, 12)
        main_layout.setSpacing(14)
        
        # ── TOPO: Barra de Status Técnica ─────────────────────────────────────
        top_layout = QHBoxLayout()
        self.status_pill = StatusPill()
        
        self.clock_lbl = QLabel("--:--:--")
        self.clock_lbl.setFont(QFont("Courier New", 11, QFont.Bold))
        self.clock_lbl.setStyleSheet(f"color: {HEX_TEXT_MUTED};")
        self.clock_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        top_layout.addWidget(self.status_pill)
        top_layout.addWidget(self.clock_lbl)
        main_layout.addLayout(top_layout)
        
        # Divisor Superior
        main_layout.addWidget(self.create_divider())
        
        # ── CORPO: Área Gráfica / Display Central ──────────────────────────────
        # Substitui o "Image" vago por um placeholder técnico estruturado
  
        
        # ── INFERIOR: Painel de Ações Instrumentais ───────────────────────────
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        self.btn_measure = SCADAButton("⚡ INICIAR MEDIÇÃO", is_primary=True)
        self.btn_history = SCADAButton("📊 HISTÓRICO", is_primary=False)
        self.btn_config  = SCADAButton("⚙️ CONFIGURAÇÃO", is_primary=False)
        
        # Conexões de eventos de clique
        self.btn_measure.clicked.connect(self.app_app.acao_iniciar_medicao)
        self.btn_history.clicked.connect(self.app_app.acao_historico)
        self.btn_config.clicked.connect(self.app_app.acao_configuracoes)
        
        button_layout.addWidget(self.btn_measure, stretch=4)
        button_layout.addWidget(self.btn_history, stretch=3)
        button_layout.addWidget(self.btn_config, stretch=3)
        main_layout.addLayout(button_layout)
        
        # Divisor Inferior
        main_layout.addWidget(self.create_divider())
        
        # Rodapé / Instrução Operacional
        footer_lbl = QLabel("AGUARDANDO COMANDO DO OPERADOR")
        footer_lbl.setFont(QFont("Sans-Serif", 9))
        footer_lbl.setStyleSheet(f"color: {HEX_TEXT_MUTED};")
        footer_lbl.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(footer_lbl)

    def create_divider(self):
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Plain)
        divider.setStyleSheet(f"color: {HEX_BORDER}; qproperty-lineWidth: 1;")
        return divider


class SCADAApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SCADA Lab Interface")
        
        # Dimensões fixas para a tela touchscreen de 7" do Raspberry Pi (Tipicamente 800x480)
        self.setFixedSize(800, 480)
        
        # Centralizar Widget Principal
        self.home_screen = HomeScreen(app_instance=self)
        self.setCentralWidget(self.home_screen)
        
        self.setStyleSheet(self.get_stylesheet())
        
        # Timer de Atualização do Relógio Técnico
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)
        self.update_clock()

    def update_clock(self):
        time_str = QTime.currentTime().toString("hh:mm:ss")
        self.home_screen.clock_lbl.setText(time_str)

    # ── Mapeamento de Funções do App Original ───────────────────────────────
    @Slot()
    def acao_iniciar_medicao(self):
        print("[SINAL] Comando de medição enviado ao hardware.")
        self.home_screen.status_pill.set_status("COLETANDO", HEX_WARN)

    @Slot()
    def acao_historico(self):
        print("[NAVEGAÇÃO] Abrindo base de dados local.")

    @Slot()
    def acao_configuracoes(self):
        print("[NAVEGAÇÃO] Acessando parâmetros do sistema.")

    def get_stylesheet(self):
        return f"""
            QMainWindow {{
                background-color: {HEX_BG};
            }}
            
            /* Estilização dos Botões via Folha de Estilo Técnica */
            SCADAButton {{
                border: 1px solid {HEX_BORDER};
                border-radius: 4px;
                color: {HEX_TEXT};
                background-color: {HEX_SURFACE};
            }}
            SCADAButton:pressed {{
                background-color: {HEX_SURFACE_PRES};
            }}
            
            /* Destaque estrito da ação principal (Norma ISA-101) */
            SCADAButton[is_primary="true"] {{
                background-color: {HEX_ACTION};
                color: #FFFFFF;
                border: 1px solid {HEX_ACTION_PRES};
            }}
            SCADAButton[is_primary="true"]:pressed {{
                background-color: {HEX_ACTION_PRES};
            }}
            
            /* Área de visualização de dados */
            QFrame#DisplayArea {{
                background-color: {HEX_SURFACE};
                border: 1px solid {HEX_BORDER};
                border-radius: 4px;
            }}
        """

if __name__ == "__main__":
    # Otimizações de renderização para o hardware do Raspberry Pi 3
    os_flags = ["-platform", "eglfs"] if hasattr(sys, "frozen") else []
    app = QApplication(sys.argv + os_flags)
    
    window = SCADAApplication()
    # Opcional para o RPi operando em modo Kiosk: window.showFullScreen()
    window.show()
    sys.exit(app.exec())