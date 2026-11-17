"""Import and wiring smoke test of the persona code (refactor gate 5).

    python workplace_mirror/checks/refactor_smoke.py [--io]

1. Every mirrored module under ``src/enbd_collections`` imports. Workplace modules that
   are not mirrored (other domains, DCORE / Way4 helpers) are stubbed and listed; a
   mirrored module that fails to import is a failure.
2. ``pipeline_registry.register_pipelines()`` runs, and every checked pipeline
   (``CHECKED``: all ``crx_*`` plus the mirrored feature pipelines the persona reads)
   builds and is not empty.
3. Every dataset of a checked pipeline exists: ``params:`` keys in
   ``conf/base/parameters`` (``globals`` resolved from ``conf/dev/globals_dev.yml``);
   ``crx_*`` free inputs in ``catalog_crx.yml``; outputs of the product and bureau
   pipelines in ``conf/base/catalog``. Other free inputs live in catalogs that
   are not mirrored and are listed only; node outputs missing from the catalog are
   MemoryDatasets and are listed only.

``--io`` prints each checked pipeline's node inputs and outputs. Exits non-zero on a
failure. The mirror's registry is incomplete (lines 54-130 and 180+ not photographed),
so a pipeline missing from it is reported, not failed.
"""

import importlib
import importlib.abc
import importlib.machinery
import pathlib
import re
import sys
import traceback
import types

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))
PKG = "enbd_collections"
STUBBED: list[str] = []
NO_INIT: list[str] = []
# Mirrored feature pipelines the persona axes read, checked like the crx_* ones.
CHECKED = (
    "product_primary",
    "product_features",
    "bureau_salary_bounces",
    "casa_primary",
    "casa_features",
    "location_features",
    "digital_login",
)
# Outputs of these pipelines must be persisted in a mirrored catalog.
OWN_CATALOG = ("product_primary", "product_features", "bureau_salary_bounces")


class _Stub:
    """Any attribute is a stub; calling one returns an empty Kedro pipeline."""

    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        return _Stub()

    def __call__(self, *args, **kwargs):
        from kedro.pipeline import Pipeline  # pylint: disable=import-outside-toplevel

        return Pipeline([])

    def __iter__(self):
        return iter(())


def _module_getattr(module_name: str):
    def stub(name):
        if name.startswith("__"):
            raise AttributeError(name)
        STUBBED.append(f"{module_name}.{name}")
        return _Stub()

    return stub


class _StubFinder(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    """Last on ``sys.meta_path``: stubs ``enbd_collections`` modules not on disk."""

    def find_spec(self, fullname, path, target=None):
        if fullname.startswith(f"{PKG}."):
            return importlib.machinery.ModuleSpec(fullname, self, is_package=True)
        return None

    def create_module(self, spec):
        module = types.ModuleType(spec.name)
        module.__path__ = []
        module.__getattr__ = _module_getattr(spec.name)
        STUBBED.append(spec.name)
        return module

    def exec_module(self, module):
        pass


def _yaml_keys(folder: pathlib.Path) -> dict:
    out = {}
    for f in sorted(folder.glob("*.yml")):
        out.update(yaml.safe_load(f.read_text()) or {})
    return out


def _param_exists(name: str, params: dict, globals_: dict) -> bool:
    node = params
    for part in name.split("."):
        if isinstance(node, str) and node.startswith("${globals:"):
            node = globals_.get(node[len("${globals:") : -1])
        if not isinstance(node, dict) or part not in node:
            return False
        node = node[part]
    return True


def _module_names() -> list[str]:
    names = []
    for path in sorted((SRC / PKG).rglob("*.py")):
        rel = path.relative_to(SRC).with_suffix("")
        parts = list(rel.parts)
        if parts[-1] == "__init__":
            parts = parts[:-1]
        names.append(".".join(parts))
    return names


def _import_modules() -> list[str]:
    """Import every mirrored module; a missing name from a partly mirrored workplace
    module is stubbed (and listed). Returns the failures."""
    failures = []
    for name in _module_names():
        if name == f"{PKG}.pipeline_registry":
            continue
        for _ in range(20):
            try:
                importlib.import_module(name)
                break
            except ImportError as exc:
                missing = re.match(
                    r"cannot import name '(\w+)' from '([\w.]+)'", str(exc)
                )
                source = sys.modules.get(missing[2]) if missing else None
                if source is None or getattr(source, "__file__", None):
                    failures.append(f"import {name}: {exc}")
                    break
                setattr(source, missing[1], _Stub())
                STUBBED.append(f"{missing[2]}.{missing[1]}")
            except Exception as exc:  # pylint: disable=broad-except
                tb = traceback.format_exception_only(type(exc), exc)[-1].strip()
                failures.append(f"import {name}: {tb}")
                break
    for name, module in list(sys.modules.items()):  # namespace packages (no __init__)
        if not name.startswith(f"{PKG}.") or getattr(module, "__file__", None):
            continue
        if (SRC / name.replace(".", "/") / "pipeline.py").exists():
            NO_INIT.append(name)  # the registry calls <package>.create_pipeline
            module.__getattr__ = _from_pipeline_module(name)
        elif not hasattr(module, "__getattr__"):
            module.__getattr__ = _module_getattr(name)
    return failures


def _from_pipeline_module(package: str):
    def attr(name):
        if name.startswith("__"):
            raise AttributeError(name)
        return getattr(importlib.import_module(f"{package}.pipeline"), name)

    return attr


def main() -> int:  # pylint: disable=too-many-locals,too-many-branches
    sys.meta_path.append(_StubFinder())
    failures = _import_modules()
    registry = importlib.import_module(f"{PKG}.pipeline_registry")
    registered = registry.register_pipelines()
    pipelines = {
        k: v for k, v in registered.items() if k.startswith("crx_") or k in CHECKED
    }
    not_registered = [k for k in CHECKED if k not in registered]
    catalog = _yaml_keys(ROOT / "conf/base/catalog")
    crx_catalog = yaml.safe_load(
        (ROOT / "conf/base/catalog/catalog_crx.yml").read_text()
    )
    params = _yaml_keys(ROOT / "conf/base/parameters")
    globals_ = yaml.safe_load((ROOT / "conf/dev/globals_dev.yml").read_text()) or {}
    external, memory = set(), set()
    show_io = "--io" in sys.argv
    for name, pipe in sorted(pipelines.items()):
        if not pipe.nodes:
            failures.append(f"{name}: empty pipeline")
        if show_io:
            print(f"\n## {name}")
            for n in pipe.nodes:
                outs = ", ".join(n.outputs) or "(log only)"
                print(f"- `{n.name}`: {', '.join(n.inputs)} -> {outs}")
        free = pipe.inputs()
        for ds in sorted(pipe.datasets()):
            if ds.startswith("params:"):
                if not _param_exists(ds[len("params:") :], params, globals_):
                    failures.append(f"{name}: {ds} not in parameters")
            elif ds in free:
                if ds.startswith("crx_") and ds not in crx_catalog:
                    failures.append(f"{name}: input {ds} not in catalog_crx.yml")
                elif ds not in catalog:
                    external.add(ds)
            elif ds not in catalog:
                if name in OWN_CATALOG:
                    failures.append(f"{name}: output {ds} not in conf/base/catalog")
                else:
                    memory.add(f"{name}: {ds}")
    stub_mirrored = sorted({m for m in STUBBED if (SRC / m.replace(".", "/")).exists()})
    print(f"modules imported: {len(_module_names()) - 1}")
    print(f"pipelines checked: {len(pipelines)} ({', '.join(sorted(pipelines))})")
    print(f"checked pipelines not in the mirror registry: {not_registered or 'none'}")
    print(f"stubbed workplace modules / names (not mirrored): {len(set(STUBBED))}")
    for m in sorted(set(STUBBED)):
        if ".pipelines." not in m:
            print(f"  {m}")
    print(f"packages without __init__.py (read through pipeline.py): {len(NO_INIT)}")
    for m in NO_INIT:
        print(f"  {m}")
    print(f"node outputs not in the catalog (MemoryDataset): {len(memory)}")
    for m in sorted(memory):
        print(f"  {m}")
    print(f"free inputs from catalogs not mirrored: {len(external)}")
    print(f"  {', '.join(sorted(external))}")
    failures += [f"mirrored module stubbed: {m}" for m in stub_mirrored]
    for f in failures:
        print(f"FAIL {f}")
    print(f"smoke: {'FAIL' if failures else 'pass'} ({len(failures)} failures)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
