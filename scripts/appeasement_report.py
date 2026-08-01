#!/usr/bin/env python3
"""Detector mecânico de test-appeasement: produção moldada para o teste passar.

Emite sinais em JSON; o julgamento é da skill (two-stage: regra programática +
juiz para a borda). Stdlib-only, um arquivo, vendorizável em qualquer repo
Python. Regras TA-* documentadas em references/taxonomia.md da skill.

Uso:
    python3 -B appeasement_report.py [--src PKG] [--tests DIR] [--format json|text]
                                     [--baseline FILE] [--write-baseline]

Exit codes: 0 = limpo ou só estoque baselined; 1 = finding high novo; 2 = erro.
"""

__version__ = "1.0.0"

import argparse
import ast
import json
import re
import sys
from pathlib import Path

BUILTIN_BASES = {"tuple", "str", "dict", "list", "frozenset", "set", "int", "float", "bytes"}
HOTSPOT_THRESHOLD = 5
PRAGMA_RE = re.compile(r"#\s*appease:\s*allow\((TA-\d+)\)\s*(.*)$")


# ---------------------------------------------------------------- descoberta

def discover_src(root):
    pyproject = root / "pyproject.toml"
    if pyproject.is_file():
        text = pyproject.read_text(encoding="utf-8", errors="replace")
        name = None
        try:
            import tomllib

            data = tomllib.loads(text)
            name = (data.get("project") or {}).get("name")
        except Exception:
            match = re.search(r'^\s*name\s*=\s*"([^"]+)"', text, re.M)
            name = match.group(1) if match else None
        if name:
            candidate = name.replace("-", "_")
            for base in (root, root / "src"):
                if (base / candidate / "__init__.py").is_file():
                    return base / candidate
    candidates = [
        d for d in root.iterdir()
        if d.is_dir() and (d / "__init__.py").is_file()
        and d.name not in ("tests", "test", "docs", "examples", "scripts")
        and not d.name.startswith(".")
    ]
    if len(candidates) == 1:
        return candidates[0]
    return None


def discover_tests(root):
    for name in ("tests", "test"):
        if (root / name).is_dir():
            return root / name
    return None


def iter_py(path):
    for p in sorted(path.rglob("*.py")):
        if "__pycache__" in p.parts:
            continue
        yield p


def parse_file(path):
    try:
        return ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return None


# ------------------------------------------------- passe 1: índice dos testes

def _dotted(node):
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
        return ".".join(reversed(parts))
    return None


def build_patch_index(tests_dir, pkg_name):
    """{alvo_qualificado: {"sites": [path:line], "tuple_return": [path:line]}}"""
    index = {}
    parse_errors = 0

    def note(target, where, tuple_return=False):
        entry = index.setdefault(target, {"sites": [], "tuple_return": []})
        entry["sites"].append(where) if not tuple_return else entry["tuple_return"].append(where)

    for path in iter_py(tests_dir):
        tree = parse_file(path)
        if tree is None:
            parse_errors += 1
            continue
        imports = collect_imports(tree)
        rel = str(path)

        for node in ast.walk(tree):
            # patch("pkg.mod.sym") / mock.patch(...) / monkeypatch.setattr("pkg.mod.sym", ...)
            if isinstance(node, ast.Call):
                fname = _dotted(node.func) or ""
                leaf = fname.rsplit(".", 1)[-1]
                if leaf in ("patch", "setattr") and node.args:
                    first = node.args[0]
                    if isinstance(first, ast.Constant) and isinstance(first.value, str) and "." in first.value:
                        note(first.value, f"{rel}:{node.lineno}")
                    elif leaf == "setattr" and isinstance(first, ast.Name) and len(node.args) >= 2:
                        second = node.args[1]
                        if isinstance(second, ast.Constant) and isinstance(second.value, str):
                            module = imports.get(first.id)
                            if module:
                                note(f"{module}.{second.value}", f"{rel}:{node.lineno}")
                elif leaf == "object" and fname.endswith("patch.object") and len(node.args) >= 2:
                    mod_arg, attr_arg = node.args[0], node.args[1]
                    if isinstance(mod_arg, ast.Name) and isinstance(attr_arg, ast.Constant):
                        module = imports.get(mod_arg.id)
                        if module:
                            note(f"{module}.{attr_arg.value}", f"{rel}:{node.lineno}")

            # with patch("t") as m: ... m.return_value = (tupla crua)
            if isinstance(node, ast.With):
                aliases = {}
                for item in node.items:
                    call = item.context_expr
                    if (
                        isinstance(call, ast.Call)
                        and (_dotted(call.func) or "").rsplit(".", 1)[-1] == "patch"
                        and call.args
                        and isinstance(call.args[0], ast.Constant)
                        and isinstance(item.optional_vars, ast.Name)
                    ):
                        aliases[item.optional_vars.id] = call.args[0].value
                if aliases:
                    for sub in ast.walk(node):
                        if (
                            isinstance(sub, ast.Assign)
                            and len(sub.targets) == 1
                            and isinstance(sub.targets[0], ast.Attribute)
                            and sub.targets[0].attr == "return_value"
                            and isinstance(sub.targets[0].value, ast.Name)
                            and sub.targets[0].value.id in aliases
                            and isinstance(sub.value, (ast.Tuple, ast.List))
                        ):
                            note(aliases[sub.targets[0].value.id], f"{rel}:{sub.lineno}", tuple_return=True)
    return index, parse_errors


# --------------------------------------------------- passe 2: regras no src

def collect_imports(tree):
    """nome local → qualificado, cobrindo imports de módulo e de função."""
    mapping = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mapping[alias.asname or alias.name.split(".")[0]] = alias.name
        elif isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                mapping[alias.asname or alias.name] = f"{node.module}.{alias.name}"
    return mapping


def except_ranges(tree):
    """[(nome_da_exceção, lineno_inicial, lineno_final)]"""
    spans = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler) and node.name:
            end = max((n.lineno for n in ast.walk(node) if hasattr(n, "lineno")), default=node.lineno)
            spans.append((node.name, node.lineno, end))
    return spans


def pragma_map(path):
    mapping = {}
    for lineno, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        match = PRAGMA_RE.search(line)
        if match:
            mapping[lineno] = (match.group(1), match.group(2).strip())
    return mapping


def producers_in_scope(func_node, imports, pkg_name):
    """var → (qualificado, é_interno) para atribuições `var = f(...)` no escopo."""
    out = {}
    for node in ast.walk(func_node):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            if isinstance(node.value, ast.Call):
                fname = _dotted(node.value.func)
                if fname:
                    root_name = fname.split(".")[0]
                    qualified = fname
                    if root_name in imports:
                        qualified = imports[root_name] + fname[len(root_name):]
                    out[node.targets[0].id] = (qualified, qualified.startswith(pkg_name + "."))
    return out


def scan_src(src_dir, pkg_name, patch_index):
    findings, suppressed = [], []
    parse_errors = 0
    getenv_hits, indirection_hits = [], []

    for path in iter_py(src_dir):
        tree = parse_file(path)
        if tree is None:
            parse_errors += 1
            continue
        rel = str(path)
        imports = collect_imports(tree)
        exc_spans = except_ranges(tree)
        pragmas = pragma_map(path)

        def emit(rule, lineno, symbol, evidence, confidence, cross_ref=None):
            pragma = pragmas.get(lineno)
            item = {
                "rule_id": rule, "path": rel, "line": lineno, "symbol": symbol,
                "evidence": evidence, "confidence": confidence,
            }
            if cross_ref:
                item["cross_ref"] = cross_ref
            if pragma and pragma[0] == rule:
                if pragma[1]:
                    item["suppressed_reason"] = pragma[1]
                    suppressed.append(item)
                else:
                    item.update(rule_id="TA-0", confidence="medium",
                                evidence=f"supressão de {rule} sem motivo: {evidence}")
                    findings.append(item)
            else:
                findings.append(item)

        # TA-2: subclasse de builtin pendurando atributo
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                bases = {b.id for b in node.bases if isinstance(b, ast.Name)}
                if bases & BUILTIN_BASES:
                    hangs = any(
                        isinstance(sub, ast.Assign)
                        and any(isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name)
                                for t in sub.targets)
                        for method in node.body
                        if isinstance(method, ast.FunctionDef) and method.name in ("__new__", "__init__")
                        for sub in ast.walk(method)
                    )
                    if hangs:
                        emit("TA-2", node.lineno, node.name,
                             f"class {node.name}({', '.join(sorted(bases & BUILTIN_BASES))}) "
                             "pendura atributos em __new__/__init__", "high")

        # TA-1 / TA-3 por função
        for func in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
            producers = producers_in_scope(func, imports, pkg_name)
            for node in ast.walk(func):
                if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
                    continue
                if node.func.id == "getattr" and len(node.args) == 3:
                    obj = node.args[0]
                    if not isinstance(obj, ast.Name):
                        continue
                    if any(obj.id == name and start <= node.lineno <= end
                           for name, start, end in exc_spans):
                        continue  # getattr defensivo em exceção capturada: legítimo
                    produced = producers.get(obj.id)
                    if not produced or not produced[1]:
                        continue
                    qualified, _ = produced
                    attr = node.args[1].value if isinstance(node.args[1], ast.Constant) else "?"
                    matches = [t for t in patch_index
                               if t == qualified or t.rsplit(".", 1)[-1] == qualified.rsplit(".", 1)[-1]]
                    if matches:
                        sites = sum((patch_index[t]["sites"] for t in matches), [])
                        tuples = sum((patch_index[t]["tuple_return"] for t in matches), [])
                        cross = {"patched_in": sites[:10]}
                        extra = ""
                        if tuples:
                            cross["tuple_return_in"] = tuples[:10]
                            extra = f"; {len(tuples)} mock(s) devolvem tupla crua"
                        emit("TA-1", node.lineno, qualified,
                             f"getattr({obj.id}, {attr!r}, default) sobre retorno de {qualified}, "
                             f"patcheado em {len(sites)} teste(s){extra}", "high", cross)
                    else:
                        emit("TA-1", node.lineno, qualified,
                             f"getattr({obj.id}, {attr!r}, default) sobre retorno interno "
                             f"de {qualified}; sem patch de teste encontrado", "medium")
                elif node.func.id == "hasattr" and len(node.args) == 2:
                    obj = node.args[0]
                    if isinstance(obj, ast.Name) and obj.id in producers and producers[obj.id][1]:
                        emit("TA-3", node.lineno, producers[obj.id][0],
                             f"hasattr({obj.id}, ...) sobre retorno interno de {producers[obj.id][0]}",
                             "high")

        # TA-5: getenv dentro de função (informativa)
        for func in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
            for node in ast.walk(func):
                if isinstance(node, ast.Call):
                    fname = _dotted(node.func) or ""
                    if fname in ("os.getenv", "os.environ.get"):
                        getenv_hits.append(f"{rel}:{node.lineno}")

        # TA-6: alias de módulo interno usado só para ler constante (informativa)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.asname and alias.name.startswith(pkg_name + "."):
                        indirection_hits.append(f"{rel}:{node.lineno} ({alias.name} as {alias.asname})")
            elif isinstance(node, ast.ImportFrom):
                if node.module == pkg_name:
                    for alias in node.names:
                        if alias.asname and alias.name == "config":
                            indirection_hits.append(f"{rel}:{node.lineno} (from {pkg_name} import config as {alias.asname})")

    return findings, suppressed, getenv_hits, indirection_hits, parse_errors


def hotspots(patch_index, pkg_name):
    rows = []
    for target, entry in patch_index.items():
        if target.startswith(pkg_name + ".") and len(entry["sites"]) >= HOTSPOT_THRESHOLD:
            rows.append({"target": target, "patches": len(entry["sites"]),
                         "sample": entry["sites"][:3]})
    return sorted(rows, key=lambda r: -r["patches"])


# ------------------------------------------------------------------ baseline

def finding_key(item):
    return f"{item['rule_id']}|{item['path']}|{item['symbol']}"


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--src", help="pacote de produção (dir); auto-descoberto se omitido")
    parser.add_argument("--tests", help="diretório de testes; auto-descoberto se omitido")
    parser.add_argument("--format", choices=("json", "text"), default="text")
    parser.add_argument("--baseline", help="arquivo de baseline (ratchet)")
    parser.add_argument("--write-baseline", action="store_true",
                        help="grava o estoque atual de findings high no baseline e sai 0")
    args = parser.parse_args()

    root = Path.cwd()
    src = Path(args.src) if args.src else discover_src(root)
    tests = Path(args.tests) if args.tests else discover_tests(root)
    if not src or not src.is_dir():
        print("erro: pacote de produção não descoberto; use --src", file=sys.stderr)
        return 2
    if not tests or not tests.is_dir():
        print("erro: diretório de testes não descoberto; use --tests", file=sys.stderr)
        return 2
    pkg_name = src.name

    patch_index, test_errors = build_patch_index(tests, pkg_name)
    findings, suppressed, getenv_hits, indirection_hits, src_errors = scan_src(
        src, pkg_name, patch_index
    )
    seen = set()
    findings = [f for f in findings
                if (k := (f["rule_id"], f["path"], f["line"], f["symbol"])) not in seen
                and not seen.add(k)]
    total_files = sum(1 for _ in iter_py(src)) + sum(1 for _ in iter_py(tests))
    if total_files and (test_errors + src_errors) > total_files // 2:
        print("erro: parse falhou na maioria dos arquivos", file=sys.stderr)
        return 2

    info = []
    for hit in getenv_hits:
        info.append({"rule_id": "TA-5", "site": hit})
    for hit in indirection_hits:
        info.append({"rule_id": "TA-6", "site": hit})

    baseline_keys = set()
    baseline_path = Path(args.baseline) if args.baseline else None
    if baseline_path and baseline_path.is_file():
        baseline_keys = {e["key"] for e in json.loads(baseline_path.read_text())["entries"]}

    high = [f for f in findings if f["confidence"] == "high"]
    new_high = [f for f in high if finding_key(f) not in baseline_keys]
    baselined = [f for f in high if finding_key(f) in baseline_keys]

    if args.write_baseline:
        target = baseline_path or Path(".appeasement-baseline.json")
        target.write_text(json.dumps({
            "version": __version__,
            "entries": [{"key": finding_key(f), "rule_id": f["rule_id"],
                         "path": f["path"], "symbol": f["symbol"]} for f in high],
        }, ensure_ascii=False, indent=1) + "\n")
        print(f"baseline gravado em {target} com {len(high)} entrada(s)")
        return 0

    report = {
        "version": __version__,
        "src": str(src), "tests": str(tests),
        "findings": findings,
        "suppressed": suppressed,
        "informational": {"items": info, "hotspots": hotspots(patch_index, pkg_name)},
        "summary": {
            "by_rule": {},
            "gate_eligible_new": len(new_high),
            "baselined": len(baselined),
            "parse_errors": test_errors + src_errors,
        },
    }
    for f in findings:
        report["summary"]["by_rule"][f["rule_id"]] = report["summary"]["by_rule"].get(f["rule_id"], 0) + 1

    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=1))
    else:
        for f in findings:
            print(f"[{f['confidence']:>6}] {f['rule_id']} {f['path']}:{f['line']} — {f['evidence']}")
        for s in suppressed:
            print(f"[suppr.] {s['rule_id']} {s['path']}:{s['line']} — motivo: {s['suppressed_reason']}")
        for h in report["informational"]["hotspots"]:
            print(f"[info  ] TA-4 {h['target']} patcheado {h['patches']}x")
        print(f"\n{len(findings)} finding(s); {len(new_high)} high novo(s); "
              f"{len(baselined)} no baseline; {len(info)} informativo(s)")

    return 1 if new_high else 0


if __name__ == "__main__":
    sys.exit(main())
