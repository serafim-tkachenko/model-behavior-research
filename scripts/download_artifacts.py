"""Download and verify frozen evidence; never extract or execute archived code."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import urllib.request

ROOT = Path(__file__).resolve().parents[1]

def digest(path):
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()

def main():
    manifest = json.loads((ROOT / "artifacts/manifest.json").read_text())
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", choices=[a["name"] for a in manifest["archives"]])
    args = parser.parse_args()
    entry = next(a for a in manifest["archives"] if a["name"] == args.archive)
    dest = ROOT / ".release"
    dest.mkdir(exist_ok=True)
    result = dest / entry["name"]
    if result.exists() and digest(result) == entry["sha256"]:
        print("Verified:", result)
        return
    base = f"https://github.com/{manifest['repository']}/releases/download/{manifest['release']}/"
    for part in entry["parts"]:
        path = dest / part["name"]
        if not path.exists() or path.stat().st_size != part["size"] or digest(path) != part["sha256"]:
            temp = path.with_name(path.name + ".download")
            with urllib.request.urlopen(base + part["name"], timeout=120) as response, temp.open("wb") as f:
                shutil.copyfileobj(response, f, 1024 * 1024)
            if temp.stat().st_size != part["size"] or digest(temp) != part["sha256"]:
                raise RuntimeError(f"Checksum mismatch: {part['name']}")
            temp.replace(path)
        print("Verified part:", part["name"], flush=True)
    if len(entry["parts"]) > 1:
        temp = result.with_name(result.name + ".assembled")
        with temp.open("wb") as output:
            for part in entry["parts"]:
                with (dest / part["name"]).open("rb") as source:
                    shutil.copyfileobj(source, output, 1024 * 1024)
        temp.replace(result)
    if digest(result) != entry["sha256"]:
        raise RuntimeError("Complete archive checksum mismatch")
    print("Verified:", result)
    print("Suggested extraction destination:", entry["suggested_destination"])

if __name__ == "__main__":
    main()

