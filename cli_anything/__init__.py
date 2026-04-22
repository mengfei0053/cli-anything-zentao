# PEP 420 namespace package — do NOT add __init__.py here.
# This file exists only to prevent IDE import errors.
# In production, this directory has no __init__.py.
__path__ = __import__('pkgutil').extend_path(__path__, __name__)
