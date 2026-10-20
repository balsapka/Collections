"""BUNDLE-ONLY (not shipped): lets the shipped tests under tests/nodes/ and tests/pipelines/
import `enbd_collections.pipelines.crx_persona` exactly as they will in the workplace repo,
by mapping that package name onto ../crx_persona (the staged copy).

In the workplace repo the real package is installed, so this file is not copied.
"""
import importlib.util
import pathlib
import sys
import types

_STAGED = pathlib.Path(__file__).resolve().parents[1] / "crx_persona"
_NAME = "enbd_collections.pipelines.crx_persona"

if _NAME not in sys.modules:
    try:
        import enbd_collections  # noqa: F401  — the real package is present: use it
    except ImportError:
        for name in ("enbd_collections", "enbd_collections.pipelines"):
            mod = types.ModuleType(name)
            mod.__path__ = []
            sys.modules[name] = mod
        spec = importlib.util.spec_from_file_location(
            _NAME, _STAGED / "__init__.py", submodule_search_locations=[str(_STAGED)])
        pkg = importlib.util.module_from_spec(spec)
        sys.modules[_NAME] = pkg
        spec.loader.exec_module(pkg)
        sys.modules["enbd_collections.pipelines"].crx_persona = pkg
