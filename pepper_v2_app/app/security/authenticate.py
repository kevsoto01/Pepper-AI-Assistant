from getpass import getpass
import hashlib
import sys

from .details import EXPECTED_HASH

def verify():
    entered = getpass("\n\nEnter access password: ") # example: yercocet
    digest = hashlib.sha256(entered.encode()).hexdigest() 
    if digest != EXPECTED_HASH:
        print("Access denied")
        sys.exit(1)
