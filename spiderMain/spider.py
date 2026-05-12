from selenium import webdriver
from pymysql import *
import pandas as pd
from sqlalchemy import create_mock_engine, create_engine
import time
import re
import csv
import os
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException


def spider_fn(key):

    def init():
        if os.path.exists('./data.csv'):
            os.remove('./data.csv')
        with open('./data.csv', 'a', encoding='utf-8', newline='') as f:
            myWrite = csv.writer(f)
            myWrite.writerow(['type', 'title', 'price', 'buy_len', 'img_src',
                              'name', 'address', 'isFreeDelivery', 'href', 'nameHref'])

    def search_product(key):
        broswer.find_element(By.ID, "q").send_keys(key)
        broswer.find_element(By.XPATH, '//*[@id="button"]').click()
        time.sleep(5)

    def scroll_to_load():
        """分段滚动，确保所有懒加载内容（包括中间区域）都能加载完成"""
        last_height = broswer.execute_script("return document.body.scrollHeight")
        scroll_step = 800  # 每次滚动800像素（约一个屏幕高度）
        current_position = 0
        max_attempts = 30  # 防止无限循环
        attempt = 0
        # 先滚动到顶部，确保从最上面开始
        broswer.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)

        while attempt < max_attempts:
            # 向下滚动一段距离
            current_position += scroll_step
            broswer.execute_script(f"window.scrollTo(0, {current_position});")
            time.sleep(1.5)  # 等待新内容加载

            # 检查是否已到达底部
            new_height = broswer.execute_script("return document.body.scrollHeight")
            if current_position >= new_height:
                # 已经到底部，再滚动一次确保最底部内容加载
                broswer.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                # 再次检查高度是否变化
                final_height = broswer.execute_script("return document.body.scrollHeight")
                if final_height == new_height:
                    break
                else:
                    # 高度变化了，继续滚动
                    current_position = new_height - scroll_step
                    new_height = final_height

            # 防止死循环（如果高度长时间不变且没到底，也可能是网络慢，多等一次）
            if new_height == last_height and current_position >= new_height:
                break
            last_height = new_height
            attempt += 1

        # 最后再平滑滚动到底部一次，确保所有内容都触发
        broswer.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    def parse_sales(sales_text):
        if not sales_text:
            return 0
        match = re.search(r'(\d+(?:\.\d+)?)\s*万', sales_text)
        if match:
            return int(float(match.group(1)) * 10000)
        match = re.search(r'\d+', sales_text)
        if match:
            return int(match.group())
        return 0

    def find_next_button():
        """尽量兼容淘宝翻页按钮变化，找不到时返回 None，避免打印 Selenium Stacktrace。"""
        candidate_xpaths = [
            '//*[@id="search-content-leftWrap"]//button[.//span[contains(text(), "下一页")] or contains(normalize-space(.), "下一页")]',
            '//*[@id="search-content-leftWrap"]//button[contains(@aria-label, "下一页")]',
            '//button[.//span[contains(text(), "下一页")] or contains(normalize-space(.), "下一页")]',
            '//button[contains(@aria-label, "下一页")]',
        ]

        for xpath in candidate_xpaths:
            buttons = broswer.find_elements(By.XPATH, xpath)
            for button in buttons:
                try:
                    if button.is_displayed():
                        return button
                except WebDriverException:
                    continue
        return None

    def is_button_disabled(button):
        class_name = button.get_attribute('class') or ''
        disabled_attr = button.get_attribute('disabled')
        aria_disabled = button.get_attribute('aria-disabled')
        return bool(disabled_attr) or aria_disabled == 'true' or 'disabled' in class_name.lower()

    def get_product(count):
        total = count
        page_count = 0                # 已翻页次数（已处理页数）
        max_pages = 5                 # 最多爬取5页（可自行修改）
        limit_per_page = 35           # 每页最多提取30条数据

        while True:
            # 获取当前页所有商品卡片
            items = broswer.find_elements(By.XPATH, '//*[@id="content_items_wrapper"]/div')
            # 本页最多取前 limit_per_page 条
            items_to_extract = items[:limit_per_page] if len(items) > limit_per_page else items

            for div in items_to_extract:
                try:
                    total = total + 1
                    # 类型
                    product_type = key
                    # 商品名
                    title = div.find_element(By.XPATH, './/div[contains(@class, "title")]/span').text
                    # 价格
                    price = div.find_element(By.XPATH, './/div[contains(@class, "priceInt")]').text + \
                            div.find_element(By.XPATH, './/div[contains(@class, "priceFloat")]').text
                    # 销量
                    sales_text = div.find_element(By.XPATH, './/span[contains(@class, "realSales")]').text
                    buy_len = parse_sales(sales_text)
                    # 商品图片
                    img_src = div.find_element(By.XPATH, './/img[contains(@class, "mainPic")]').get_attribute('src')
                    # 店铺
                    name = div.find_element(By.XPATH, './/span[contains(@class, "shopNameText")]').text
                    # 地址
                    address_spans = div.find_elements(By.XPATH, './/div[contains(@class, "procity")]/span')
                    address_parts = [span.text.strip() for span in address_spans if span.text.strip()]
                    address = ' '.join(address_parts)
                    # 包邮情况
                    isFreeDeliveryList = div.find_elements(By.XPATH, './/span[text()="包邮"]')
                    isFreeDelivery = "包邮" if len(isFreeDeliveryList) > 0 else "不包邮"
                    # 详情链接
                    href = div.find_element(By.XPATH, './/a[contains(@class, "doubleCardWrapperAdapt")]').get_attribute('href')
                    # 店铺详情
                    nameHref = div.find_element(By.XPATH, './/a[contains(@class, "shopName")]').get_attribute('href')
                    print(title)
                    save_to_csv(product_type, title, price, buy_len, img_src, name, address, isFreeDelivery, href, nameHref)
                    # print(f"类型：{product_type}\n商品名：{title}\n价格：{price}\n销量: {buy_len}\n店铺：{name}\n地址: {address}\n包邮: {isFreeDelivery}\n商品图片：{img_src}\n详情链接：{href}\n店铺详情：{nameHref}")
                    if total % 10 == 0:
                        print('已爬取%d条数据了' % total)

                except Exception as e:
                    total = total - 1
                    print(f"提取商品失败，已跳过当前商品：{e.__class__.__name__}")
                    continue

            # 本页提取完成，打印提示
            extracted_this_page = len(items_to_extract)
            print(f"\n本页共提取 {extracted_this_page} 条数据，累计已提取 {total} 条")

            # 翻页控制：每提取完一页（达到x条或不足x条）就尝试翻页
            page_count += 1
            if page_count >= max_pages:
                print(f"已达到最大页数 {max_pages}，抓取结束")
                break

            # 尝试翻到下一页：找不到按钮时只打印简短提示，不再输出 Selenium Stacktrace
            try:
                next_btn = find_next_button()
                if next_btn is None:
                    print("没有找到下一页按钮，可能已到最后一页或页面结构发生变化，抓取结束")
                    break

                if is_button_disabled(next_btn):
                    print("下一页按钮不可用，已是最后一页，抓取结束")
                    break

                broswer.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
                time.sleep(1)
                try:
                    next_btn.click()
                except WebDriverException:
                    broswer.execute_script("arguments[0].click();", next_btn)

                print(f"正在翻页到第 {page_count + 1} 页...")
                time.sleep(5)
                scroll_to_load()  # 翻页后滚动加载新页面商品
                continue
            except Exception:
                print("翻页失败，抓取结束")
                break

    def main():
        init()
        count = 0
        search_product(key)
        scroll_to_load()
        get_product(count)
        save_to_sql()

    def save_to_csv(product_type, title, price, buy_len, img_src, name, address, isFreeDelivery, href, nameHref):
        with open('./data.csv', 'a', encoding='utf-8', newline='') as f:
            myWriter = csv.writer(f, dialect='excel', delimiter=',')
            myWriter.writerow([product_type, title, price, buy_len, img_src, name, address, isFreeDelivery, href, nameHref])

    def save_to_sql():
        products = pd.read_csv('./data.csv')
        df = pd.DataFrame(products)
        df = df_clean(df)  # 此时 df 中只有原有列，address 被替换为省份
        conn = create_engine('mysql+pymysql://root:root@localhost:3306/commodity_data?charset=utf8')
        df.to_sql('products', con=conn, index=False, if_exists='append')
        print("已成功导入数据库")

    def df_clean(df):
        # 提取地址的第一个词（省份）
        df['address'] = df['address'].str.split().str[0]
        # 如果提取后为空或 NaN，填充为 '暂无'
        df['address'] = df['address'].fillna('暂无')
        # 不再新增 address_province 列
        return df

    main()

if __name__ == '__main__':
    service = Service('C:\Program Files\Google\Chrome\Application/chromedriver.exe')
    options = webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", "localhost:9223")
    broswer = webdriver.Chrome(service=service, options=options)
    broswer.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument',
                            {'source': 'Object.defineProperty(navigator,"webdriver",{get:()=>undefined})'})
    broswer.get('https://s.taobao.com/search')
    spider_fn('家具')