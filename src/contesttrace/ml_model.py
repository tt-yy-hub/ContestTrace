# -*- coding: utf-8 -*-
"""
机器学习文本分类封装：训练 / 保存 / 加载 / 预测。

默认使用 scikit-learn MultinomialNB + TF-IDF（经典词袋基线，参见 sklearn 文档）。
"""

from __future__ import annotations

import csv
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import joblib
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.pipeline import Pipeline
except Exception:  # pragma: no cover
    joblib = None
    TfidfVectorizer = None
    MultinomialNB = None
    Pipeline = None


def _build_pipeline() -> Any:
    """构造 TF-IDF + 多项式朴素贝叶斯管道。"""

    if Pipeline is None:
        raise RuntimeError("scikit-learn 未安装")
    return Pipeline(
        [
            ("tfidf", TfidfVectorizer(max_features=8000, ngram_range=(1, 2))),
            ("clf", MultinomialNB()),
        ]
    )


def load_training_csv(path: Path) -> Tuple[List[str], List[str]]:
    """读取训练 CSV：列 text, label（竞赛/非竞赛 等）。"""

    texts: List[str] = []
    labels: List[str] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                t = (row.get("text") or "").strip()
                lb = (row.get("label") or "").strip()
                if t and lb:
                    texts.append(t)
                    labels.append(lb)
            except Exception:
                continue
    return texts, labels


def train_and_save(train_csv: Path, model_path: Path, logger: logging.Logger) -> bool:
    """从 CSV 训练并保存 joblib 模型。"""

    try:
        texts, labels = load_training_csv(train_csv)
        if len(texts) < 5:
            logger.warning("训练样本过少（<5），跳过训练")
            return False
        model = _build_pipeline()
        model.fit(texts, labels)
        model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, model_path)
        logger.info(f"模型已保存：{model_path}")
        return True
    except Exception as e:
        logger.warning(f"模型训练失败：{type(e).__name__}: {e}")
        return False


def load_model(model_path: Path, logger: logging.Logger) -> Optional[Any]:
    """加载模型；失败返回 None。"""

    try:
        if not model_path.exists() or joblib is None:
            return None
        return joblib.load(model_path)
    except Exception as e:
        logger.warning(f"模型加载失败：{e}")
        return None


def predict_competition(model: Any, text: str) -> Optional[str]:
    """预测标签字符串。"""

    try:
        if model is None or not text.strip():
            return None
        return str(model.predict([text])[0])
    except Exception:
        return None
