"""Zentrale Übersicht der wichtigsten Eingangsparameter -> docs/eingangsparameter.md.

Aus der Config erzeugt (Single Source of Truth = YAML), Netz klein und groß nebeneinander.
Die vollständige Liste aller Parameter steht in docs/annahmen.md (``serts annahmen``).

Zeile = (Parameter-Pfad, Beschriftung, Faktor, Einheit). Faktor/Einheit nur, wenn die Anzeige von der
Config-Einheit abweicht (z. B. EUR/MWh -> ct/kWh).
"""

from __future__ import annotations

from serts import economics
from serts.config import Config, load_config

Zeile = tuple[str, str, float, str | None]

GRUPPEN: list[tuple[str, list[Zeile]]] = [
    (
        "1 Netz und Standort",
        [
            ("standort.flaeche_verfuegbar", "Freifläche (Kollektor + Speicher)", 1, None),
            ("last.Q_gebaeude", "Wärmebedarf Gebäude", 1, None),
            ("last.Q_netzverlust", "Netzverluste (Standarddämmung)", 1, None),
            ("last.P_max_kontrolle", "Spitzenlast inkl. Verluste (Stundenwert)", 1, None),
            ("netz.trassenlaenge", "Trassenlänge", 1, None),
            ("netz.hausanschluesse", "Hausanschlüsse", 1, None),
            ("netz.T_VL", "Vorlauftemperatur", 1, None),
            ("netz.T_RL", "Rücklauftemperatur (Modell)", 1, None),
            ("zeit.wetterjahr", "Wetter-/Lastjahr (Temperatur DWD 03028)", 1, None),
        ],
    ),
    (
        "2 Energiepreise und Emissionen (netto, real)",
        [
            ("strom.tarif", "Strom: Tarif (fest oder day_ahead)", 1, None),
            ("strom.preis_fest", "Strom gesamt (fester Tarif)", 0.1, "ct/kWh"),
            ("strom.netzentgelt", "  davon Netzentgelt (Arbeitspreis)", 0.1, "ct/kWh"),
            ("strom.abgaben", "  davon Steuern/Abgaben/Umlagen", 0.1, "ct/kWh"),
            ("strom.vertriebsmarge", "Day-Ahead-Tarif: Vertriebsmarge", 0.1, "ct/kWh"),
            ("strom.preisjahr", "Day-Ahead-Tarif: Preisjahr", 1, None),
            ("strom.emissionsfaktor", "Strom: CO2-Faktor", 1000, "g/kWh"),
            ("gas_referenz.gaspreis", "Erdgas (Brennwert Hs, ohne CO2-Preis)", 0.1, "ct/kWh"),
            ("gas_referenz.co2_preis", "CO2-Preis (ETS)", 1, None),
            ("gas_referenz.emissionsfaktor", "Erdgas: CO2-Faktor (Hi)", 1000, "g/kWh"),
            ("biomasse.brennstoffkosten", "Biomasse (Option, nicht im Basisfall)", 0.1, "ct/kWh"),
        ],
    ),
    (
        "3 Wirtschaftlichkeit (VDI 2067-1)",
        [
            ("oekonomie.zins", "Kalkulationszins (real)", 100, "%"),
            ("oekonomie.betrachtungszeitraum", "Betrachtungszeitraum", 1, None),
            ("oekonomie.preisbasisjahr", "Preisbasis", 1, None),
            ("oekonomie.nebenkosten", "Planungs-/Nebenkosten auf alle Investitionen", 100, "%"),
            ("oekonomie.foerderquote", "Förderquote in der Optimierung (Basis ohne)", 100, "%"),
            ("oekonomie.bew_ausweis_quote", "BEW Modul 2: Ausweis je Lauf (Obergrenze)", 100, "%"),
            ("oekonomie.preisaenderung.strom", "Preisänderung Strom (real)", 100, "%/a"),
            ("oekonomie.preisaenderung.gas", "Preisänderung Gas (real)", 100, "%/a"),
            ("oekonomie.preisaenderung.co2", "Preisänderung CO2 (real)", 100, "%/a"),
        ],
    ),
    (
        "4 Investitionen und Lebensdauern (netto; Quelle: KWW Technikkatalog 2026, wo vermerkt)",
        [
            ("kollektor.kosten_spez", "Kollektorfeld (Brutto-Fläche)", 1, None),
            ("oekonomie.lebensdauer.kollektor", "  Lebensdauer", 1, None),
            ("ptes.kosten_ref", "PTES bei 60.000 m3 (Kostenkurve, siehe unten)", 1, None),
            ("ptes.kosten_exponent", "  Größenexponent spez. Kosten", 1, None),
            ("oekonomie.lebensdauer.ptes", "  Lebensdauer", 1, None),
            ("waermepumpe.kosten_spez", "Wärmepumpe (Luft + Speicher)", 0.001, "EUR/kW_th"),
            ("oekonomie.lebensdauer.waermepumpe", "  Lebensdauer", 1, None),
            ("pth.kosten_spez", "Power-to-Heat (Reserve)", 0.001, "EUR/kW_th"),
            ("oekonomie.lebensdauer.pth", "  Lebensdauer", 1, None),
            ("gas_referenz.kosten_spez", "Gaskessel (nur Gas-Referenz)", 0.001, "EUR/kW_th"),
            ("oekonomie.lebensdauer.gaskessel", "  Lebensdauer", 1, None),
            ("netz.kosten_trasse_strasse", "Trasse unter Straße", 1, None),
            ("netz.kosten_trasse_gruen", "Trasse Grünfläche", 1, None),
            ("netz.anteil_strasse", "  Anteil Straße an der Trasse", 100, "%"),
            ("oekonomie.lebensdauer.netz", "  Lebensdauer Trasse", 1, None),
            ("netz.kosten_hausanschluss", "Hausanschluss inkl. Übergabestation", 1, None),
            ("oekonomie.lebensdauer.hausanschluss", "  Lebensdauer", 1, None),
        ],
    ),
    (
        "5 Technik (Wirkungsgrade, Temperaturen, Verluste)",
        [
            ("kollektor.eta0", "Kollektor: Konversionsfaktor eta0", 1, None),
            ("kollektor.neigung", "Kollektor: Neigung (Süd)", 1, None),
            ("kollektor.flaechenfaktor", "Grundfläche je Kollektor-Bruttofläche", 1, None),
            ("kollektor.feldverluste", "Kollektor: Feld-/Rohrverluste", 100, "%"),
            ("ptes.T_oben", "PTES: max. Temperatur", 1, None),
            ("ptes.T_unten", "PTES: min. Temperatur", 1, None),
            ("ptes.verlustrate", "PTES: Wärmeverlust (Speicherinhalt)", 1, None),
            (
                "ptes.uebergang_ref",
                "PTES: Übergangszone bei 60.000 m³ (Anteil am heißen Teil)",
                100,
                "%",
            ),
            ("ptes.volumen_je_grundflaeche", "PTES: Volumen je Grundfläche", 1, None),
            (
                "waermepumpe.cop_ansatz_luft",
                "Luft-WP: COP-Ansatz (KWW: Gütegrad x Carnot auf Vorlauf)",
                1,
                None,
            ),
            (
                "waermepumpe.guetegrad_faktor",
                "Luft-WP: Faktor auf KWW-Gütegrad (45 % bei 80 °C)",
                1,
                None,
            ),
            ("waermepumpe.COP_ptes", "Speicher-WP: COP", 1, None),
            ("waermepumpe.luft_leistung_bei_tmin", "Luft-WP: Leistung bei -7 °C (Anteil)", 1, None),
            ("pth.eta", "PtH: Wirkungsgrad", 1, None),
            ("pth.redundanz", "PtH: Reserve (x Spitzenlast)", 1, None),
            ("gas_referenz.eta", "Gaskessel: Wirkungsgrad (Hi)", 1, None),
        ],
    ),
]

PTES_STUETZ = (2_000, 10_000, 20_000, 60_000, 100_000)
KWW_PTES = {20_000: 90, 50_000: 70, 100_000: 60, 200_000: 50}


def _fmt(v: float | str | bool) -> str:
    if isinstance(v, bool):
        return "ja" if v else "nein"
    if isinstance(v, str):
        return v
    if 1900 < v < 2100 and float(v).is_integer():  # Jahreszahl
        return str(int(v))
    return f"{v:,.0f}".replace(",", ".") if abs(v) >= 100 else f"{v:.4g}".replace(".", ",")


def _kurz(text: str, n: int = 95) -> str:
    text = (text or "").replace("|", "/").replace("\n", " ")
    if len(text) <= n:
        return text
    for trenner in ("; ", " ("):  # an einer sinnvollen Stelle kürzen
        if trenner in text[:n]:
            return text[: text.rindex(trenner, 0, n)] + " …"
    kurz = text[: n - 1].rstrip()
    if kurz.count("(") > kurz.count(")"):
        kurz = kurz[: kurz.rindex("(")].rstrip()
    return kurz + " …"


def _wert(cfg: Config, pfad: str, faktor: float) -> str:
    v = cfg.get_optional(pfad)
    if v is None:
        return "**offen**"
    return _fmt(v * faktor if isinstance(v, (int, float)) and not isinstance(v, bool) else v)


def uebersicht_markdown(klein: Config | None = None, gross: Config | None = None) -> str:
    klein = klein or load_config(netz="klein")
    gross = gross or load_config(netz="gross")
    zeilen = [
        "# Zentrale Eingangsparameter",
        "",
        "> Automatisch erzeugt aus `config/base.yaml` und `config/netze/*.yaml` mit `uv run serts uebersicht`.",
        "> Nicht von Hand ändern: Zahlen in der YAML anpassen, Übersicht neu erzeugen. Alle Parameter mit "
        "Quellen: [annahmen.md](annahmen.md).",
        "",
        f"Szenario: **{klein.name}**"
        + (f" / **{gross.name}** (groß)" if gross.name != klein.name else "")
        + '. "=" heißt: im großen Netz gleicher Wert '
        "wie im kleinen. Status: **B** belegt (Quelle/Messwert), **V** Vorgabe (Teamentscheidung), "
        "**A** Annahme (begründet, ohne Primärquelle). Kosten netto in EUR, real, Preisbasis 2025/26.",
        "",
    ]
    for titel, rows in GRUPPEN:
        zeilen += [
            f"## {titel}",
            "",
            "| Parameter | klein | groß | Einheit | St. | Quelle |",
            "|---|---|---|---|---|---|",
        ]
        for pfad, label, faktor, einheit_neu in rows:
            node = klein.node(pfad)
            einheit = einheit_neu or node.get("einheit", "")
            a = _wert(klein, pfad, faktor)
            b = _wert(gross, pfad, faktor)
            status = node["status"][0].upper()
            if gross.node(pfad)["status"] != node["status"]:
                status += "/" + gross.node(pfad)["status"][0].upper()
            if a != b:
                quelle = (
                    f"klein: {_kurz(node.get('quelle'), 45)}; groß: "
                    f"{_kurz(gross.node(pfad).get('quelle'), 45)}"
                )
            else:
                quelle = _kurz(node.get("quelle") or "")
            zeilen.append(
                f"| {label} | {a} | {'=' if a == b else b} | {einheit.replace('|', '/')} | {status} | "
                f"{quelle} |"
            )
        zeilen.append("")

    zeilen += [
        "## 6 Abgeleitet: spezifische PTES-Kosten (Kostenkurve des Modells)",
        "",
        "Kosten je m3 Wasseräquivalent (Preisindex und `ptes.kosten_faktor` eingerechnet). Die Kurve folgt dem "
        "KWW-Fit Invest = 1093,6 x V^0,7472; Stützwerte des KWW: "
        + ", ".join(f"{v:,.0f} m3 = {c} EUR/m3".replace(",", ".") for v, c in KWW_PTES.items())
        + ". Unter 20.000 m3 ist die Kurve **extrapoliert** (KWW-Gültigkeit 20.000-200.000 m3).",
        "",
        "| Volumen [m3] | " + " | ".join(f"{v:,.0f}".replace(",", ".") for v in PTES_STUETZ) + " |",
        "|---|" + "---|" * len(PTES_STUETZ),
        "| Kosten [EUR/m3] | "
        + " | ".join(f"{economics.ptes_kosten_je_m3(klein, v):.0f}" for v in PTES_STUETZ)
        + " |",
        "",
        "Nicht übernommen aus dem KWW: Kollektor- und Speichererträge/-verluste (eigene Rechnung mit PVGIS-"
        "Normaljahr und Speichermodell). Solar-O&M (1 % des Invests, KWW) und weitere Instandhaltungssätze "
        "stehen in `oekonomie.om_fix.*` ([annahmen.md](annahmen.md)).",
        "",
    ]
    return "\n".join(zeilen)
