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


### 1.账号信息
![账号信息](http://c.trojx.com/PicGo/20250105165535911.png)

### 2.文章数据
![文章数据](http://c.trojx.com/PicGo/20250105165700253.png)

### 3.评论数据
![评论数据](http://c.trojx.com/PicGo/20250105165801587.png)

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

## 许可证
本项目基于 MIT License 进行开源。

## 免责声明

本项目仅用于学习和研究目的，禁止将本程序用于任何违反相关法律法规或侵犯他人合法权益的活动。使用本程序爬取数据时，请务必遵守以下规则：

1. **数据合法性**：
   - 确保您已获得目标网站的授权或在目标网站允许的范围内进行爬取。
   - 请勿爬取涉及隐私、敏感或受版权保护的数据。

2. **资源消耗**：
   - 请合理设置爬取频率，避免对目标网站服务器造成过大压力或影响其正常运行。

3. **数据用途**：
   - 爬取的数据仅限个人学习或研究使用，未经目标网站或数据所有者授权，不得将爬取的数据用于商业或其他用途。

4. **风险承担**：
   - 使用本程序产生的一切后果，由使用者自行承担，作者不对任何因使用本程序导致的直接或间接损失负责。
