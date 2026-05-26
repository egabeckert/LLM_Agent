import sys
from pylint import run_pylint

def run_lint():
    # Defaults to current directory, or you can parse sys.argv
    sys.argv[1:] = ["src"] 
    run_pylint()   
