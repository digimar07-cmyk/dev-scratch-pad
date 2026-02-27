import subprocess
import sys
import os

# Executa o arquivo monolítico original até modularização estar completa
original_file = os.path.join(os.path.dirname(__file__), "..", "laserflix_v740_Ofline_Stable.py")

if os.path.exists(original_file):
    subprocess.run([sys.executable, original_file])
else:
    print(f"Arquivo não encontrado: {original_file}")
    print("Execute direto: python ../laserflix_v740_Ofline_Stable.py")
