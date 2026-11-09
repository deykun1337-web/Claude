"""Ruslan v2: friendlier face, pink DEYKUN cap, white tee with a gold chain, jeans (blocky 16px textures)."""
from tex import PX
SK, SK2, HAIR, PINK, PINK2, PINKD = "#EBC3A5", "#D9A98A", "#4A3224", "#F0569A", "#FF7DB4", "#B8336E"
EYE, IRIS, BROW, MOUTH = "#FFFFFF", "#5B3A22", "#4A3224", "#7A2E2A"
EXPRS = ["neutral", "happy", "shock", "smug", "sad", "angry", "panic", "think"]


def face(expr, m, b):
    t = PX(16, 16, SK, 81, 5)
    t.p(0, 0, PINK, 16, 4, 4); t.p(4, 1, "#FFFFFF", 8, 1, 2); t.p(5, 2, PINK2, 6, 1, 3)  # cap + DEYKUN print stripe
    t.p(0, 4, PINKD, 16, 1, 3)                                                            # brim shadow
    t.p(0, 5, HAIR, 1, 3); t.p(15, 5, HAIR, 1, 3)
    by = 5 if expr in ("shock", "panic", "happy") else 6
    if expr == "angry": t.p(3, 6, BROW, 3); t.p(10, 6, BROW, 3); t.p(5, 7, BROW); t.p(10, 7, BROW)
    elif expr == "sad": t.p(3, 6, BROW, 3); t.p(10, 6, BROW, 3); t.p(3, 5, BROW); t.p(12, 5, BROW)
    elif expr == "think": t.p(3, 6, BROW, 3); t.p(10, 5, BROW, 3)
    else: t.p(3, by, BROW, 3); t.p(10, by, BROW, 3)
    for ex in (3, 10):
        if b: t.p(ex, 8, "#5A3A2A", 3); continue
        if expr == "happy": t.p(ex, 8, "#3A2418", 3); t.p(ex + 1, 7, "#3A2418"); continue
        if expr == "smug": t.p(ex, 8, EYE, 3); t.p(ex + 1, 8, IRIS); t.p(ex, 7, SK2, 3); continue
        h = 2 if expr in ("shock", "panic") else 1
        t.p(ex, 7 if h == 2 else 8, EYE, 3, h + (0 if h == 2 else 0)); t.p(ex + 1, 8, IRIS); t.p(ex + 1, 7 if h == 2 else 8, IRIS)
    t.p(3, 10, "#F2A9A0", 2, 1, 3); t.p(11, 10, "#F2A9A0", 2, 1, 3)  # blush
    t.p(7, 9, SK2, 2, 2)                                              # nose shade
    for x, y in ((5, 13), (10, 13), (6, 14), (9, 14), (7, 15), (8, 15)): t.p(x, y, "#CFA184", noise=3)  # light stubble
    if m >= 1:
        t.p(6, 12, "#3A0F0A", 4, m + 1); t.p(7, 12 + m, "#E86A7A", 2)
    elif expr in ("happy", "smug"):
        t.p(5, 12, MOUTH); t.p(10, 12, MOUTH); t.p(6, 13, MOUTH, 4)
    elif expr in ("sad",):
        t.p(6, 12, MOUTH, 4); t.p(5, 13, MOUTH); t.p(10, 13, MOUTH)
    elif expr in ("shock", "panic"):
        t.p(7, 12, "#3A0F0A", 2, 2)
    else:
        t.p(6, 12, MOUTH, 4)
    return t


for e in EXPRS:
    for m in (0, 1, 2):
        for b in (0, 1):
            face(e, m, b).save(f"r2_face_{e}_{m}_{b}")
s = PX(16, 16, SK, 82, 5); s.p(0, 0, PINK, 16, 4, 4); s.p(0, 4, HAIR, 16, 3, 4); s.save("r2_side")
s = PX(16, 16, SK, 83, 5); s.p(0, 0, PINK, 16, 6, 4); s.p(0, 6, HAIR, 16, 6, 4); s.save("r2_back")
c = PX(16, 16, PINK, 84, 5); c.p(6, 6, "#FFFFFF", 4, 4, 2); c.save("r2_cap")
tee = PX(16, 16, "#F4F2EE", 85, 4)
for x, y in ((3, 0), (4, 1), (5, 2), (6, 3), (7, 3), (8, 3), (9, 3), (10, 2), (11, 1), (12, 0)): tee.p(x, y, "#F2B53A", noise=6)
tee.p(7, 4, "#F2B53A", 2, 2, 6); tee.save("r2_tee")
PX(16, 16, "#F4F2EE", 86, 4).save("r2_tee_side")
arm = PX(16, 16, SK, 87, 5); arm.p(0, 0, "#F4F2EE", 16, 6, 4); arm.save("r2_arm")
j = PX(16, 16, "#3C5A8C", 88, 8)
for k in range(6): j.p(j.rr.randint(0, 15), j.rr.randint(0, 15), "#4D6EA3", 2, 1, 4)
j.p(0, 14, "#1E2430", 16, 2, 3); j.save("r2_jeans")
print("ok")
