import streamlit as st
import requests
from bs4 import BeautifulSoup

# 伪装浏览器请求头，防止网站拦截爬虫
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome 120.0.0.0 Safari/537.36",
    "Referer": "https://www.bqg691.cc/"
}
# 网站根域名
BASE_DOMAIN = "https://www.bqg691.cc"

# 页面基础配置
st.set_page_config(page_title="哈夫克小说搜寻程序", page_icon="📖")
st.title("📖 哈夫克小说搜寻程序 V1.0.0")
st.subheader("天空属于哈夫克 | 技术提供：银翼")
st.divider()

# 会话存储搜索结果
if "search_result_list" not in st.session_state:
    st.session_state.search_result_list = []

# ===================== 1. 小说搜索模块 =====================
book_name_input = st.text_input("请输入小说名字：")
search_button = st.button("🔍 点击搜索小说")

if search_button and book_name_input.strip():
    with st.spinner("正在加载搜索结果，请稍等..."):
        # 拼接搜索页面地址
        search_url = f"{BASE_DOMAIN}/#/search/{book_name_input}"
        try:
            resp = requests.get(search_url, headers=HEADERS, timeout=10)
            resp.encoding = "utf-8"
            soup = BeautifulSoup(resp.text, "lxml")
            item_list = soup.select("div.item")

            st.subheader("======= 搜索结果列表 =======")
            res_data = []
            for item in item_list:
                # 作者
                author_tag = item.select_one("dt > span")
                author = author_tag.get_text(strip=True) if author_tag else "未知作者"
                # 书名、链接
                a_tag = item.select_one("dt > a")
                book_title = a_tag.get_text(strip=True) if a_tag else "无书名"
                book_href = a_tag["href"] if a_tag else ""
                res_data.append({
                    "title": book_title,
                    "author": author,
                    "href": book_href
                })
                st.write(f"书名：{book_title} | 作者：{author} | 序列：{book_href}")
            st.session_state.search_result_list = res_data
        except Exception as e:
            st.error(f"搜索失败：{str(e)}")

st.divider()

# ===================== 2. 小说下载模块 + 3MB自动分割 =====================
# 文本切割函数：单文件最大3MB，换行分割不截断文字
def split_3mb_text(full_text: str, max_byte=3*1024*1024):
    part_arr = []
    cache_text = ""
    line_list = full_text.splitlines(keepends=True)
    for line in line_list:
        # 判断加入该行是否超过3MB
        if len((cache_text + line).encode("utf-8")) > max_byte and cache_text:
            part_arr.append(cache_text)
            cache_text = ""
        cache_text += line
    if cache_text:
        part_arr.append(cache_text)
    return part_arr

seq_input = st.text_input("请输入目标小说的序列（例：/book/341/）：")
download_btn = st.button("📥 开始下载整本小说")

if download_btn and seq_input.strip():
    all_novel_text = ""
    with st.spinner("正在统计章节、批量爬取正文..."):
        try:
            # 目录页
            catalog_url = f"{BASE_DOMAIN}{seq_input}"
            catalog_resp = requests.get(catalog_url, headers=HEADERS, timeout=10)
            catalog_resp.encoding = "utf-8"
            catalog_soup = BeautifulSoup(catalog_resp.text, "lxml")

            # 统计总章节
            dd_tags = catalog_soup.select("dd")
            total_chap = len(dd_tags)
            st.write(f"全书总章节数：{total_chap}")

            # 收集全部章节链接
            chapter_list = []
            a_tags = catalog_soup.select("dd > a")
            for a in a_tags:
                chap_name = a.get_text(strip=True)
                chap_href = a["href"]
                full_chap_url = BASE_DOMAIN + chap_href
                chapter_list.append((chap_name, full_chap_url))

            # 逐章爬取正文
            for idx, (chap_name, chap_url) in enumerate(chapter_list, 1):
                st.write(f"正在下载 {chap_name} 【{idx}/{total_chap}】")
                chap_resp = requests.get(chap_url, headers=HEADERS, timeout=8)
                chap_resp.encoding = "utf-8"
                chap_soup = BeautifulSoup(chap_resp.text, "lxml")
                content_box = chap_soup.select_one("div#chaptercontent")
                content = content_box.get_text("\n", strip=True) if content_box else "该章节无内容"
                # 拼接完整小说文本
                all_novel_text += f"【{chap_name}】\n{content}\n\n========================================\n\n"

            # 分割成多个≤3MB文件
            text_parts = split_3mb_text(all_novel_text)
            st.success(f"✅ 下载完成！自动分割为 {len(text_parts)} 个文件（单文件不超过3MB）")
            # 批量生成下载按钮
            for i, part_content in enumerate(text_parts, 1):
                st.download_button(
                    label=f"下载分片{i}",
                    data=part_content,
                    file_name=f"{book_name_input}_part{i}.txt",
                    mime="text/plain"
                )
        except Exception as err:
            st.error(f"下载失败：{str(err)}")

st.divider()
st.caption("天空属于哈夫克 | 仅供学习测试，禁止商用")