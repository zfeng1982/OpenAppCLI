import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from core import *
import requests

def extract_one_url(text: str) -> str:
    match = re.search(r'https?://\S+', text)
    return match.group(0) if match else ""
def expand_short_url(short_url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    try:
        resp = requests.get(
            short_url,
            headers=headers,
            allow_redirects=False,  # 关键：禁止自动跳转
            timeout=5
        )
        if resp.status_code in (301, 302, 303, 307, 308):
            return resp.headers.get("Location")
        return short_url  # 没有跳转
    except Exception as e:
        return f"解析失败: {e}"
def get_note_type(driver):
    note_type = "normal"
    if is_video_note(driver):
        note_type = "video"
    return note_type

def is_video_note(driver) -> bool:
    """返回 True 表示当前页面是视频笔记"""
    try:
        driver.find_element(AppiumBy.CLASS_NAME, "com.xingin.redview.seekbar.VideoSeekBar")
        return True
    except:
        return False
#一般用于获取广告的喜欢数,收藏数和评论数,对应的index分别是0,1,2
def get_last_three_numbers_appium(driver):
    elements = driver.find_elements(AppiumBy.XPATH, "//android.widget.TextView")
    if len(elements) < 3:
        return None
    last_three = elements[-3:]
    texts = [el.text for el in last_three]
    if all(re.match(r'^\d+$', t) for t in texts):
        return texts
    return None

def get_detail_info(driver,is_id =True):
    note_id = ""
    comment_num = ""
    favorites_num =""
    like_num =""
    # 默认为普通图文类型
    note_type="normal"
    httpurl=""

    try:

        note_type=get_note_type(driver)
            # 2. 获取评论数（content-desc 以 '评论' 开头的 Button）
        try:
            # 使用 find_elements 避免找不到时报错
            comment_btns = driver.find_elements(AppiumBy.XPATH,
                                                "//android.widget.Button[starts-with(@content-desc, '评论')]")
            if comment_btns:
                comment_num = comment_btns[0].get_attribute("content-desc").replace('评论',"")

        except Exception as e:
            print(f"获取评论数失败")

            # 3. 获取收藏数（content-desc 以 '收藏' 开头的 Button）
        try:
            collect_btns = driver.find_elements(AppiumBy.XPATH,
                                                "//android.widget.Button[starts-with(@content-desc, '收藏')]")
            if collect_btns:
                favorites_num = collect_btns[0].get_attribute("content-desc").replace('收藏',"")

        except Exception as e:
            print(f"获取收藏数失败")


        #用于广告详情页的互动指标
        # print(f"comment_num:{comment_num},favorites_num:{favorites_num}")
        if comment_num=="" and favorites_num=="":
            interaction_metrics=get_last_three_numbers_appium(driver)
            if interaction_metrics and len(interaction_metrics)>=3:
                favorites_num = interaction_metrics[1]
                comment_num=interaction_metrics[2]



        # like_num_fail =False
        # try:
        #     like_layout = driver.find_element(AppiumBy.XPATH,
        #                                       "//android.widget.Button[starts-with(@content-desc, '收藏')]/preceding-sibling::android.widget.LinearLayout[1]")
        #     # 在该布局内查找 TextView（显示数字）
        #     like_text_elem = like_layout.find_element(AppiumBy.XPATH, ".//android.widget.TextView")
        #     like_num = like_text_elem.text.strip()
        # except Exception as e:
        #     like_num_fail=True
        #
        # try:
        #     if like_num_fail:
        #         # like_btn = driver.find_element(AppiumBy.XPATH,"//android.widget.Button[starts-with(@content-desc, '点赞')]")
        #         like_btn = driver.find_element(AppiumBy.XPATH,"//android.widget.Button[contains(@content-desc, '点赞')]")
        #         like_num = like_btn.get_attribute("content-desc").replace('已点赞',"").replace('点赞',"").replace(' ',"")
        # except Exception as e:
        #     print(f"获取点赞数失败: {e}")
        # 先用分享文本找,找不到用moreOperateIV
        try:
            share_btn = driver.find_element(AppiumBy.XPATH, ".//*[@content-desc='分享']")
        except:
            share_btn = driver.find_element(AppiumBy.ID, "com.xingin.xhs:id/moreOperateIV")

        if share_btn:
            share_btn.click()
            time.sleep(1)
            # 2. 在弹窗中点击“复制链接”
            copy_btn = WebDriverWait(driver, 10).until(EC.presence_of_element_located((AppiumBy.XPATH, "//*[@text='复制链接']")))
            copy_btn.click()
            time.sleep(1)
            # 3.获取剪贴板内容
            share_link = driver.get_clipboard_text()
            httpurl = extract_one_url(share_link)
            if is_id:
                lonurl = expand_short_url(httpurl)
                #     # 4. 从链接中提取笔记ID
                #     # 链接格式示例：https://www.xiaohongshu.com/discovery/item/笔记ID?source=...
                match = re.search(r'/item/([a-zA-Z0-9]+)', lonurl)
                if match:
                    note_id = match.group(1)

    except Exception as e:
        print(f"获取笔记ID失败")

    return {
            "title": "",
            "note_id": note_id,
            "author": "",
            "date": "",
            "like_num": like_num,
            "comment_num": comment_num,
            "favorites_num": favorites_num,
            "note_type": note_type,
            "share_link": httpurl
            }


def collect_note_index_cards(driver,target_count: int,max_swipe_count=10):
    """
    滚动并收集小红书笔记卡片信息
    :param driver: 设备
    :param limit: 需要收集的卡片数量
    :param max_scrolls: 最大滚动次数，防止无限循环
    :return: 列表，每个元素为 dict {"title": str, "author": str, "date": str, "likes": str}
    """
    collected = []  # 存放已抓取卡片的数据
    # 获取屏幕尺寸，用于滚动
    size = driver.get_window_size()
    start_x = size["width"] // 2
    start_y = int(size["height"] * 0.8)
    end_y = int(size["height"] * 0.2)


    title_ary=[]  #用标题来去重
    swipe_count=0
    while len(collected) < target_count:
        # 定位 content-desc 以“笔记”或“视频”开头的元素
        xpath = "//*[starts-with(@content-desc, '笔记') or starts-with(@content-desc, '视频') or starts-with(@content-desc, '直播')]"
        elements = driver.find_elements(AppiumBy.XPATH, xpath)
        # desc_list = [elem.get_attribute("content-desc") for elem in elements]
        for elem in elements:
            try:
                desc=elem.get_attribute("content-desc")
            except:
                break
            type_=""
            title=""
            author=""
            likes=""
            date=""
            comment_num=""
            favorites_num=""
            note_type="normal"
            share_link=""
            # pattern = r'^(笔记|视频|直播)\s+(.+?)\s+来自\s*(.+?)\s*([\d.]+[万]?)?\s*(赞|人观看)$'
            pattern = r'^(笔记|视频|直播)\s+(.+?)\s+来自\s*(.+?)\s*([\d.]+[万]?)?赞$'
            print(f"desc:{desc}")

            match = re.match(pattern, desc)
            if match:
                type_, title, author, likes = match.groups()

            if not likes:
                likes="0"

            print(f"type_:{type_},title:{title},author:{author},likes:{likes}")
            # 存在就不要放子
            if title in title_ary or title=="" or title is None or type_=='直播' or type_=="":
                continue
            elem.click()
            time.sleep(4)

            detailNote=get_detail_info(driver)
            note_id=detailNote.get("note_id")
            note_type=detailNote.get("note_type")
            comment_num=detailNote.get("comment_num")
            favorites_num=detailNote.get("favorites_num")
            share_link=detailNote.get("share_link")


            if not note_id or len(note_id)<5:
                # 退出详情页面,并且跳过这个卡片
                driver.back()
                continue
            date_pattern = re.compile(
                r"\d{1,2}-\d{1,2}|\d{4}-\d{1,2}-\d{1,2}|\d+分钟前|\d+小时前|刚刚|今天|昨天|\d+天前")
            # 获取评论数
            if note_type =='video':
                pass
                # 这个展开不大准确
                # time.sleep(1)
                is_click=click_expand_by_coordinate(driver,'展开')
                if is_click:
                    time.sleep(1)
                    #展示开必须能找到评论两个字,否则可能是点错位置了
                    elements = driver.find_elements(AppiumBy.XPATH,"//android.widget.TextView[contains(@text, '评论')]")
                    if len(elements) > 0:
                        try:
                            #评论内容太多往下拉下
                            for i in range(20):
                                views = driver.find_elements(AppiumBy.XPATH, "//android.view.View")
                                for view in views:
                                    # 优先检查 content-desc
                                    content_desc = view.get_attribute("content-desc")
                                    if content_desc and date_pattern.search(content_desc):
                                        match = list(re.finditer(r'\d', content_desc))
                                        if match:
                                            last_digit_pos = match[-1].start()
                                            date = content_desc[:last_digit_pos + 1].replace("编辑于","")
                                        break
                                if not date and len(date)<2:
                                    scroll_small_step(driver,0.5)
                                    time.sleep(0.1)
                                else:
                                    break
                        except:
                            pass
                    driver.back()
            else:
                # 最多下划20次
                for i in range(20):
                    scroll_small_step(driver,0.5)
                    time.sleep(0.1)
                    views = driver.find_elements(AppiumBy.XPATH, "//android.view.View")
                    for view in views:
                        # 优先检查 content-desc
                        content_desc = view.get_attribute("content-desc")

                        if content_desc and date_pattern.search(content_desc):
                            # date = content_desc.replace(" 已声明原创","").replace(" 内容为自主拍摄","").replace(" 已声明原创","").rstrip(' ')
                            match = list(re.finditer(r'\d', content_desc))
                            if match:
                                last_digit_pos = match[-1].start()
                                date=content_desc[:last_digit_pos + 1].replace("编辑于","")
                            # date = content_desc.replace(" 已声明原创","").replace(" 内容为自主拍摄","").rceplace(" 已声明原创","").rstrip(' ')
                                break
                    if  date and len(date)>2:
                        break
            time.sleep(1)
            driver.back()
            title_ary.append(title)
            note = {
                "title": title,
                "note_id": note_id,
                "author": author,
                "date": date,
                "like_num": likes,
                "comment_num": comment_num,
                "favorites_num": favorites_num,
                "note_type": note_type,
                "share_link": share_link
            }
            collected.append(note)
            print(f"已获取第{len(collected)},共需要获取{target_count}篇笔记")
            if len(collected) >= target_count:
                return collected

        if  swipe_count>=max_swipe_count:
            break
        # 4. 滚动加载更多
        driver.swipe(start_x, start_y, start_x, end_y, duration=800)
        time.sleep(3)
        swipe_count=swipe_count+1
    return collected


