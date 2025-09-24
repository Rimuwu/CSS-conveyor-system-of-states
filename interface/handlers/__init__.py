import importlib
from pathlib import Path

current_dir = Path(__file__).parent

for file in current_dir.glob('*.py'):
    if file.name != '__init__.py':
        module_name = file.stem
        importlib.import_module(f'.{module_name}', package=__name__)