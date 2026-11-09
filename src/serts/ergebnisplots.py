"""Grafiken zu einem Lauf: Was läuft wann, wie viel, und was deckt wann die Last?

Eingang: ``r`` (Stundenwerte aus kpi.zeitreihen_ergebnis) und ``k`` (Kennzahlen aus kpi.auswerten).
Alle Grafiken: ``alle(r, k, out_dir)``.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

# Wärmequellen am Netz: Spalte -> (Beschriftung, Farbe). Reihenfolge = Stapelreihenfolge.
QUELLEN = {
    "solar_direkt": ("Solar direkt", "#f2c12e"),
    "entladen_direkt": ("Speicher direkt", "#f28e2b"),
    "wp_waerme_speicher": ("WP aus Speicher", "#59a14f"),
    "wp_waerme_luft": ("WP Luft", "#4e79a7"),
    "pth_waerme": ("PtH", "#e15759"),
}


def _quellen(r: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({k: r[k] for k in QUELLEN if k in r})


def _stapel(ax, df: pd.DataFrame) -> None:
    ax.stackplot(
        df.index,
        *[df[c] for c in df.columns],
        labels=[QUELLEN[c][0] for c in df.columns],
        colors=[QUELLEN[c][1] for c in df.columns],
        linewidth=0,
    )


def jahresverlauf(r: pd.DataFrame, out: Path) -> Path:
    """Oben: Wärmeherkunft (Tagesmittel, gestapelt) + Last. Unten: Speicherinhalt + Außentemperatur."""
    q = _quellen(r).resample("D").mean()
    fig, (a1, a2) = plt.subplots(
        2, 1, figsize=(12, 7), sharex=True, gridspec_kw={"height_ratios": [2, 1]}
    )
    _stapel(a1, q)
    a1.plot(q.index, r["last"].resample("D").mean(), "k", lw=1, label="Last (inkl. Netzverluste)")
    a1.set_ylabel("Wärme [MW] (Tagesmittel)")
    a1.legend(ncol=6, fontsize=8, loc="upper center")
    a1.set_title("Wer deckt wann die Last?")
    a2.fill_between(
        r.index, r["speicherinhalt"], color="#f28e2b", alpha=0.4, label="Speicherinhalt"
    )
    a2.set_ylabel("Speicherinhalt [MWh]")
    if "T_a" in r:
        a3 = a2.twinx()
        a3.plot(
            r["T_a"].resample("D").mean(), color="grey", lw=0.8, label="Außentemp. (Tagesmittel)"
        )
        a3.set_ylabel("T_a [°C]")
        a3.legend(fontsize=8, loc="upper right")
    a2.legend(fontsize=8, loc="upper left")
    for a in (a1, a2):
        a.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def typwochen(r: pd.DataFrame, out: Path) -> Path:
    """Stundenwerte in drei typischen Wochen: kälteste Woche, Übergang (April), Sommer (Juli)."""
    wochenlast = r["last"].resample("W-MON").mean()
    kalt = wochenlast.idxmax()
    wochen = {
        f"Kälteste Woche (ab {kalt:%d.%m.})": (kalt, kalt + pd.Timedelta(days=7)),
        "Übergang (April)": (
            pd.Timestamp(f"{r.index[0].year}-04-11"),
            pd.Timestamp(f"{r.index[0].year}-04-18"),
        ),
        "Sommer (Juli)": (
            pd.Timestamp(f"{r.index[0].year}-07-11"),
            pd.Timestamp(f"{r.index[0].year}-07-18"),
        ),
    }
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    ymax = float(r["last"].max()) * 1.15
    for ax, (titel, (a, b)) in zip(axes, wochen.items(), strict=True):
        w = r.loc[a:b]
        _stapel(ax, _quellen(w))
        ax.plot(w.index, w["last"], "k", lw=1.2, label="Last")
        ax.plot(w.index, w["laden"], color="#b07aa1", lw=1, ls="--", label="Speicher laden (Solar)")
        ax.set(title=titel, ylabel="MW", ylim=(0, max(ymax, float(w["laden"].max()) * 1.1)))
        ax.grid(alpha=0.3)
    axes[0].legend(ncol=7, fontsize=7, loc="upper center")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def dauerlinie(r: pd.DataFrame, out: Path) -> Path:
    """Jahresdauerlinie der Last; jede Stunde zeigt, welche Quelle sie gedeckt hat."""
    reihenfolge = r["last"].sort_values(ascending=False).index
    q = _quellen(r).loc[reihenfolge].reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.stackplot(
        np.arange(len(q)),
        *[q[c] for c in q.columns],
        labels=[QUELLEN[c][0] for c in q.columns],
        colors=[QUELLEN[c][1] for c in q.columns],
        linewidth=0,
    )
    ax.plot(np.arange(len(q)), r["last"].loc[reihenfolge].to_numpy(), "k", lw=1, label="Last")
    ax.set(
        xlabel="Stunden im Jahr, nach Last sortiert",
        ylabel="MW",
        title="Geordnete Jahresdauerlinie mit Deckungsbeitrag je Quelle",
    )
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def teppich(r: pd.DataFrame, out: Path) -> Path:
    """Tag x Stunde: wann läuft welche Anlage? (Leistung in MW)."""
    spalten = [
        ("wp_waerme_luft", "WP Luft"),
        ("wp_waerme_speicher", "WP aus Speicher"),
        ("solar_direkt", "Solar direkt"),
        ("laden", "Speicher laden"),
        ("entladen_direkt", "Speicher direkt"),
        ("pth_waerme", "PtH"),
    ]
    fig, axes = plt.subplots(len(spalten), 1, figsize=(12, 2.0 * len(spalten)), sharex=True)
    for ax, (c, titel) in zip(axes, spalten, strict=True):
        s = r[c]
        mat = s.groupby([s.index.dayofyear, s.index.hour]).mean().unstack().T
        im = ax.imshow(
            mat.to_numpy(),
            aspect="auto",
            origin="lower",
            cmap="magma_r",
            extent=(1, mat.shape[1] + 1, 0, 24),
        )
        ax.set_ylabel("Uhrzeit")
        ax.set_yticks([0, 6, 12, 18, 24])
        ax.set_title(f"{titel} (MW, Summe {s.sum():,.0f} MWh)", fontsize=9, loc="left")
        fig.colorbar(im, ax=ax, pad=0.01)
    axes[-1].set_xlabel("Tag im Jahr (UTC)")
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    plt.close(fig)
    return out


def jahresbilanz(r: pd.DataFrame, k: dict, out: Path) -> Path:
    """Links: Wärmeherkunft im Jahr. Rechts: Kosten je MWh geliefert, System vs. Gas-Referenz."""
    q = _quellen(r).sum()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 5))
    links = 0.0
    for c, v in q.items():
        a1.barh(0, v, left=links, color=QUELLEN[c][1], label=f"{QUELLEN[c][0]}: {v:,.0f} MWh")
        if v > 0.04 * q.sum():
            a1.text(links + v / 2, 0, f"{v / q.sum():.0%}", ha="center", va="center", fontsize=9)
        links += v
    solar = k.get("Q_kollektor_MWh", 0.0)
    a1.barh(1, solar, color="#f2c12e", alpha=0.6, label=f"Kollektorertrag: {solar:,.0f} MWh")
    a1.barh(
        2,
        k.get("E_strom_MWh", 0.0),
        color="#76b7b2",
        label=f"Netzstrom: {k.get('E_strom_MWh', 0):,.0f} MWh",
    )
    a1.set_yticks([0, 1, 2], ["Wärme ans Netz", "Solarthermie", "Strombezug"])
    a1.set_xlabel("MWh/a")
    a1.set_title("Was läuft wie viel?")
    a1.legend(fontsize=8, loc="lower right")
    a1.grid(axis="x", alpha=0.3)

    Qg = k.get("Q_geliefert_MWh", k["Q_last_MWh"])  # Wärme beim Kunden (ohne Netzverluste)
    sys_teile = {
        "Kollektor": k["kosten_a_kollektor"],
        "Speicher": k["kosten_a_speicher"],
        "Wärmepumpe": k["kosten_a_waermepumpe"],
        "PtH": k["kosten_a_pth"],
        "Strom": k["kosten_a_strom"],
        "Netz": k.get("kosten_a_netz_system", 0.0),
    }
    gas_teile = {
        "Kessel": k["gas_capex_a"],
        "Gas": k["gas_brennstoffkosten_a"],
        "CO₂": k["gas_co2_kosten_a"],
        "Netz": k.get("kosten_a_netz_gasref", 0.0),
    }
    farben = plt.get_cmap("tab20").colors
    for x, teile in [(0, sys_teile), (1, gas_teile)]:
        unten = 0.0
        for i, (name, v) in enumerate(teile.items()):
            h = v / Qg
            a2.bar(x, h, bottom=unten, color=farben[(i + 4 * x) % 20], edgecolor="w")
            if h > 4:
                a2.text(x, unten + h / 2, f"{name}\n{h:.0f}", ha="center", va="center", fontsize=8)
            unten += h
        a2.text(x, unten + 2, f"{unten:.0f} €/MWh", ha="center", fontweight="bold")
    a2.set_xticks([0, 1], ["Solar + PTES + WP + PtH", "Gas-Referenz"])
    a2.set_ylabel("€ je MWh geliefert (inkl. Netz)")
    a2.set_title("Was kostet die Wärme beim Kunden? (VDI 2067, real)")
    a2.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def alle(r: pd.DataFrame, k: dict, out_dir: Path) -> list[Path]:
    return [
        jahresverlauf(r, out_dir / "1_jahresverlauf.png"),
        typwochen(r, out_dir / "2_typwochen.png"),
        dauerlinie(r, out_dir / "3_dauerlinie.png"),
        teppich(r, out_dir / "4_betrieb_tag_stunde.png"),
        jahresbilanz(r, k, out_dir / "5_jahresbilanz_kosten.png"),
    ]
