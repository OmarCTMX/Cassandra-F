# este archivo solo re-exporta get_db desde connect.py
# lo dejo aqui para que client.py pueda importarlo sin problemas
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from connect import get_db  # noqa: F401
