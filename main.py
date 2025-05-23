from pathlib import Path
from django.core.management.utils import get_random_secret_key

import socket

# This will give you your machine name
machine_name = socket.gethostname()
print(machine_name)  # Add this temporarily to see your hostname


BASE_DIR1 = Path(__file__).resolve().parent.parent
BASE_DIR2 = Path(__file__).resolve().parent
BASE_DIR3 = Path(__file__).resolve()

# print(get_random_secret_key())

# print(BASE_DIR1)
# print(BASE_DIR2)
# print(BASE_DIR3)
