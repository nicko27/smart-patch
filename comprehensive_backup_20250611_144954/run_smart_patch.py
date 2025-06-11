#!/usr/bin/env python3
"""Script de lancement simplifié pour Smart Patch Processor"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire courant au Python path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from main import main
    main()
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Erreur: {e}")
    sys.exit(1)
