#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机器学习辅助分类模块
实现基于文本特征的竞赛分类
"""

import os
import json
from pathlib import Path
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

logger = logging.getLogger(__name__)


class ContestClassifier:
    """
    竞赛分类器
    """
    
    def __init__(self, model_path: str = "data/classifier_model.json"):
        """
        初始化分类器
        
        Args:
            model_path: 模型保存路径
        """
        self.model_path = model_path
        self.pipeline = None
        self.categories = ['学科竞赛', '技能竞赛', '创业竞赛', '文体竞赛', '其他竞赛']
        self._load_model()
    
    def _load_model(self):
        """
        加载模型
        """
        try:
            # 简单的分类模型，使用TF-IDF和朴素贝叶斯
            self.pipeline = Pipeline([
                ('tfidf', TfidfVectorizer(analyzer='char', ngram_range=(1, 2))),
                ('clf', MultinomialNB())
            ])
            logger.info("分类模型初始化成功")
        except Exception as e:
            logger.error(f"加载分类模型失败: {e}")
            self.pipeline = None
    
    def train(self, X: list, y: list):
        """
        训练分类模型
        
        Args:
            X: 特征列表（文本）
            y: 标签列表
        """
        try:
            if not self.pipeline:
                self._load_model()
            
            # 分割训练集和测试集
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # 训练模型
            self.pipeline.fit(X_train, y_train)
            
            # 评估模型
            y_pred = self.pipeline.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            logger.info(f"模型训练完成，准确率: {accuracy:.2f}")
            
            # 保存模型（简化版，实际项目中可以使用joblib或pickle）
            self._save_model()
        except Exception as e:
            logger.error(f"训练模型失败: {e}")
    
    def predict(self, text: str) -> str:
        """
        预测分类
        
        Args:
            text: 文本内容
        
        Returns:
            预测的分类
        """
        try:
            if not self.pipeline:
                self._load_model()
            
            # 预测
            prediction = self.pipeline.predict([text])
            return prediction[0]
        except Exception as e:
            logger.error(f"预测分类失败: {e}")
            return '其他竞赛'
    
    def _save_model(self):
        """
        保存模型
        """
        try:
            # 确保目录存在
            model_dir = Path(self.model_path).parent
            model_dir.mkdir(parents=True, exist_ok=True)
            
            # 简化版模型保存，实际项目中可以使用joblib或pickle
            with open(self.model_path, 'w', encoding='utf-8') as f:
                json.dump({'categories': self.categories}, f, ensure_ascii=False)
            logger.info("模型保存成功")
        except Exception as e:
            logger.error(f"保存模型失败: {e}")
    
    def classify_contest(self, contest: dict) -> str:
        """
        对竞赛进行分类
        
        Args:
            contest: 竞赛信息字典
        
        Returns:
            分类结果
        """
        try:
            # 构建特征文本
            text = contest.get('title', '') + ' ' + contest.get('content', '')
            if not text:
                return '其他竞赛'
            
            # 预测分类
            category = self.predict(text)
            return category
        except Exception as e:
            logger.error(f"分类竞赛失败: {e}")
            return '其他竞赛'
