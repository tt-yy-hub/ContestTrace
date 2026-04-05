#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
推荐模块初始化文件
"""

from .classifier import ContestClassifier
from .recommender import ContestRecommender

__all__ = [
    'ContestClassifier',
    'ContestRecommender'
]
