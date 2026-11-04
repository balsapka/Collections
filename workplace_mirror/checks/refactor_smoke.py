"""Import smoke test of the crx_persona pipelines (refactor gate 5).

    python workplace_mirror/checks/refactor_smoke.py [--io]

Imports ``pipeline_registry`` and calls ``register_pipelines()``. Workplace modules that
are not mirrored here (other domains, DCORE / Way4 helpers) are replaced by stubs and
listed; a crx_persona module that is missing is a failure. Then every ``crx_*`` pipeline
must build, and every node dataset must exist: ``crx_*`` datasets in
``catalog_crx.yml``, ``params:`` keys in ``conf/base/parameters`` (``globals`` keys
resolved from ``conf/dev/globals_dev.yml``). Other datasets live in catalogs that are
not mirrored and are listed only. ``--io`` prints each pipeline's node inputs and
outputs. Exits non-zero on a failure.
"""

import importlib
import importlib.abc
import importlib.machinery
import pathlib
import re
import sys
import types

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
CRX = "enbd_collections.pipelines.crx_persona"
STUBBED: list[str] = []
NO_INIT: list[str] = []


class _Stub:
    """Any attribute is a stub; calling one returns an empty Kedro pipeline."""

    def __getattr__(self, name):
        return _Stub()

    def __call__(self, *args, **kwargs):
        from kedro.pipeline import Pipeline  # pylint: disable=import-outside-toplevel

        return Pipeline([])

    def __iter__(self):
        return iter(())


class _StubFinder(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    """Last on ``sys.meta_path``: stubs ``enbd_collections`` modules not on disk."""

    def find_spec(self, fullname, path, target=None):
        if fullname.startswith("enbd_collections.") and not fullname.startswith(CRX):
            return importlib.machinery.ModuleSpec(fullname, self, is_package=True)
        return None

    def create_module(self, spec):
        module = types.ModuleType(spec.name)
        module.__path__ = []
        module.__getattr__ = lambda name: _Stub()
        STUBBED.append(spec.name)
        return module

    def exec_module(self, module):
        pass


def _recording_stub(module_name: str):
    def stub(name):
        STUBBED.append(f"{module_name}.{name}")
        return _Stub()

    return stub


def _from_pipeline_module(package: str):
    def attr(name):
        return getattr(importlib.import_module(f"{package}.pipeline"), name)

    return attr


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


def _import_registry():
    """Import the registry; a name missing from a partly mirrored workplace module is
    stubbed (and listed) and the import retried."""
    while True:
        try:
            return importlib.import_module("enbd_collections.pipeline_registry")
        except ImportError as exc:
            missing = re.match(r"cannot import name '(\w+)' from '([\w.]+)'", str(exc))
            if not missing or missing[2].startswith(CRX):
                raise
            setattr(sys.modules[missing[2]], missing[1], _Stub())
            STUBBED.append(f"{missing[2]}.{missing[1]}")
            for m in [m for m in sys.modules if m.startswith(CRX)]:
                del sys.modules[m]


def main() -> int:
    sys.meta_path.append(_StubFinder())
    pipeline_registry = _import_registry()
    for name, module in list(sys.modules.items()):  # partly mirrored workplace packages
        if name.startswith("enbd_collections.") and not name.startswith(CRX):
            if not hasattr(module, "__getattr__"):
                module.__getattr__ = _recording_stub(name)
        elif name.startswith(CRX) and getattr(module, "__file__", None) is None:
            # no __init__.py in the mirror (a namespace package): read its pipeline.py
            NO_INIT.append(name)
            module.__getattr__ = _from_pipeline_module(name)

    pipelines = {
        k: v
        for k, v in pipeline_registry.register_pipelines().items()
        if k.startswith("crx_")
    }
    catalog = _yaml_keys(ROOT / "conf/base/catalog")
    crx_catalog = yaml.safe_load(
        (ROOT / "conf/base/catalog/catalog_crx.yml").read_text()
    )
    params = _yaml_keys(ROOT / "conf/base/parameters")
    globals_ = yaml.safe_load((ROOT / "conf/dev/globals_dev.yml").read_text()) or {}
    failures, external, memory = [], set(), set()
    show_io = "--io" in sys.argv
    for name, pipe in sorted(pipelines.items()):
        if not pipe.nodes:
            failures.append(f"{name}: empty pipeline")
        if show_io:
            print(f"\n## {name}")
        for n in pipe.nodes:
            if show_io:
                ins = ", ".join(n.inputs)
                print(f"- `{n.name}`: {ins} -> {', '.join(n.outputs) or '(log only)'}")
        for ds in sorted(pipe.datasets()):
            if ds.startswith("params:"):
                if not _param_exists(ds[len("params:") :], params, globals_):
                    failures.append(f"{name}: {ds} not in parameters")
            elif ds.startswith("crx_") and ds not in crx_catalog:
                # a free input must be persisted; a node output is a MemoryDataset
                if ds in pipe.inputs():
                    failures.append(f"{name}: input {ds} not in catalog_crx.yml")
                else:
                    memory.add(f"{name}: {ds}")
            elif not ds.startswith("crx_") and ds not in catalog:
                external.add(ds)
    stub_crx = [m for m in STUBBED if m.startswith(CRX)]
    print(f"\ncrx pipelines built: {len(pipelines)}")
    print(f"stubbed workplace modules (not mirrored): {len(STUBBED)}")
    for m in STUBBED:
        if ".pipelines." not in m or "crx_persona" in m:
            print(f"  {m}")
    print(f"crx packages without __init__.py in the mirror: {len(NO_INIT)}")
    for m in NO_INIT:
        print(f"  {m}")
    print(f"crx node outputs not in the catalog (memory only): {len(memory)}")
    for m in sorted(memory):
        print(f"  {m}")
    print(f"datasets from catalogs not mirrored: {', '.join(sorted(external))}")
    for f in failures + [f"crx module stubbed: {m}" for m in stub_crx]:
        print(f"FAIL {f}")
    print("smoke: " + ("FAIL" if failures or stub_crx else "pass"))
    return 1 if failures or stub_crx else 0


if __name__ == "__main__":
    sys.exit(main())
