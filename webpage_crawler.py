import time

import requests
import random
import argparse

from bs4 import BeautifulSoup, Comment
from utils import logger, filter_object_fields
import config
from store.storage_factory import StorageFactory

UA_LIST = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .\
            NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; InfoPath.3)', ]


def _is_good_resp(resp):
    """
    判断文章网页链接请求结果是否有效，可以进行解析
    """
    if resp.status_code == 200:
        content = resp.content.decode('utf-8', 'ignore')
        return True
    else:
        return False


def get_article_list(column_id, page_size=20):
    """
    获取指定账号的全部文章列表
    :param column_id: 账号 ID
    :param page_size: 每页获取的文章数，默认为 20
    :return: 所有文章的列表
    """
    base_url = "https://nfplusapi.nfnews.com/nfplus-manuscript-web/article/list"
    page_num = 1
    all_articles = []

    while True:
        # 构造请求参数
        params = {
            "nfhSubCount": 0,
            "columnId": column_id,
            "service": 0,
            "pageSize": page_size,
            "pageNum": page_num,
        }

        try:
            # 发送 GET 请求
            response = requests.get(base_url, params=params)
            response.raise_for_status()

            # 解析响应数据
            data = response.json()
            if not data.get("success", False):
                logger.error(f"请求失败，错误信息: {data.get('msg', '未知错误')}")
                break

            article_data = data.get("data", {})
            articles = article_data.get("list", [])

            # 添加文章到结果列表
            if articles and len(articles) > 0:
                for article in articles:
                    # 只保留必要的字段
                    filtered_article = filter_object_fields(article, ['articleId', 'title', 'copyright', 'summary',
                                                                      'releaseTime', 'createTime', 'updateTime',
                                                                      'articleType', 'shareUrl', 'source',
                                                                      'countDiscuss', 'countLike',
                                                                      'columnName', 'columnId', 'columnDesc',
                                                                      'picMiddle'])
                    all_articles.append(filtered_article)
                logger.debug(f"第 {page_num} 页获取成功，共 {len(articles)} 篇文章")
            else:
                logger.debug("没有更多文章")
                break

            # 检查是否还有下一页
            if not article_data.get("hasNextPage", False):
                logger.debug("已到最后一页")
                break

            # 下一页
            page_num += 1

        except requests.RequestException as e:
            logger.error(f"请求失败: {e}")
            break

    logger.info(f"获取完成，共获取到 {len(all_articles)} 篇文章")
    return all_articles


def get_all_article_comments(article_id, page_size=20):
    """
    获取指定文章的全部评论
    :param article_id: 文章 ID
    :param page_size: 每页评论数，默认为 20
    :return: 所有评论的列表
    """
    logger.debug(f"开始获取文章 {article_id} 的所有评论")

    all_comments = []  # 存储所有评论
    page_num = 1  # 初始页码
    has_next_page = True

    while has_next_page:
        # 构造请求 URL 和参数
        url = "https://nfplusapi.nfnews.com/nfplus-cmt-web/buildStyle/cmt/moreCommentList"
        params = {
            "articleId": article_id,
            "pageNum": page_num,
            "pageSize": page_size,
        }
        headers = {
            'User-Agent': random.choice(UA_LIST),
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }

        # 发送请求
        try:
            resp = requests.get(url, headers=headers, params=params, allow_redirects=False)
            resp.raise_for_status()
            data = resp.json()  # 转换为 JSON 数据

            # 验证返回状态
            if not data.get("success", False) or data.get("code") != 200:
                logger.error(f"接口返回错误: {data.get('msg', '未知错误')}")
                break

            # 提取评论数据
            comment_data = data.get("data", {})
            new_comments = comment_data.get("newComment", [])

            if not new_comments:
                logger.debug("没有更多评论，停止获取")
                break  # 如果没有新评论，则停止分页

            # 添加新评论到结果列表
            for new_comment in new_comments:
                all_comments.append({
                    "cmtId": new_comment['cmtId'],
                    "parentId": new_comment['parentId'],
                    "username": new_comment['username'],
                    "likeCount": new_comment['likeCount'],
                    "userUuid": new_comment['userUuid'],
                    "portraitUrl": new_comment['portraitUrl'],
                    "cmtContent": new_comment['cmtContent'],
                    "articleId": new_comment['articleId'],
                    "createTime": new_comment['createTime'],
                    "ipLocation": new_comment['ipLocation'],
                    "rootCmtId": new_comment['rootCmtId'],
                    "subCmtCount": new_comment['subCmtCount'],
                })

            logger.debug(f"第 {page_num} 页评论获取成功，共 {len(new_comments)} 条")

            # 检查是否有下一页
            has_next_page = comment_data.get("hasNextPage", False)
            if not has_next_page:
                logger.debug("已到最后一页")
                break

            page_num += 1  # 下一页

            time.sleep(1)  # 间隔
        except Exception as e:
            logger.error(f"获取评论时出错: {e}")
            break

    logger.debug(f"获取完成，共获取到 {len(all_comments)} 条评论")
    return all_comments


def parse_article_page(url):
    """
    解析文章网页内容
    :param url: 网页链接
    :return:
    """
    logger.debug("parse_article_page: url={}".format(url))
    resp = requests.get(url, headers={
        'User-Agent': random.choice(UA_LIST),
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
    }, allow_redirects=False)

    MAX_RETRY_TIMES = 5
    retry_time = 0
    while (not _is_good_resp(resp)) and retry_time < MAX_RETRY_TIMES:
        time_to_sleep = 30
        logger.error(
            "parse_article_page: sleep {}s until next request, retry_time={}.".format(time_to_sleep, retry_time))
        time.sleep(time_to_sleep)
        retry_time += 1
        resp = requests.get(url, headers={
            'User-Agent': random.choice(UA_LIST),
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        })

    title = ''
    author = ''
    is_original = False
    pub_date = ''
    article_id = ''
    address = ''
    keyword = ''  # 关键字
    avatar = ''  # 所属公众号头像
    cover_url = ''  # 封面图片
    content_text = ''  # 正文文本

    if resp.status_code == 200:
        content = resp.content.decode('utf-8', 'ignore')
        # logger.debug("content: {}".format(content))
        soup = BeautifulSoup(content, 'html5lib')
        # print(soup.prettify())

        title = soup.find(attrs={'id': 'articleTitle'}).text.strip()
        author = soup.find(name='meta', attrs={"name": "author"}).get("content")
        is_original = soup.find(name='meta', attrs={"name": "Copyright"}).get("content") != "0"
        avatar = soup.find(name='img', attrs={"class": "colimg"}).get("src")
        pub_date = soup.find(name='div', attrs={"class": "nfhtime pubtime"}).get("data-time")
        address = soup.find(name='meta', attrs={"name": "location"}).get("content")

        # 查找所有注释内容
        comments = soup.find_all(string=lambda text: isinstance(text, Comment))
        for comment in comments:
            if "enpproperty" in comment:  # 查找包含 "enpproperty" 的注释
                # 将注释内容解析为新的 BeautifulSoup 对象
                metadata_soup = BeautifulSoup(comment, "html5lib")
                article_id = metadata_soup.find("articleid").text if metadata_soup.find("articleid") else None
                title = metadata_soup.find("title").text if metadata_soup.find("title") else None
                keyword = metadata_soup.find("keyword").text if metadata_soup.find("keyword") else None
                cover_url = metadata_soup.find("picurl").text if metadata_soup.find("picurl") else None
                break

        # 正文文本
        rich_media_content = soup.find(attrs={'class': 'article'})
        if rich_media_content:
            content_text = rich_media_content.text

        return {
            'title': title,
            'is_original': is_original,
            'author': author,
            'pub_date': pub_date,
            'article_id': article_id,
            'address': address,
            'keyword': keyword,
            'avatar': avatar,
            'cover_url': cover_url,
            'content_text': content_text,
        }
    else:
        return None


def get_account_info(account):
    """
    获取账号信息
    :param account: 南方号名称
    :return:
    """
    # 固定参数
    base_url = "https://api.nfnews.com/nanfang_if/searchInSign/classifiedSearch"
    fixed_params = {"pageIndex": 1, "origin": 3, "pageSize": 20, "location": "guangzhou",
                    "deviceId": config.API_DEVICEID, "userId": "", "indexType": 0,
                    "sortType": "time", "classifiedType": -1, "sign": config.API_SIGN,
                    "secretCanChanged": "true", "keyword": account}

    # 将关键字加入参数
    try:
        # 发送请求
        response = requests.get(base_url, params=fixed_params)
        response.raise_for_status()  # 检查响应状态码

        # 解析响应数据
        data = response.json()

        # 检查接口返回结果
        if not data.get("success", False) or data.get("code") != 200:
            logger.error(f"接口返回错误: {data.get('msg', '未知错误')}")
            return None

        # 提取 nfh 数组中的账号信息
        nfh_accounts = data.get("data", {}).get("nfh", [])
        for account_info in nfh_accounts:
            if account_info.get("columnName") == account:
                logger.debug(f"找到完全匹配的账号信息: {account_info}")
                return account_info

        logger.warning(f"未找到与关键字 '{account}' 完全匹配的账号信息")
        return None

    except requests.RequestException as e:
        logger.error(f"获取账号信息时发生错误: {e}")
        return None


def main():
    # 配置命令行参数解析
    parser = argparse.ArgumentParser(description="南方号文章爬取与存储脚本")
    parser.add_argument("-a", "--account", type=str, help="账号名称（例如: 中山大学）")
    parser.add_argument("-c", "--column_id", type=int, help="账号 ID")
    args = parser.parse_args()

    account_name = args.account
    column_id = args.column_id

    # 参数校验
    if not account_name and not column_id:
        parser.error("必须提供 --account 或 --column_id 参数中的一个")

    # 初始化存储实例
    storage = StorageFactory.get_storage()

    # 如果提供了账号名称，则先获取账号信息
    if account_name:
        account_info = get_account_info(account_name)
        if not account_info:
            logger.error(f"未找到与 '{account_name}' 对应的账号信息")
            return
        # 保存账号信息
        storage.store_account_info(account_info)
        column_id = account_info['columnId']  # 从账号信息中提取 columnId

    # 爬取文章列表
    article_list = get_article_list(column_id=column_id)
    for article in article_list:
        # 保存文章
        storage.store_article(article)
        comments = get_all_article_comments(article_id=article['articleId'])
        # 保存文章评论
        storage.store_comments(comments)

    logger.info("任务完成！")


if __name__ == '__main__':
    main()
