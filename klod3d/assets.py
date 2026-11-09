"""Poly Haven (CC0) asset fetcher → klod3d/build/assets/<id>/...  (HDRIs, PBR textures, models). Cached.
Usage: python3 klod3d/assets.py hdri <id> [2k]     → build/assets/<id>.hdr
       python3 klod3d/assets.py tex <id> [2k]      → build/assets/<id>/{diff,nor_gl,rough,disp}.jpg|png
       python3 klod3d/assets.py model <id> [1k]    → build/assets/<id>/<id>.blend (+ textures)
       python3 klod3d/assets.py search <hdris|textures|models> <word>
Credit is not required (CC0) but we keep a list in reels/CREDITS.md."""
import json, os, sys, urllib.request
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build", "assets"); os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "deykun-reels/1.0"}


def get(url): return json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read())


def dl(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 0: return path
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300) as r, open(path, "wb") as f: f.write(r.read())
    return path


if __name__ == "__main__":
    kind, aid = sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else ""
    res = sys.argv[3] if len(sys.argv) > 3 else ("2k" if kind != "model" else "1k")
    if kind == "search":
        d = get(f"https://api.polyhaven.com/assets?t={aid}")
        w = sys.argv[3].lower()
        print("\n".join(k for k, v in d.items() if w in k or w in " ".join(v.get("tags", [])) + " ".join(v.get("categories", [])))[:3000])
    elif kind == "hdri":
        f = get(f"https://api.polyhaven.com/files/{aid}")["hdri"][res]["hdr"]["url"]; print(dl(f, os.path.join(OUT, f"{aid}.hdr")))
    elif kind == "tex":
        fs = get(f"https://api.polyhaven.com/files/{aid}")
        for m, key in (("Diffuse", "diff"), ("nor_gl", "nor_gl"), ("Rough", "rough"), ("Displacement", "disp")):
            if m in fs:
                ext = "jpg" if "jpg" in fs[m][res] else "png"
                print(dl(fs[m][res][ext]["url"], os.path.join(OUT, aid, f"{key}.{ext}")))
    elif kind == "model":
        # .blend (the system Blender's glTF importer is broken) — load with bpy.data.libraries.load(path) → objects
        g = get(f"https://api.polyhaven.com/files/{aid}")["blend"][res]["blend"]
        print(dl(g["url"], os.path.join(OUT, aid, f"{aid}.blend")))
        for rel, v in g.get("include", {}).items(): dl(v["url"], os.path.join(OUT, aid, rel))
