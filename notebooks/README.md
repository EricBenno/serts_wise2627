# Notebooks

Nur Auswertung und Abbildungen, keine Modelllogik (die gehört nach `src/serts`).
Daten über das Paket laden, z. B.:

```python
from serts.config import load_config
from serts import demand, weather
cfg = load_config()
last = demand.waermebedarf(cfg)
T_a = weather.aussentemperatur(cfg)
```

Ausgaben vor dem Commit löschen („Clear all outputs“). Kernel: `.venv` des Repos (`uv add --dev ipykernel` bei Bedarf).
