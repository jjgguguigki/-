import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time

# 全局缓存无头浏览器，避免重复创建
@st.cache_resource
def init_driver():
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    import subprocess, sys

    chrome_opt = Options()
    chrome_opt.add_argument("--headless=new")
    chrome_opt.add_argument("--no-sandbox")
    chrome_opt.add_argument("--disable-dev-shm-usage")
    chrome_opt.add_argument("--disable-gpu")
    chrome_opt.binary_location = subprocess.getoutput("which chromium-chromedriver")

    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_opt)
    return driver

# ====================== 网页头部UI ======================
st.set_page_config(page_title="哈夫克小说搜寻程序", page_icon="📖")
st.title("📖 哈夫克小说搜寻程序 V1.0.0")
st.subheader("天空属于哈夫克 | 技术提供：银翼")
st.divider()

# 初始化浏览器
driver = init_driver()

# 会话存储搜索结果
if "search_data" not in st.session_state:
    st.session_state.search_data = []

# ====================== 1. 小说搜索区域 ======================
bk_name = st.text_input("请输入小说名字：")
search_btn = st.button("🔍 点击搜索小说")

if search_btn and bk_name.strip():
    with st.spinner("正在加载网页、搜索小说，请等待3秒..."):
        # 完全复制你原版搜索逻辑，无改动
        driver.get("https://www.bqg691.cc/#/")
        time.sleep(3)
        search_input = driver.find_element(By.CLASS_NAME, "text")
        search_input.send_keys(f"{bk_name}")
        search_input.send_keys(Keys.ENTER)
        time.sleep(3)

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        all_item = soup.select("div.item")

        st.subheader("======= 搜索结果列表 =======")
        result_list = []
        for item in all_item:
            creater = item.select_one('dt > span')
            creater_yes = creater.get_text(strip=True) if creater else "未知作者"
            book_a = item.select_one("dt > a")
            book_name = book_a.get_text(strip=True) if book_a else "无书名"
            book_href = book_a["href"] if book_a else ""
            result_list.append({
                "name": book_name,
                "author": creater_yes,
                "seq": book_href
            })
            st.write(f"书名: {book_name}, 作者: {creater_yes}, 书名序列: {book_href}")
        st.session_state.search_data = result_list

st.divider()

# ====================== 2. 整本小说下载区域 ======================
seq_input = st.text_input("请输入目标小说的序列：")
download_btn = st.button("📥 开始下载整本小说")

# 存储完整小说文本
novel_content = ""

if download_btn and seq_input.strip():
    with st.spinner("正在统计章节、批量下载正文..."):
        # 完全复制你原版目录+下载逻辑
        driver.get(f"https://www.bqg691.cc/#/book/{seq_input}/")
        time.sleep(3)
        download_1 = driver.page_source
        downloads = BeautifulSoup(download_1, "html.parser")

        st.write("正在计算章节数......")
        dl_list = downloads.select("dd")
        total_chapter = len(dl_list)
        st.write(f"全书总章节数：{total_chapter}")
        time.sleep(2)
        st.write("开始下载....")

        chap_data = []
        all_a = downloads.select("dd > a")
        for zhangjie_a in all_a:
            zhangjie_name = zhangjie_a.get_text(strip=True)
            zhangjie_href = zhangjie_a["href"]
            full_url = "https://www.bqg691.cc" + zhangjie_href
            chap_data.append((zhangjie_name, full_url))

        # 循环下载每一章，拼接文本
        full_text = ""
        for idx, (chap_name, chap_url) in enumerate(chap_data, 1):
            st.write(f"正在下载 {chap_name} 【{idx}/{total_chapter}】")
            driver.get(chap_url)
            time.sleep(2)

            chap_soup = BeautifulSoup(driver.page_source, "html.parser")
            content_box = chap_soup.select_one("div#chaptercontent")
            content = content_box.get_text("\n", strip=True) if content_box else "该章节无内容"

            full_text += f"【{chap_name}】\n"
            full_text += content
            full_text += "\n\n========================================\n\n"

        # 下载完成提示
        st.success("✅ 整本小说全部下载完成！")
        # 网页下载按钮，用户直接保存txt
        st.download_button(
            label="💾 点击下载完整小说txt文件",
            data=full_text,
            file_name=f"{bk_name if bk_name else '完整小说'}.txt",
            mime="text/plain"
        )

st.divider()
st.caption("天空属于哈夫克")