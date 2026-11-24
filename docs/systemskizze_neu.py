"""System sketch (scientific style, English): buses as bars, storage as one tank with three layers,
constraints as numbered markers with formulas in the legend.
Numbers: small network, base case, as of E44 (docs/systemskizze.md) - update here when parameters change.
Run: uv run python docs/systemskizze_neu.py docs/systemskizze_neu"""

import sys

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

mpl.rcParams.update(
    {
        "font.family": "STIXGeneral",
        "mathtext.fontset": "stix",
        "font.size": 11,
        "hatch.linewidth": 0.5,
    }
)
STROM, SOLAR, WAERME, GRAU = "#2f5d8a", "#c8901a", "#b03a2e", "#4d4d4d"
TITEL, TEXT, KLEIN = 13.5, 11.5, 10.5

fig, ax = plt.subplots(figsize=(16, 9.6))
ax.set(xlim=(0, 17.2), ylim=(-2.15, 10.0))
ax.axis("off")


def box(x, y, w, h, titel, zeilen=(), fc="white", opt=False, ls="-"):
    ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec="black", lw=0.9, zorder=3, ls=ls))
    n = len(zeilen)
    mitte = y + h / 2 + 0.18 * n
    ax.text(x + w / 2, mitte, titel + (r"$^{\ast}$" if opt else ""), ha="center", va="center",
            fontsize=TITEL, weight="bold", zorder=4)
    for i, z in enumerate(zeilen):
        ax.text(x + w / 2, mitte - 0.37 * (i + 1), z, ha="center", va="center", fontsize=TEXT,
                zorder=4)


def schiene(x, y0, y1, name, farbe):
    ax.plot([x, x], [y0, y1], color=farbe, lw=5, solid_capstyle="butt", zorder=2)
    ax.text(x, y1 + 0.12, name, ha="center", va="bottom", fontsize=KLEIN + 0.5, style="italic",
            color=farbe)


def pfeil(p0, p1, farbe, label="", lpos=0.5, ls="-", z=1):
    ax.add_patch(
        FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=13, lw=1.3, color=farbe,
                        linestyle=ls, zorder=z, shrinkA=0, shrinkB=0.5)
    )
    if label:
        x = p0[0] + (p1[0] - p0[0]) * lpos
        y = p0[1] + (p1[1] - p0[1]) * lpos
        ax.text(x, y + 0.1, label, ha="center", va="bottom", fontsize=KLEIN, zorder=5,
                color=farbe if ls != "-" else "black", bbox=dict(fc="white", ec="none", pad=0.6))


def marke(x, y, nr):
    ax.text(x, y, str(nr), ha="center", va="center", fontsize=9.5, zorder=7,
            bbox=dict(boxstyle="circle,pad=0.15", fc="white", ec="black", lw=0.8))


# ---------------- electricity side ----------------
box(0.3, 6.95, 2.6, 1.55, "Grid electricity",
    [r"$c_\mathrm{el}(t)$ = day-ahead 2024", "+ fees, mean ≈ 23 ct/kWh"], fc="#ececec")
box(3.5, 6.95, 2.6, 1.55, "Grid connection", ["capacity charge", "44 €/(kW·a) incl. BKZ"], opt=True)
pfeil((2.9, 7.72), (3.5, 7.72), STROM)
schiene(6.75, 5.35, 9.55, "Electricity", STROM)
pfeil((6.1, 7.72), (6.72, 7.72), STROM)

bx, bw = 8.2, 4.0
box(bx, 8.55, bw, 1.0, "Power-to-heat", [r"$\eta$ = 0.99;  $P \geq \dot Q_\mathrm{max}$;  340 €/kW"], opt=True)
box(bx, 6.85, bw, 1.4, "Air-source heat pump",
    [r"$\mathrm{COP} = 0.452\,T_\mathrm{sup}/(T_\mathrm{sup}-T_a)$",
     r"off at $T_a < -7$ °C;  1,730 €/kW"],
    opt=True)
box(bx, 5.35, bw, 1.2, "Storage heat pump", ["COP = 3.9 (Jensen et al.);  1,100 €/kW"], opt=True)
for y in (9.05, 7.55, 5.95):
    pfeil((6.78, y), (bx, y), STROM)
marke(bx + bw - 0.2, 6.85 + 1.4 - 0.2, 3)

# ---------------- solar side ----------------
box(0.3, 2.2, 2.6, 1.6, "Collector field", [r"$\dot Q_\mathrm{sol}(t) = A\,q_\mathrm{sol}(t)$",
                                            r"$T_\mathrm{m}$ = 67.5 °C"], fc="#ececec", opt=True)
marke(0.5, 3.6, 1)
schiene(3.55, 0.35, 4.3, "Solar", SOLAR)
pfeil((2.9, 3.0), (3.52, 3.0), SOLAR)

sx, sw = 6.0, 2.9
schichten = [  # y0, h, colour, title, text
    (3.1, 1.25, "#f3c9a3", "hot core", "85 °C, used directly"),
    (2.15, 0.95, "#f6e3cf", "transition zone", "45–85 °C, preheating"),
    (0.85, 1.3, "#d6e4f0", "cold part", "10–45 °C, via heat pump only"),
]
for y0, h, fc, titel, text in schichten:
    ax.add_patch(Rectangle((sx, y0), sw, h, fc=fc, ec="black", lw=0.9, zorder=3))
    ax.text(sx + sw / 2 + 0.15, y0 + h / 2 + 0.16, titel, ha="center", va="center",
            fontsize=TEXT + 0.5, weight="bold", zorder=4)
    ax.text(sx + sw / 2 + 0.15, y0 + h / 2 - 0.2, text, ha="center", va="center", fontsize=KLEIN,
            zorder=4)
ax.text(sx + sw / 2, 4.5, r"Pit thermal energy storage (PTES)$^{\ast}$", ha="center", va="bottom",
        fontsize=TITEL, weight="bold")
for i, nr in enumerate((1, 2, 4)):
    marke(sx + sw - 0.2 - 0.33 * (2 - i), 4.15, nr)
for y_a in (3.1, 2.15):
    pfeil((sx + 0.25, y_a + 0.22), (sx + 0.25, y_a - 0.32), GRAU, z=5)
ax.text(sx - 0.1, 2.6, "mixing\n(no\nloss)", ha="right", va="center", fontsize=KLEIN - 0.5,
        style="italic", color=GRAU)

pfeil((3.58, 3.72), (sx, 3.72), SOLAR, r"charge, 45 → 85 °C", lpos=0.5)
pfeil((3.58, 1.5), (sx, 1.5), SOLAR, r"charge, 10 → 45 °C", lpos=0.5)
pfeil((3.58, 0.5), (14.17, 0.5), SOLAR, "solar heat direct", lpos=0.62)
marke(4.15, 3.72, 6)

wx = 14.2
pfeil((sx + sw, 3.72), (wx - 0.03, 3.72), WAERME, "direct discharge", lpos=0.66)
pfeil((sx + sw, 2.6), (wx - 0.03, 2.6), WAERME, r"preheat return, 45 → 60 °C", lpos=0.66)
# charging the hot core with heat pump / PtH heat (base case since E43, day-ahead price)
pfeil((wx - 0.03, 4.25), (sx + sw, 4.25), WAERME, "charging from grid (HP / PtH)", lpos=0.62,
      ls=(0, (4, 3)))
marke(10.2, 3.72, 6)
marke(13.4, 3.72, 5)
marke(13.4, 2.6, 5)
# source heat: cold part -> storage heat pump
qx = 9.6
ax.plot([sx + sw, qx, qx], [1.5, 1.5, 5.15], color=STROM, lw=1.2, ls=(0, (4, 3)), zorder=1)
pfeil((qx, 5.1), (qx, 5.35), STROM)
ax.text(qx + 0.12, 1.58, r"source heat $(\mathrm{COP}-1)\,P_\mathrm{el}$", fontsize=KLEIN,
        color=STROM, va="bottom")

# ---------------- heat side ----------------
schiene(wx, 0.3, 9.55, "Heat", WAERME)
for y in (9.05, 7.55, 5.95):
    pfeil((bx + bw, y), (wx - 0.03, y), WAERME)
box(14.75, 4.7, 2.4, 1.6, "Load", ["buildings + grid losses", "5,462 MWh/a"], fc="#ececec")
pfeil((wx + 0.03, 5.5), (14.75, 5.5), WAERME)
box(14.75, 2.5, 2.4, 1.6, "District grid", ["fixed from F|Heat,", "costs only"], ls="--")
ax.plot([15.95, 15.95], [4.1, 4.7], color="black", lw=0.8, ls=":")

# ---------------- legend ----------------
ax.plot([0.3, 17.05], [-0.15, -0.15], color="black", lw=0.6)
neben = [
    r"Area: $2.3\,A + V/2.65 \leq A_\mathrm{free}$ (13,000 m²)",
    r"Storage parts: $E_\mathrm{core} : E_\mathrm{zone} : E_\mathrm{cold}$ fixed",
    r"Air HP: $\dot Q(t) \leq f(T_a)\,\dot Q_\mathrm{nom}$, $f$: 1 → 0.8 at −1 … −7 °C",
    r"Stratification: $e_\mathrm{core}/E_\mathrm{core} \leq e_\mathrm{zone}/E_\mathrm{zone} \leq e_\mathrm{cold}/E_\mathrm{cold}$",
    r"Reheating: $\dot Q_\mathrm{pre}/0.75 + \alpha(t)\,\dot Q_\mathrm{dir} \leq \dot Q_\mathrm{HP} + \dot Q_\mathrm{PtH}$",
    r"Flow: $\dot V_\mathrm{ch},\ \dot V_\mathrm{dis} \leq 0.0094\,\mathrm{h}^{-1}\cdot V$",
]
for i, t in enumerate(neben):
    x = 0.45 + (i % 3) * 5.6
    y = -0.6 - (i // 3) * 0.55
    marke(x, y, i + 1)
    ax.text(x + 0.25, y, t, fontsize=KLEIN, va="center")
ax.text(0.3, -1.85,
        r"$^{\ast}$ size is optimised.   Dashed: source heat, charging from grid.   Storage heat loss "
        r"$4\cdot10^{-5}\,\mathrm{h}^{-1}$ at 60,000 m³ (higher for smaller tanks).   "
        "LP over 8760 h, perfect foresight; small network, base case.",
        fontsize=KLEIN, va="center", color=GRAU)

fig.tight_layout(pad=0.4)
out = sys.argv[1]
fig.savefig(out + ".png", dpi=170)
fig.savefig(out + ".svg")
print(out)
