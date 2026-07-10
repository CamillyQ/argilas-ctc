from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QSizePolicy
from PySide6.QtGui import QFont

HEX_SURFACE      = "#FFFFFF"
HEX_SURFACE_PRES = "#EBEEF2"
HEX_BORDER       = "#D1D1CD"
HEX_TEXT         = "#212121"
HEX_ACTION       = "#2E5284"
HEX_ACTION_PRES  = "#1F375B"

class SCADAButton(QPushButton):
    """
    Componente de toque industrial. 
    - Tamanho mínimo de 64px de altura garante conformidade com a ISO 9241-9 para telas de 7".
    - Feedback tátil-visual imediato via QSS.
    - Suporta estados 'Primary' (Ação única) e 'Secondary' (Neutro).
    """
    def __init__(self, text, is_primary=False, parent=None):
        super().__init__(text, parent)
        self.is_primary = is_primary
        
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(64)  
        
        self.setFont(QFont("Sans-Serif", 11, QFont.Bold))
        
        self.setProperty("is_primary", str(is_primary).lower())


class StatusPill(QWidget):
    """
    Indicador de Estado Crítico do Sistema (Overview Nível 1 - ISA-101).
    Garante redundância para daltonismo associando um caractere geométrico (●)
    de cor fixa a um texto explícito em caixa alta.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(8)

        self.led = QLabel("●")
        self.led.setFont(QFont("Sans-Serif", 14, QFont.Bold))
   
        self.label = QLabel("SISTEMA PRONTO")
        self.label.setFont(QFont("Courier New", 10, QFont.Bold))
        
        layout.addWidget(self.led)
        layout.addWidget(self.label)
        layout.addStretch() 
        
        self.set_status("SISTEMA PRONTO", "#6B6B6B")

    def set_status(self, text, color_hex):
        """
        Método público para alterar o estado do sistema dinamicamente em tempo de execução.
        """
        self.label.setText(text.upper())
        self.label.setStyleSheet(f"color: {HEX_TEXT};")
        self.led.setStyleSheet(f"color: {color_hex};")