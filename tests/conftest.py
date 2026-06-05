import sys
import os

# Adiciona etl/ ao path para que "from logger import get_logger" funcione
# dentro de transform.py quando importado nos testes
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "etl"))
