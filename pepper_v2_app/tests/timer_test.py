import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.utils.timing import timer
import numpy 

def calculation(maxx):
    for itemer in range(1, maxx):
        print(numpy.sqrt(itemer))
        
timer(calculation, 10000)