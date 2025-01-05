#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Trojx(饶建勋) on 2025/1/3
import csv
import os

from store.base_storage import BaseStorage
from utils import logger

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "./data")


class CSVStorage(BaseStorage):
    def __init__(self, base_dir=DATA_DIR):
        """
        初始化存储路径
        :param base_dir: 数据存储的根目录
        """
        self.base_dir = base_dir
        logger.debug(f"__init__ base_dir:{base_dir}")
        os.makedirs(self.base_dir, exist_ok=True)

    def store_account_info(self, account_info):
        """
        存储账号信息
        :param account_info: 账号信息
        """
        file_path = os.path.join(self.base_dir, "accounts.csv")
        is_new_file = not os.path.exists(file_path)

        with open(file_path, mode="a", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=account_info.keys())
            if is_new_file:
                writer.writeheader()
            writer.writerow(account_info)

        logger.debug(f"账号信息已存储到 {file_path}")

    def store_article(self, article_data):
        """
        将文章数据存储到 CSV 文件
        :param article_data: 文章数据字典
        """
        if not article_data:
            logger.debug(f"store_article: empty article_data.")
            return
        file_path = os.path.join(self.base_dir, "articles.csv")
        is_new_file = not os.path.exists(file_path)

        with open(file_path, mode='a', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=article_data.keys())
            if is_new_file:
                writer.writeheader()  # 写入表头
            writer.writerow(article_data)

        logger.debug(f"文章数据已存储到 {file_path}")

    def store_comments(self, comments_data):
        """
        将评论数据存储到 CSV 文件
        :param comments_data: 评论数据列表
        """
        if not comments_data or len(comments_data) < 1:
            logger.debug(f"store_comments: empty data.")
            return
        file_path = os.path.join(self.base_dir, "comments.csv")
        is_new_file = not os.path.exists(file_path)

        with open(file_path, mode='a', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=comments_data[0].keys())
            if is_new_file:
                writer.writeheader()  # 写入表头
            writer.writerows(comments_data)

        logger.debug(f"评论数据已存储到 {file_path}")
