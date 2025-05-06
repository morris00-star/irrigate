from pathlib import Path
from django.core.management.utils import get_random_secret_key


BASE_DIR1 = Path(__file__).resolve().parent.parent
BASE_DIR2 = Path(__file__).resolve().parent
BASE_DIR3 = Path(__file__).resolve()

print(get_random_secret_key())

# print(BASE_DIR1)
# print(BASE_DIR2)
# print(BASE_DIR3)
