"""
Loads config/kpi_targets.yaml and gives later modules (anomaly detection,
forecasting) a one-line way to check a result against the agreed targets,
instead of every notebook hardcoding its own threshold.

Usage:
    from kpi_targets import load_targets, check_forecast, check_anomaly_detection

    targets = load_targets()
    ok, msg = check_forecast(mape=9.4, targets=targets)
    print(msg)   # "PASS: MAPE 9.4% <= target 12%"
"""

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "config" / "kpi_targets.yaml"


def load_targets(path: Path = CONFIG_PATH) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"KPI config not found at {path}")
    with open(path) as f:
        return yaml.safe_load(f)


def check_forecast(mape: float, targets: dict) -> tuple[bool, str]:
    target = targets["forecasting"]["mape_target_pct"]
    stretch = targets["forecasting"]["mape_stretch_pct"]
    if mape <= stretch:
        return True, f"STRETCH MET: MAPE {mape:.1f}% <= stretch {stretch}%"
    if mape <= target:
        return True, f"PASS: MAPE {mape:.1f}% <= target {target}%"
    return False, f"FAIL: MAPE {mape:.1f}% > target {target}%"


def check_anomaly_detection(precision: float, recall: float, targets: dict) -> tuple[bool, str]:
    p_target = targets["anomaly_detection"]["precision_target_pct"]
    r_target = targets["anomaly_detection"]["recall_target_pct"]
    p_ok = precision >= p_target
    r_ok = recall >= r_target
    status = "PASS" if (p_ok and r_ok) else "FAIL"
    return (p_ok and r_ok), (
        f"{status}: precision {precision:.1f}% (target {p_target}%), "
        f"recall {recall:.1f}% (target {r_target}%)"
    )


if __name__ == "__main__":
    targets = load_targets()
    print("Loaded KPI targets:")
    print(f"  Forecasting  -> MAPE target {targets['forecasting']['mape_target_pct']}%, "
          f"stretch {targets['forecasting']['mape_stretch_pct']}%")
    print(f"  Anomaly det. -> precision >= {targets['anomaly_detection']['precision_target_pct']}%, "
          f"recall >= {targets['anomaly_detection']['recall_target_pct']}%")
