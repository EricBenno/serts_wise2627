"""Standardplots. Nur Darstellung, keine Berechnungslogik."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402


def lastgang(last: pd.DataFrame, out: Path) -> Path:
    """Tagesmittel gestapelt + geordnete Jahresdauerlinie."""
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4), gridspec_kw={"width_ratios": [2, 1]})
    cols = [c for c in ("gebaeude", "netzverlust", "ankerkunde") if last[c].abs().sum() > 0]
    last[cols].resample("D").mean().plot.area(ax=a1, linewidth=0)
    a1.set(ylabel="Leistung [MW] (Tagesmittel)", xlabel="")
    dauer = np.sort(last["gesamt"].to_numpy())[::-1]
    a2.plot(np.arange(1, len(dauer) + 1), dauer)
    a2.set(xlabel="Stunden [h]", ylabel="Leistung [MW]", title="Jahresdauerlinie")
    for a in (a1, a2):
        a.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def last_ueber_temperatur(last: pd.Series, T_a: pd.Series, out: Path) -> Path:
    fig, ax = plt.subplots(figsize=(6, 4))
    d = pd.DataFrame({"T": T_a.resample("D").mean(), "P": last.resample("D").mean()})
    ax.scatter(d["T"], d["P"], s=8)
    ax.set(xlabel="Tagesmittel Außentemperatur [°C]", ylabel="Tagesmittel Last [MW]")
    ax.set_title(f"Korrelation r = {d['T'].corr(d['P']):.2f}")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def monatsbilanz(r: pd.DataFrame, out: Path) -> Path:
    """Wärmeherkunft je Monat (gestapelt) + Speicherinhalt (Tagesmittel)."""
    quellen = {
        "Solar direkt": r["solar_direkt"],
        "Speicher direkt": r["entladen_direkt"],
        "WP aus Speicher": r["wp_waerme_speicher"],
        "WP Luft": r["wp_waerme_luft"],
        "PtH": r["pth_waerme"],
    }
    monat = pd.DataFrame(quellen).resample("MS").sum()
    last = r["last"].resample("MS").sum()
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 7), sharex=False)
    monat.index = monat.index.strftime("%b")
    monat.plot.bar(stacked=True, ax=a1, width=0.8)
    a1.plot(range(len(last)), last.to_numpy(), "k_", ms=20, mew=2, label="Last")
    a1.set(ylabel="Wärme [MWh/Monat]", xlabel="")
    a1.legend(ncol=3, fontsize=8)
    if "speicherinhalt" in r:
        r["speicherinhalt"].resample("D").mean().plot(ax=a2)
        a2.set(ylabel="Speicherinhalt [MWh]", xlabel="")
    for a in (a1, a2):
        a.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def tornado(
    df: pd.DataFrame, spalte: str, titel: str, out: Path, referenz: str | None = None
) -> Path:
    """Balken je Parameter von min bis max der Kennzahl, Basis als senkrechte Linie.

    ``df`` aus tornado.py: Zeile 'basis' + je Parameter/Wert eine Zeile.
    """
    basis = float(df.loc[df["parameter"] == "basis", spalte].iloc[0])
    var = df[df["parameter"] != "basis"].copy()
    var["delta"] = var[spalte] - basis
    # Parameter ohne Einfluss auf diese Kennzahl weglassen (z. B. Netzkosten beim Solaranteil)
    var = var[var.groupby("parameter")["delta"].transform(lambda d: d.abs().max()) > 1e-9]
    gruppen = []
    for p, g in var.groupby("parameter"):
        g = g.sort_values("wert")
        bw = float(g["basiswert"].iloc[0])
        werte = " / ".join(f"{w:g}" for w in g["wert"])
        label = f"{p}\n(Basis {bw:g}; Variante {werte})"
        # größter Ausschlag zuerst zeichnen, damit kleinere Balken sichtbar bleiben
        g = g.reindex(g["delta"].abs().sort_values(ascending=False).index)
        gruppen.append((label, bw, g))
    gruppen.sort(key=lambda x: x[2]["delta"].abs().max())

    fig, ax = plt.subplots(figsize=(9, 0.55 * len(gruppen) + 1.5))
    for i, (_label, bw, g) in enumerate(gruppen):
        for _, row in g.iterrows():
            # Farbe = Richtung der Parameteränderung (nicht der Kennzahl)
            farbe = "tab:blue" if float(row["wert"]) < bw else "tab:orange"
            ax.barh(i, row["delta"], left=basis, color=farbe, alpha=0.8, height=0.6)
            ax.text(
                basis + row["delta"],
                i,
                f" {row[spalte]:.3g} ",
                va="center",
                ha="left" if row["delta"] >= 0 else "right",
                fontsize=7,
            )
    ax.axvline(basis, color="k", lw=1)
    from matplotlib.patches import Patch

    handles = [
        Patch(color="tab:blue", alpha=0.8, label="Parameter niedriger als Basis"),
        Patch(color="tab:orange", alpha=0.8, label="Parameter höher als Basis"),
    ]
    if spalte == "lcoh" and "gas_lcoh" in df:
        gas = float(df.loc[df["parameter"] == "basis", "gas_lcoh"].iloc[0])
        handles.append(
            ax.axvline(gas, color="grey", ls="--", lw=1, label=f"Gas-Referenz {gas:.0f}")
        )
    ax.legend(handles=handles, fontsize=7, loc="lower right")
    ax.set_yticks(range(len(gruppen)), [g[0] for g in gruppen], fontsize=7)
    ax.set_xlabel(titel)
    ax.set_title(
        f"Sensitivität {titel} (Basis {basis:.3g}; Größen jeweils neu optimiert)", fontsize=9
    )
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def cop_kurve(T_a: pd.Series, cop: pd.Series, out: Path) -> Path:
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.scatter(T_a, cop, s=2)
    ax.set(xlabel="Außentemperatur [°C]", ylabel="COP Luft [-]")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out
