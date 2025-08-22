import os
import sys

# Ajouter le répertoire courant au PYTHONPATH pour permettre les imports relatifs
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
