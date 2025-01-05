import re
import sys
import ctypes

# import win32gui
import os
import subprocess
from datetime import datetime, timedelta
import socket
import uuid

# 获取主机名称+MAC地址作为 CLIENT_ID
CLIENT_ID = socket.gethostname() + "-" + hex(uuid.getnode())

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
project_name = "app_crawler"

current_path = os.path.abspath(os.path.dirname(__file__))
root_path = current_path[:current_path.find(project_name) + len(project_name)]
logfile = os.path.join(root_path, './log/client.log')
if not os.path.exists(os.path.dirname(logfile)):
    os.mkdir(os.path.dirname(logfile))


class AlignedFormatter(logging.Formatter):
    def __init__(self, max_length=30):
        """
        初始化自定义 Formatter
        :param fmt: 格式化字符串
        :param datefmt: 时间格式
        :param max_length: `filename[line:lineno]` 部分的最大长度
        """
        super().__init__(fmt='%(asctime)s %(filename_lineno)s %(levelname)s %(message)s',
                         datefmt='%Y-%m-%d %H:%M:%S')
        self.max_length = max_length

    def format(self, record):
        # 生成 `filename[line:lineno]` 部分
        filename_lineno = f"{record.filename}[line:{record.lineno}]"

        # 如果长度超过 max_length，进行头尾保留的缩略
        if len(filename_lineno) > self.max_length:
            # 计算保留的头部和尾部长度
            keep_length = (self.max_length - 3) // 2
            head = filename_lineno[:keep_length]
            tail = filename_lineno[-keep_length:]
            filename_lineno = f"{head}...{tail}"

        # 右对齐并填充空格
        record.filename_lineno = filename_lineno.ljust(self.max_length)

        return super().format(record)


# 定义日志格式
formatter = AlignedFormatter()

# 打印日志到log文件
fileHandler = logging.FileHandler(logfile, encoding='utf-8')
fileHandler.setLevel(logging.DEBUG)
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)

# 同时打印日志到terminal
streamHandler = logging.StreamHandler()
streamHandler.setLevel(logging.DEBUG)
streamHandler.setFormatter(formatter)  # 设置控制台日志的格式化器
logger.addHandler(streamHandler)


# logger.addHandler(streamHandler)


# def get_window_classname(window_title):
#     hwnd = win32gui.FindWindow(None, window_title)
#     if hwnd != 0:
#         className = win32gui.GetClassName(hwnd)
#         return className
#     else:
#         return None


def getCoding(strInput):
    '''
    获取编码格式
    '''
    try:
        strInput.decode("utf8")
        return 'utf8'
    except:
        pass
    try:
        strInput.decode("gbk")
        return 'gbk'
    except:
        return "unicode"


def gbk_to_utf8(gbk_string):
    if getCoding(gbk_string) == 'gbk':
        return gbk_string.decode('gbk').encode('utf-8')
    return gbk_string


def convert_count_text_to_number(count_text):
    """
    将形如“10万+”的数字描述转换为数字
    :param count_text:
    :return:
    """
    counts = re.findall(r"\d+\.?\d*", count_text)
    if len(counts) > 0:
        count = counts[0]
        if "10万+" == count_text:
            return 100001
        if "万" in count_text:
            return int(10000 * float(count))
        else:
            return int(count)
    return 0


def split_list(input_list, max_length=10):
    """
    使用列表推导式将列表分割成多个子列表，每个子列表长度不超过 max_length
    """
    return [input_list[i:i + max_length] for i in range(0, len(input_list), max_length)]


def open_file(file_path):
    """
    用默认应用程序打开指定文件
    """
    if sys.platform.startswith('win'):
        os.startfile(file_path)
    elif sys.platform.startswith('darwin'):
        subprocess.call(["open", file_path])
    else:
        subprocess.call(["xdg-open", file_path])


class QTextEditLogger(logging.Handler):
    def __init__(self, text_edit):
        super().__init__()
        self.text_edit = text_edit

    def emit(self, record):
        msg = self.format(record)
        self.text_edit.append(msg)  # 将日志消息添加到文本框
        self.text_edit.verticalScrollBar().setValue(self.text_edit.verticalScrollBar().maximum())  # 自动滚动到最底部


def parse_date(text):
    # 获取今天的日期
    today = datetime.today()

    # 处理 "今天"、"昨天" 等相对时间
    if text == "今天":
        return today.strftime("%Y-%m-%d")
    elif text == "昨天":
        return (today - timedelta(days=1)).strftime("%Y-%m-%d")

    # 处理星期几，如 "星期一" 到 "星期日"
    weekdays = {
        "星期一": 0,
        "星期二": 1,
        "星期三": 2,
        "星期四": 3,
        "星期五": 4,
        "星期六": 5,
        "星期日": 6
    }
    if text in weekdays:
        today_weekday = today.weekday()  # 获取今天是星期几 (0 = Monday, 6 = Sunday)
        target_weekday = weekdays[text]
        delta_days = (today_weekday - target_weekday) % 7
        # 如果目标日期是今天，delta_days 需要设为7以便回到上一个相同的星期几
        if delta_days == 0:
            delta_days = 7
        return (today - timedelta(days=delta_days)).strftime("%Y-%m-%d")

    # 处理类似 "9月1日" 的日期，省略年份，表示今年
    match = re.match(r"(\d{1,2})月(\d{1,2})日", text)
    if match:
        month = int(match.group(1))
        day = int(match.group(2))
        return datetime(today.year, month, day).strftime("%Y-%m-%d")

    # 处理 "2019年9月1日" 的日期
    match = re.match(r"(\d{4})年(\d{1,2})月(\d{1,2})日", text)
    if match:
        year = int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))
        return datetime(year, month, day).strftime("%Y-%m-%d")

    return None  # 如果无法匹配任何模式，则返回 None


def ellipsize_article(article):
    """
    缩略显示article字典数据，因为正文字段可能太长，影响log观看
    :param article:
    :return:
    """
    article_copy = article.copy()
    max_length = 20
    if 'content_text' in article_copy:
        if len(article_copy['content_text']) > max_length:
            article_copy['content_text'] = article_copy['content_text'][:max_length] + "..."

    return str(article_copy)


def has_admin():
    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_admin


def get_client_id():
    return CLIENT_ID


def filter_object_fields(obj, fields):
    """
    提取对象中的指定字段
    :param obj: 数据对象，可以是字典或具有属性的对象
    :param fields: 需要保留的字段名列表
    :return: 仅包含指定字段的字典
    """
    if isinstance(obj, dict):
        # 如果是字典，从字典中提取字段
        return {field: obj.get(field, None) for field in fields}
    else:
        # 如果是对象，从对象属性中提取字段
        return {field: getattr(obj, field, None) for field in fields}


if __name__ == '__main__':
    # print(get_window_classname("订阅号"))

    print(convert_count_text_to_number("10万+"))
    print(convert_count_text_to_number("1.3万"))
    print(convert_count_text_to_number("7.0万"))
    print(convert_count_text_to_number("5687"))
    print(get_client_id())
