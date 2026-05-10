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
            print(f"获取评论数失败: {e}")

            # 3. 获取收藏数（content-desc 以 '收藏' 开头的 Button）
        try:
            collect_btns = driver.find_elements(AppiumBy.XPATH,
                                                "//android.widget.Button[starts-with(@content-desc, '收藏')]")
            if collect_btns:
                favorites_num = collect_btns[0].get_attribute("content-desc").replace('收藏',"")

        except Exception as e:
            print(f"获取收藏数失败: {e}")

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
        print(f"获取笔记ID失败: {e}")
    return  note_id,note_type,comment_num,favorites_num,like_num,httpurl

def collect_note_cards(driver,target_count: int,max_swipe_count=10):
    """
    滚动并收集小红书笔记卡片信息
    :param driver: 设备
    :param limit: 需要收集的卡片数量
    :param scroll_pause: 每次滚动后等待时间（秒）
    :param max_scrolls: 最大滚动次数，防止无限循环
    :return: 列表，每个元素为 dict {"title": str, "author": str, "date": str, "likes": str}
    """
    wait = WebDriverWait(driver, 10)

    # 等待 RecyclerView 出现
    wait.until(EC.presence_of_element_located(
        (AppiumBy.XPATH, "//androidx.recyclerview.widget.RecyclerView")
    ))

    # 等待至少一个卡片出现（确保内容加载）
    wait.until(EC.presence_of_element_located(
        (AppiumBy.XPATH, "//androidx.recyclerview.widget.RecyclerView/android.widget.FrameLayout")
    ))
    # 等待搜索结果页加载完成（例如等待 RecyclerView 出现）
    recycler_xpath = "//androidx.recyclerview.widget.RecyclerView"
    wait.until(EC.presence_of_element_located((AppiumBy.XPATH, recycler_xpath)))


    collected = []  # 存放已抓取卡片的数据


    # 获取屏幕尺寸，用于滚动
    size = driver.get_window_size()
    start_x = size["width"] // 2
    start_y = int(size["height"] * 0.8)
    end_y = int(size["height"] * 0.2)

    scroll_small_step(driver)
    time.sleep(2)  # 额外等待页面渲染
    title_ary=[]  #用标题来去重
    swipe_count=0
    while len(collected) < target_count:
        # 2. 获取当前屏幕内所有可能的卡片容器（RecyclerView的直接子FrameLayout）
        cards = driver.find_elements(AppiumBy.XPATH,
                                     "//androidx.recyclerview.widget.RecyclerView/android.widget.FrameLayout")

        for card in cards:
            # 递归获取所有TextView和ImageView
            text_views = card.find_elements(AppiumBy.XPATH, ".//android.widget.TextView")
            image_views = card.find_elements(AppiumBy.XPATH, ".//android.widget.ImageView")

            # text_views[0].click()

            if not text_views or not image_views:
                continue  # 缺少文本或图片，直接跳过

            # 解析日期和点赞数
            date_pattern = re.compile(r"\d{1,2}-\d{1,2}|\d{4}-\d{1,2}-\d{1,2}|\d+分钟前|\d+小时前|刚刚|昨天|\d+天前")
            # likes_pattern = re.compile(r"^[\d,]+(\.\d+)?[万wW]?$")
            view_len=len(text_views)
            for idx, tv in enumerate(text_views):
                text = tv.text.strip()
                # print(f"text({idx}):{text}")
                # 检查日期,如是出现了日期则日期前一个为作者,前两个为标题,后一个为点赞数
                if date_pattern.search(text):
                    # 防止 list index out of range
                    if idx<2 or (idx>view_len-1):
                        continue
                    title=text_views[idx-2].text.strip()
                    author = text_views[idx - 1].text.strip()
                    # 标题已经存在则跳过.或者出现错误位的情况,如标题是数字或者日期,作者错位
                    if title in title_ary or title.isdigit() or date_pattern.search(title) or author=="关注":
                        # print(f"title continue:{title} author:{author}")
                        continue
                    tv.click()
                    time.sleep(5)
                    note_id,note_type,comment_num,favorites_num,_,share_link=get_detail_info(driver)
                    driver.back()
                    title_ary.append(title)

                    date = text
                    like_num =text_views[idx+1].text.strip()
                    note = {
                        "title": title,
                        "note_id": note_id,
                        "author": author,
                        "date": date,
                        "like_num": like_num,
                        "comment_num": comment_num,
                        "favorites_num": favorites_num,
                        "note_type": note_type,
                        "share_link": share_link
                    }

                    collected.append(note)
                    # 放够了直接返回吧
                    if len(collected) >= target_count:
                        return collected

        if  swipe_count>=max_swipe_count:
            break
        # 4. 滚动加载更多
        driver.swipe(start_x, start_y, start_x, end_y, duration=800)
        time.sleep(2)
        swipe_count=swipe_count+1
    return collected


