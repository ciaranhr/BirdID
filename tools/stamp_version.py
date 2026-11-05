#!/usr/bin/env python3
"""Set the service worker's cache VERSION, e.g. to the commit being deployed.

Usage: python3 tools/stamp_version.py <version> [path/to/sw.js]

CI runs this before each deploy, so every release changes sw.js. Browsers then install the new
worker, which precaches a fresh, consistent copy of the app shell and drops the old one - no
manual version bump needed. Fails (rather than silently doing nothing) if the line isn't found.
"""
import os, re, sys

SW = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app", "sw.js")
PATTERN = re.compile(r"^const VERSION = '[^'\n]*';", re.M)


def stamp(text, version):
    if not re.fullmatch(r"[A-Za-z0-9._-]+", version):
        raise ValueError(f"unsafe version string: {version!r}")
    new, n = PATTERN.subn(f"const VERSION = '{version}';", text)
    if n != 1:
        raise ValueError(f"expected exactly one `const VERSION = '...';` line, found {n}")
    return new


def main(argv):
    if len(argv) not in (2, 3):
        sys.exit(__doc__)
    path = argv[2] if len(argv) == 3 else SW
    with open(path) as f:
        text = f.read()
    with open(path, "w") as f:
        f.write(stamp(text, argv[1]))
    print(f"{path}: VERSION = {argv[1]}")


if __name__ == "__main__":
    main(sys.argv)
