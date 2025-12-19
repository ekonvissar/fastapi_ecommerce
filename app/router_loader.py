from pathlib import Path
from pkgutil import iter_modules
import importlib

def include_routers(app):
    package_dir = Path(__file__).resolve().parent / "routers"
    for _, module_name, _ in iter_modules([str(package_dir)]):
        module = importlib.import_module(f"app.routers.{module_name}")
        if hasattr(module, "router"):
            app.include_router(module.router)
