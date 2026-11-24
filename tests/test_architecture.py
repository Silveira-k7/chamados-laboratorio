import ast
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1] / "chamados"
ALLOWED_INTERNAL_IMPORTS = {
    "__init__": set(),
    "__main__": {"cli"},
    "cli": {"application", "domain", "storage"},
    "application": {"domain"},
    "domain": set(),
    "storage": {"domain"},
}
SQLITE_MODULES = {"cli", "storage"}


def imported_modules(source: Path) -> set[str]:
    modules = set()
    for node in ast.walk(ast.parse(source.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level and node.module is None:
                modules.update(f"chamados.{alias.name}" for alias in node.names)
            elif node.level:
                modules.add(f"chamados.{node.module}")
            elif node.module == "chamados":
                modules.update(f"chamados.{alias.name}" for alias in node.names)
            elif node.module:
                modules.add(node.module)
    return modules


class ArchitectureTest(unittest.TestCase):
    def test_application_and_domain_do_not_depend_on_adapters(self):
        source_files = sorted(PACKAGE.glob("*.py"))
        self.assertEqual({file.stem for file in source_files}, ALLOWED_INTERNAL_IMPORTS.keys())
        for source in source_files:
            with self.subTest(module=source.stem):
                imports = imported_modules(source)
                internal = {name.split(".")[1] for name in imports if name.startswith("chamados.")}
                self.assertLessEqual(internal, ALLOWED_INTERNAL_IMPORTS[source.stem])
                if source.stem not in SQLITE_MODULES:
                    self.assertFalse(any(name.split(".")[0] == "sqlite3" for name in imports))
