#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Trojx(饶建勋) on 2025/1/3
from typing import Type
from config import STORAGE_TYPE
from store.base_storage import BaseStorage
from store.csv_storage import CSVStorage


class StorageFactory:
    _instance: BaseStorage = None  # 单例实例

    @staticmethod
    def get_storage() -> BaseStorage:
        """
        获取存储实例（单例模式）
        :return: 存储类实例
        """
        if StorageFactory._instance is None:
            # 动态创建存储实例
            if STORAGE_TYPE == "CSVStorage":
                StorageFactory._instance = CSVStorage()
            else:
                raise ValueError(f"未知的存储类型: {STORAGE_TYPE}")

        return StorageFactory._instance
