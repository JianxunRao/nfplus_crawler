import uiautomator2 as u2
import time
import os
from utils import logger
from webpage_crawler import parse_article_page, get_all_article_comments
from store.storage_factory import StorageFactory
from store.base_storage import BaseStorage

DATA_PATH = os.path.join(os.path.dirname(__file__), './data')
os.makedirs(DATA_PATH, exist_ok=True)


class NfplusCrawler:
    def __init__(self, device_ip=None):
        # 连接设备
        self.device = u2.connect(device_ip) if device_ip else u2.connect()
        self.app_package = "com.nfdaily.nfplus"

        # 当前爬取的账号名称
        self.account = ''

    def start_app(self):
        """启动南方plus应用"""
        # 启动之前先停止
        self.device.app_stop(self.app_package)

        self.device.app_start(self.app_package)
        time.sleep(1)

        skip_button = self.device(text="跳过")
        if skip_button.exists:
            logger.debug(f"点击'跳过'")
            skip_button.click()

        logger.debug(f"应用 {self.app_package} 启动")

    def stop_app(self):
        """停止南方plus应用"""
        self.device.app_stop(self.app_package)
        logger.debug(f"应用 {self.app_package} 已停止")

    def is_on_home_page(self):
        """检查当前是否在应用主页"""
        # 判断条件可以根据实际情况调整，例如判断某个特定控件是否存在
        home_element = self.device(resourceId="com.nfdaily.nfplus:id/logo_image")  # 你可以根据主页元素的 resourceId 来判断
        return home_element.exists

    def go_back_to_home(self):
        """模拟按返回按钮直到返回到应用主页"""
        for _ in range(5):
            self.device.press('back')
            time.sleep(1)  # 等待返回操作完成
            if self.is_on_home_page():  # 判断是否已经回到主页
                logger.debug("已成功返回到主页")
                return
        logger.warning("无法返回到主页")

    def swipe_left_on_element(self, element):
        """
        在特定控件范围内向左滑动
        :param element: 目标控件
        """
        if not element.exists:
            raise Exception("控件不存在")

        # 获取控件边界
        bounds = element.info['bounds']
        logger.debug(f"swipe_left_on_element: bounds={bounds}")
        start_x = bounds['right'] // 2  # 按住中间开始向左滑，防止触发屏幕边缘的全面屏手势
        end_x = bounds['left']  # 控件的左边界
        y = (bounds['top'] + bounds['bottom']) // 2  # 控件的垂直中心

        # 执行滑动操作
        self.device.swipe(start_x, y, end_x, y, steps=10)

    def swipe_vertical(self, start_ratio=0.6, end_ratio=0.4, steps=2):
        """
        手动纵向上下滑动屏幕
        :param start_ratio: 起始点相对于屏幕高度的比例
        :param end_ratio: 结束点相对于屏幕高度的比例
        :param steps: 滑动的步数，值越大滑动越慢
        """
        screen_width, screen_height = self.device.window_size()
        start_x = screen_width // 2
        start_y = int(screen_height * start_ratio)
        end_y = int(screen_height * end_ratio)

        self.device.swipe(start_x, start_y, start_x, end_y, steps=steps)
        logger.debug(f"swipe_vertical: start_y {start_y} -> end_y {end_y}")

    def get_clipboard_content(self):
        """
        获取剪贴板中的内容
        :return: 剪贴板内容
        """
        clipboard_content = self.device.clipboard  # 获取剪贴板内容
        if clipboard_content:
            logger.debug(f"get_clipboard_content: {clipboard_content}")
            return clipboard_content
        else:
            logger.error(f"get_clipboard_content: 剪贴板为空")
            return ''

    def open_account_profile(self, account):
        """
        进入账号主页
        :param account: 账号名称
        :return:
        """

        self.account = account

        # 先返回主页
        self.go_back_to_home()

        # 点击顶部搜索框，输入关键字
        search_box = self.device(resourceId="com.nfdaily.nfplus:id/search_content_view")
        if search_box.exists:
            search_box.click()
            search_box.set_text(account)
            time.sleep(1)
        else:
            raise Exception("搜索输入框未找到")

        # 点击搜索按钮
        search_button = self.device(resourceId="com.nfdaily.nfplus:id/right_btn")
        if search_button.exists:
            search_button.click()
        else:
            raise Exception("未找到'搜索'按钮")

        # 点击搜索结果中的指定项
        search_result = self.device(text=account, resourceId="com.nfdaily.nfplus:id/tv_name",
                                    className="android.widget.TextView")
        if search_result.wait(timeout=10):  # 动态等待
            search_result.click()
        else:
            logger.error(f"搜索结果中未找到 '{account}'")
            raise Exception

    def parse_account_profile(self):
        """
        解析账号主页中的信息
        :return:
        """

        # 解析账号头像
        logo_element = self.device(resourceId="com.nfdaily.nfplus:id/logo")
        if not logo_element.wait(timeout=5):
            raise Exception("未找到头像控件")
        try:
            logo_image = logo_element.screenshot()  # 返回 PIL.Image 对象
            logo_path = os.path.join(DATA_PATH, self.account + ".png")
            logo_image.save(logo_path)
            print(f"头像图片已直接保存到 {logo_path}")
        except Exception as e:
            raise Exception(f"保存头像图片时出错: {e}")

        # 解析账号名称
        account_element = self.device(resourceId="com.nfdaily.nfplus:id/sub_name")
        if not account_element.wait(timeout=5):
            raise Exception("未找到名称控件")
        account_name = account_element.get_text()
        if self.account != account_name:
            raise Exception("账号名称不一致")

        # 解析账号简介
        desc_element = self.device(resourceId="com.nfdaily.nfplus:id/sub_description")
        if not desc_element.wait(timeout=5):
            raise Exception("未找到简介控件")
        desc = desc_element.get_text()

        logger.debug(f"parse_account_profile: logo_path:{logo_path},account_name:{account_name},desc:{desc}")

    def parse_articles(self):
        """
        解析文章列表并逐个点击获取详情
        """
        recycler_view = self.device(resourceId="com.nfdaily.nfplus:id/recyclerView")
        if not recycler_view.exists:
            raise Exception("未找到文章列表")

        parsed_articles = set()
        while True:
            articles = recycler_view.child(resourceId="com.nfdaily.nfplus:id/ll_item_root")

            for article_item in articles:
                # 获取文章标题
                title = article_item.child(resourceId="com.nfdaily.nfplus:id/adapter_news_title").get_text()

                if title in parsed_articles:
                    logger.debug(f"parse_articles: 已解析过：{title}")
                    continue

                # 标记文章为已解析
                parsed_articles.add(title)

                # 打印文章标题
                logger.info(f"parse_articles: {title}")

                # 点击文章并解析详情
                article_item.click()
                time.sleep(2)
                self.parse_article_details()

                # 返回上一页
                time.sleep(1)
                back_button = self.device(resourceId="com.nfdaily.nfplus:id/view_btn_left")
                if back_button.exists:
                    back_button.click()
                    time.sleep(1)
                    logger.debug(f"parse_articles: press back")
                else:
                    raise Exception(f"parse_articles: 返回按钮不存在！")

            # 滑动到下一页
            self.swipe_vertical()
            time.sleep(2)

    def parse_article_details(self):
        """
        解析文章详情页内容
        """
        logger.info(f"parse_article_details: start.")

        # 点击"更多"按钮，复制文章链接
        more_button = self.device(resourceId="com.nfdaily.nfplus:id/view_btn_more")
        more_button.click(timeout=2)
        share_listview = self.device(resourceId="com.nfdaily.nfplus:id/share_list_view")
        # 向左滑动列表，让按钮显示出来
        self.swipe_left_on_element(share_listview)
        time.sleep(1)  # 等待滑动完成，再点击按钮，防止点错位置
        link_button = share_listview.child(className="android.widget.TextView", text="复制链接")
        link_button.click(timeout=5)

        # 复制获得文章链接
        time.sleep(2)
        article_url = self.get_clipboard_content()

        # 从网页解析文章内容
        article_data = parse_article_page(article_url)
        # logger.debug(f"parse_article_details: article_data={article_data}")

        # 获取文章评论
        article_comments = get_all_article_comments(article_id=article_data['article_id'])
        # logger.debug(f"parse_article_details: article_comments={article_comments}")

        # 保存数据
        store: BaseStorage = StorageFactory.get_storage()
        store.store_article(article_data)
        store.store_comments(article_comments)

        logger.info(f"parse_article_details: end.")


if __name__ == "__main__":
    crawler = NfplusCrawler()
    crawler.start_app()
    crawler.open_account_profile(account="中山大学")
    crawler.parse_account_profile()
    crawler.parse_articles()
