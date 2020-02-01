
"""
to create exe-file you execute this script with one parameter: build_exe.

example: python3 setup.py build_exe

"""
from cx_Freeze import setup, Executable
import sys

base = None
executables = [Executable("main.py", base=base)]
add_to_path = True

options = {
    'build_exe': {
        'includes': ['selenium', 'selenium.webdriver'],
        'path': sys.path
    }
}

setup(
    name = "AFitness",
    version = "3.1",
    description = 'Fill in web form',
    executables = executables,
    options = options
)
