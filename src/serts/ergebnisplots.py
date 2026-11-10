"""Grafiken zu einem Lauf: Was läuft wann, wie viel, und was deckt wann die Last?

Eingang: ``r`` (Stundenwerte aus kpi.zeitreihen_ergebnis) und ``k`` (Kennzahlen aus kpi.auswerten).
Alle Grafiken: ``alle(r, k, out_dir)``.
"""

from __future__ import annotations

from pathlib import Path

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
    """Oben: Wärmeherkunft (Tagesmittel) + Last. Mitte: Speicherinhalt heiß/kalt. Unten: Speichertemperaturen."""
    q = _quellen(r).resample("D").mean()
    fig, (a1, a2, a3) = plt.subplots(
        3, 1, figsize=(12, 9), sharex=True, gridspec_kw={"height_ratios": [2, 1, 1]}
    )
    _stapel(a1, q)
    a1.plot(q.index, r["last"].resample("D").mean(), "k", lw=1, label="Last (inkl. Netzverluste)")
    a1.set_ylabel("Wärme [MW] (Tagesmittel)")
    a1.legend(ncol=6, fontsize=8, loc="upper center")
    a1.set_title("Wer deckt wann die Last?")
    a2.stackplot(
        r.index,
        r["speicher_kalt"],
        r["speicher_heiss"],
        labels=["kalter Teil (10-45 °C, nur über WP)", "heißer Teil (45-85 °C, direkt nutzbar)"],
        colors=["#9ecae1", "#f28e2b"],
        alpha=0.8,
        linewidth=0,
    )
    a2.set_ylabel("Speicherinhalt [MWh]")
    a2.legend(fontsize=8, loc="upper left")
    if "T_speicher_oben" in r:
        a3.plot(
            r["T_speicher_oben"].resample("D").mean(),
            color="#d62728",
            lw=1.0,
            label="oben (Kennlinie, Tagesmittel)",
        )
        a3.plot(r["T_speicher_mittel"].resample("D").mean(), color="#555", lw=1.0, label="Mittel")
    if "T_direkt_noetig" in r.attrs:
        a3.axhline(
            r.attrs["T_direkt_noetig"], color="k", ls=":", lw=1, label="nötig für Direktentladung"
        )
    a3.set_ylim(0, 100)
    a3.set_ylabel("Speicher [°C]")
    a3.legend(fontsize=8, loc="upper left", ncol=3)
    for a in (a1, a2, a3):
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
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 6))
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
    a1.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3)
    a1.grid(axis="x", alpha=0.3)

    Qg = k.get("Q_geliefert_MWh", k["Q_last_MWh"])  # Wärme beim Kunden (ohne Netzverluste)
    sys_teile = {
        "Kollektor": k["kosten_a_kollektor"],
        "Speicher": k["kosten_a_speicher"],
        "Wärmepumpe": k["kosten_a_waermepumpe"],
        "PtH": k["kosten_a_pth"],
        "Strom": k["kosten_a_strom"],
        "Wärmenetz Trasse": k.get("kosten_a_netz_trasse", 0.0),
        "Hausanschl. + Übergabest.": k.get("kosten_a_netz_hausanschluss", 0.0),
    }
    gas_teile = {
        "Kessel": k["gas_capex_a"],
        "Gas": k["gas_brennstoffkosten_a"],
        "CO₂": k["gas_co2_kosten_a"],
        "Wärmenetz Trasse": k.get("kosten_a_netz_trasse", 0.0),
        "Hausanschl. + Übergabest.": k.get("kosten_a_netz_hausanschluss", 0.0),
    }
    farbe = {
        "Kollektor": "#f2c12e",
        "Speicher": "#f28e2b",
        "Wärmepumpe": "#4e79a7",
        "PtH": "#e15759",
        "Strom": "#76b7b2",
        "Wärmenetz Trasse": "#bab0ac",
        "Hausanschl. + Übergabest.": "#d9d3cf",
        "Kessel": "#9c755f",
        "Gas": "#b07aa1",
        "CO₂": "#59595c",
    }
    gesehen = set()
    if "lcoh_inkl_netz_bew" in k:
        h = k["lcoh_inkl_netz_bew"]
        a2.bar(2, h, color="#8cd17d", edgecolor="w", width=0.6, label="mit BEW Modul 2 (gesamt)")
        a2.text(2, h + 2, f"{h:.0f} €/MWh", ha="center", fontweight="bold")
        zuschuss = k["zuschuss_bew_EUR"] / 1e6
        a2.text(2, h / 2, f"Zuschuss\n{zuschuss:.1f} Mio. €", ha="center", fontsize=8)
    for x, teile in [(0, sys_teile), (1, gas_teile)]:
        unten = 0.0
        for name, v in teile.items():
            h = v / Qg
            lab = f"{name}" if name not in gesehen else None
            gesehen.add(name)
            a2.bar(x, h, bottom=unten, color=farbe[name], edgecolor="w", label=lab, width=0.6)
            if h > 6:
                a2.text(x, unten + h / 2, f"{name} {h:.0f}", ha="center", va="center", fontsize=8)
            unten += h
        a2.text(x, unten + 2, f"{unten:.0f} €/MWh", ha="center", fontweight="bold")
    a2.set_ylim(0, a2.get_ylim()[1] * 1.12)
    a2.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=4)
    if "lcoh_inkl_netz_bew" in k:
        a2.set_xticks(
            [0, 1, 2], ["Solar + PTES + WP + PtH", "Gas-Referenz", "System mit BEW\n(max. 40 %)"]
        )
    else:
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
