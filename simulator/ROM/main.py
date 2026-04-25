"""
Filename: main.py

Description:
    Loads parameters and uts and than initializes and manages 
    the "coilgun" class and routes simulation results to matplotlib 
    for plotting.
"""

from pathlib import Path
from picounits.extensions.parser import Parser

from modules.model import CoilGun

BASE_DIR = Path(__file__).parent
parameter = Parser.open(BASE_DIR / "parameters.uiv", BASE_DIR / "units.ut")

coilgun = CoilGun(parameter)