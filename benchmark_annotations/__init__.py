__version__ = "21.10.0"

from pathlib import Path
import statistics
import subprocess
import sys
from tempfile import TemporaryDirectory
import time


obj_template = """
from dataclasses import dataclass, field
from typing import NewType, TypeAlias, TypeVar
import sys

Email= NewType("Email", str)
UserID: TypeAlias = int
T = TypeVar("T")

@dataclass
class Object:
    simple: bool
    author: UserID
    emails: set[Email] = field(default_factory=set)

    @classmethod
    def from_str(cls: type[T], serialized: str) -> T:
        ...
"""

func_template = """
def function_simple{func_idx}(arg: str) -> None:
    ...

def function_complex{func_idx}(arg1: int, arg2: dict[int, list[int | str | None]]) -> Object:
    ...
"""

psutil_template = """
import os
import psutil

from . import test

proc = psutil.Process(os.getpid())
rss_mb = proc.memory_info().rss / 1024 / 1024
print(f"{rss_mb:.2f} MB")
"""


def generate_modules(d: Path, with_future: bool) -> None:
    d = d / "example_{}".format("with_future" if with_future else "no_future")
    d.mkdir()
    for mod_idx in range(1000):
        pkgname = f"pkg{str(mod_idx)[0]}"
        modname = f"module{mod_idx}"
        pkg = d / pkgname
        pkg.mkdir(exist_ok=True)
        with (pkg / f"{modname}.py").open("w") as f:
            if with_future:
                f.write("from __future__ import annotations\n\n")
            f.write(obj_template)
            for func_idx in range(100):
                f.write(func_template.format(func_idx=func_idx))
            f.write("print(__file__, file=sys.stderr)")
        with (d / "test.py").open("a") as f:
            f.write(f"from .{pkgname} import {modname}\n")

    with (d / "test_mem.py").open("a") as f:
        f.write(psutil_template)


def run_once(d: Path, with_future: bool) -> None:
    example = "example_with_future" if with_future else "example_no_future"
    print((" " + example + " ").center(50, "*"))

    generate_modules(d, with_future=with_future)
    times = []
    for i in range(21):
        print(end=".", flush=True)
        start = time.monotonic()
        proc = subprocess.run(
            [sys.executable, "-m", f"{example}.test"], cwd=d, capture_output=True
        )
        proc.check_returncode()
        times.append(time.monotonic() - start)
    print()
    mean = statistics.geometric_mean(times[1:])
    stdev = statistics.stdev(times[1:])

    print(f"Import time: {mean:.2f}s \N{PLUS-MINUS SIGN}{stdev:.2f}s")

    proc = subprocess.run(
        [sys.executable, "-m", f"{example}.test_mem"], cwd=d, capture_output=True
    )
    proc.check_returncode()
    print(f"RSS Memory usage: {proc.stdout.decode().strip()}")


def main() -> None:
    with TemporaryDirectory(suffix="_benchmark_annotations") as tempdir:
        temppath = Path(tempdir)
        run_once(temppath, with_future=False)
        run_once(temppath, with_future=True)
