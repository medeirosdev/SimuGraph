from __future__ import annotations
import os
import sys
import importlib.util
import inspect
from simugraph.algorithms.base import StepAlgorithm

def load_plugins() -> list[type[StepAlgorithm]]:
    """
    Dynamically loads all plugins in the plugins/ directory.
    Scans for any classes that inherit from StepAlgorithm.
    """
    # Look for 'plugins' directory in the workspace root
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    plugins_dir = os.path.join(base_dir, "plugins")
    if not os.path.exists(plugins_dir):
        return []

    # Insert plugins directory into sys.path
    if plugins_dir not in sys.path:
        sys.path.insert(0, plugins_dir)

    discovered_algorithms = []

    for filename in os.listdir(plugins_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]
            module_path = os.path.join(plugins_dir, filename)
            
            try:
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                if spec is None or spec.loader is None:
                    continue
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
                
                # Check classes in the module
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    # Ensure it is subclass of StepAlgorithm and defined in this module
                    if issubclass(obj, StepAlgorithm) and obj is not StepAlgorithm:
                        if obj.__module__ == module_name:
                            discovered_algorithms.append(obj)
            except Exception as e:
                print(f"Failed to load plugin {filename}: {e}")

    return discovered_algorithms
