#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Trojx(饶建勋) on 2025/1/3
from typing import List, Dict
from abc import ABC, abstractmethod


class BaseStorage(ABC):
    @abstractmethod
    def store_account_info(self, account_data: Dict):
        """
        存储账号信息
        :param account_data: 账号信息字典
        """
        pass

    @abstractmethod
    def store_article(self, article_data: Dict):
        """
        存储文章数据
        :param article_data: 文章数据字典
        """
        pass

    @abstractmethod
    def store_comments(self, comments_data: List[Dict]):
        """
        存储文章评论数据
        :param comments_data: 评论数据列表
        """
        pass
