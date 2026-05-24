from __future__ import annotations

import sys
import importlib.util
from pathlib import Path


def main() -> int:
    project_dir = Path(__file__).resolve().parent.parent
    scripts_dir = project_dir / "scripts"
    if not scripts_dir.exists():
        spec = importlib.util.find_spec("scripts")
        if spec and spec.submodule_search_locations:
            scripts_dir = Path(list(spec.submodule_search_locations)[0])
    sys.path.insert(0, str(scripts_dir))
    from geo_cli import main as cli_main

    return cli_main()


if __name__ == "__main__":
    raise SystemExit(main())
