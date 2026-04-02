# -*- coding: utf-8 -*-
"""从 data/training_data/*.csv 训练竞赛分类模型到 data/models/competition_nb.joblib"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from contesttrace.config_center import load_config  # noqa: E402
from contesttrace.ml_model import train_and_save  # noqa: E402
from contesttrace.utils import ensure_dir, setup_logger  # noqa: E402


def main() -> None:
    cfg = load_config()
    logger = setup_logger(cfg.paths.logs_dir)
    ensure_dir(cfg.paths.models_dir)
    csv_path = cfg.paths.training_dir / "sample_labeled.csv"
    model_path = cfg.paths.models_dir / "competition_nb.joblib"
    train_and_save(csv_path, model_path, logger)


if __name__ == "__main__":
    main()
