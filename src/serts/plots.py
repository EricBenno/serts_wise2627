"""Standardplots. Nur Darstellung, keine Berechnungslogik."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
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
        "PTES direkt": r["entladen_direkt"],
        "WP aus PTES": r["wp_waerme_ptes"],
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
        a2.set(ylabel="PTES-Inhalt [MWh] (bez. 10 °C)", xlabel="")
    for a in (a1, a2):
        a.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def heatmap_lcoh(df: pd.DataFrame, out: Path) -> Path:
    """LCOH über A_spez x V/A; Rasterpunkte über der verfügbaren Fläche schraffiert (x)."""
    piv = df.pivot(index="V_pro_A", columns="A_spez", values="lcoh")
    ok = df.pivot(index="V_pro_A", columns="A_spez", values="flaeche_ok")
    fig, ax = plt.subplots(figsize=(8, 4.5))
    im = ax.imshow(piv.to_numpy(), origin="lower", aspect="auto", cmap="viridis_r")
    ax.set_xticks(range(len(piv.columns)), [f"{c:g}" for c in piv.columns])
    ax.set_yticks(range(len(piv.index)), [f"{i:g}" for i in piv.index])
    for i in range(piv.shape[0]):
        for j in range(piv.shape[1]):
            val = piv.iat[i, j]
            mark = "" if bool(ok.iat[i, j]) else " ×"
            ax.text(j, i, f"{val:.0f}{mark}", ha="center", va="center", fontsize=8, color="w")
    ax.set(
        xlabel="Kollektorfläche [m² je MWh/a Einspeisung]",
        ylabel="PTES-Volumen [m³/m² Kollektor]",
        title="LCOH [€/MWh] (× = Fläche > verfügbar)",
    )
    fig.colorbar(im, ax=ax, label="LCOH [€/MWh]")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def pareto(df: pd.DataFrame, out: Path) -> Path:
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for ok, marker, lab in [(True, "o", "Fläche ok"), (False, "x", "Fläche überschritten")]:
        d = df[df["flaeche_ok"] == ok]
        sc = ax.scatter(
            d["ee_anteil"] * 100,
            d["lcoh"],
            c=d["V_pro_A"],
            marker=marker,
            cmap="plasma",
            vmin=df["V_pro_A"].min(),
            vmax=df["V_pro_A"].max(),
            label=lab,
        )
    if "gas_lcoh" in df:
        ax.axhline(df["gas_lcoh"].iloc[0], color="grey", ls="--", label="Gas-Referenz")
    ax.set(xlabel="Erneuerbaren-Anteil [%]", ylabel="LCOH [€/MWh]")
    fig.colorbar(sc, ax=ax, label="V/A [m³/m²]")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
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
