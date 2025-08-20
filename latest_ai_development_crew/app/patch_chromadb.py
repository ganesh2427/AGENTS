# app/patch_chromadb.py
import sys
import types

# Create a fake chromadb module
fake_chromadb = types.ModuleType("chromadb")
fake_chromadb.Client = lambda *args, **kwargs: None
fake_chromadb.__version__ = "0.0.0"

# Also fake submodules that crewai tries to import
fake_chromadb.errors = types.SimpleNamespace()
fake_chromadb.api = types.SimpleNamespace()
fake_chromadb.api.ClientAPI = object
fake_chromadb.api.types = types.SimpleNamespace(OneOrMany=object)

sys.modules["chromadb"] = fake_chromadb
sys.modules["chromadb.errors"] = fake_chromadb.errors
sys.modules["chromadb.api"] = fake_chromadb.api
sys.modules["chromadb.api.types"] = fake_chromadb.api.types
