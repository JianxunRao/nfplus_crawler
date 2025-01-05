# 南方Plus 爬虫工具

[![License](https://img.shields.io/badge/license-MIT-green)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/)
[![Last Commit](https://img.shields.io/github/last-commit/JianxunRao/nfplus_crawler)](https://github.com/JianxunRao/nfplus_crawler/commits/main)
[![Issues](https://img.shields.io/github/issues/JianxunRao/nfplus_crawler)](https://github.com/JianxunRao/nfplus_crawler/issues)
[![Stars](https://img.shields.io/github/stars/JianxunRao/nfplus_crawler)](https://github.com/JianxunRao/nfplus_crawler/stargazers)

## 简介

本项目是一个基于 Python 的爬虫工具，旨在从南方Plus平台中自动化获取账号信息、文章内容及其评论，并支持将数据存储为 CSV 文件或其他形式。

主要功能包括：

- **账号搜索**：根据账号名称或 ID 搜索并获取账号信息。
- **文章爬取**：获取指定账号的全部文章列表。
- **评论爬取**：爬取文章的全部评论数据。
- **数据存储**：支持将爬取的数据存储为 CSV 文件。

---

## 安装指南

### 1. 克隆仓库

```bash
git clone https://github.com/JianxunRao/nfplus_crawler.git
cd nfplus_crawler
```

### 2. 创建虚拟环境并安装依赖
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 使用方法

### 1. 通过账号名称爬取
```bash
python webpage_crawler.py -a 中山大学
```

### 2. 通过账号 ID 爬取
```bash
python webpage_crawler.py -c 1356
```

### 3. 可选参数
- `--account` (`-a`)：指定要爬取的账号名称。
- `--column_id` (`-c`)：指定要爬取的账号 ID。

参数必须至少提供一个；如果 --account 和 --column_id 同时提供，以 --account 优先。

