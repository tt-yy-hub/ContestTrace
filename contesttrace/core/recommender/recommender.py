#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
推荐引擎模块
实现基于用户画像的关键词匹配和标签权重的推荐
"""

import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ContestRecommender:
    """
    竞赛推荐引擎
    """
    
    def __init__(self, user_profile_path: str = "data/user_profile.json"):
        """
        初始化推荐引擎
        
        Args:
            user_profile_path: 用户画像保存路径
        """
        self.user_profile_path = user_profile_path
        self.user_profile = self._load_user_profile()
    
    def _load_user_profile(self) -> dict:
        """
        加载用户画像
        
        Returns:
            用户画像字典
        """
        try:
            profile_path = Path(self.user_profile_path)
            if profile_path.exists():
                with open(profile_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # 默认用户画像
                return {
                    'keywords': {},  # 关键词权重
                    'tags': {},      # 标签权重
                    'categories': {} # 分类权重
                }
        except Exception as e:
            logger.error(f"加载用户画像失败: {e}")
            return {
                'keywords': {},
                'tags': {},
                'categories': {}
            }
    
    def _save_user_profile(self):
        """
        保存用户画像
        """
        try:
            # 确保目录存在
            profile_dir = Path(self.user_profile_path).parent
            profile_dir.mkdir(parents=True, exist_ok=True)
            
            with open(self.user_profile_path, 'w', encoding='utf-8') as f:
                json.dump(self.user_profile, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存用户画像失败: {e}")
    
    def update_user_profile(self, contest: dict, feedback: int = 1):
        """
        更新用户画像
        
        Args:
            contest: 竞赛信息字典
            feedback: 反馈值，1表示正反馈，-1表示负反馈
        """
        try:
            # 更新关键词权重
            for keyword in contest.get('keywords', []):
                self.user_profile['keywords'][keyword] = self.user_profile['keywords'].get(keyword, 0) + feedback
            
            # 更新标签权重
            for tag in contest.get('tags', []):
                self.user_profile['tags'][tag] = self.user_profile['tags'].get(tag, 0) + feedback
            
            # 更新分类权重
            category = contest.get('category', '其他竞赛')
            self.user_profile['categories'][category] = self.user_profile['categories'].get(category, 0) + feedback
            
            # 保存用户画像
            self._save_user_profile()
        except Exception as e:
            logger.error(f"更新用户画像失败: {e}")
    
    def recommend(self, contests: list, top_n: int = 10) -> list:
        """
        推荐竞赛
        
        Args:
            contests: 竞赛信息列表
            top_n: 推荐数量
        
        Returns:
            推荐的竞赛列表
        """
        try:
            # 计算每个竞赛的推荐分数
            scored_contests = []
            for contest in contests:
                score = self._calculate_score(contest)
                scored_contests.append((contest, score))
            
            # 按分数排序，返回前top_n个
            scored_contests.sort(key=lambda x: x[1], reverse=True)
            recommended_contests = [contest for contest, score in scored_contests[:top_n]]
            
            logger.info(f"推荐完成，共推荐 {len(recommended_contests)} 个竞赛")
            return recommended_contests
        except Exception as e:
            logger.error(f"推荐竞赛失败: {e}")
            return []
    
    def _calculate_score(self, contest: dict) -> float:
        """
        计算竞赛的推荐分数
        
        Args:
            contest: 竞赛信息字典
        
        Returns:
            推荐分数
        """
        score = 0.0
        
        # 关键词匹配分数
        for keyword in contest.get('keywords', []):
            score += self.user_profile['keywords'].get(keyword, 0) * 0.5
        
        # 标签匹配分数
        for tag in contest.get('tags', []):
            score += self.user_profile['tags'].get(tag, 0) * 0.3
        
        # 分类匹配分数
        category = contest.get('category', '其他竞赛')
        score += self.user_profile['categories'].get(category, 0) * 0.2
        
        # 截止时间分数（近的截止时间得分更高）
        days_left = contest.get('days_left', -1)
        if days_left > 0 and days_left <= 30:
            score += (30 - days_left) * 0.1
        
        return score
    
    def search(self, query: str, contests: list, top_n: int = 10) -> list:
        """
        自然语言查询
        
        Args:
            query: 查询语句
            contests: 竞赛信息列表
            top_n: 返回数量
        
        Returns:
            查询结果列表
        """
        try:
            # 简单的关键词匹配
            query_words = query.lower().split()
            matched_contests = []
            
            for contest in contests:
                # 构建竞赛文本
                contest_text = (
                    contest.get('title', '').lower() + ' ' +
                    contest.get('content', '').lower() + ' ' +
                    ' '.join(contest.get('keywords', [])).lower() + ' ' +
                    ' '.join(contest.get('tags', [])).lower()
                )
                
                # 计算匹配度
                match_score = 0
                for word in query_words:
                    if word in contest_text:
                        match_score += 1
                
                if match_score > 0:
                    matched_contests.append((contest, match_score))
            
            # 按匹配度排序
            matched_contests.sort(key=lambda x: x[1], reverse=True)
            return [contest for contest, score in matched_contests[:top_n]]
        except Exception as e:
            logger.error(f"搜索竞赛失败: {e}")
            return []
