import re
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
        WebDriverWait(driver, 2).until(EC.presence_of_element_located((AppiumBy.CLASS_NAME, "com.xingin.redview.seekbar.VideoSeekBar")))
        return True
    except:
        return False
#一般用于获取广告的喜欢数,收藏数和评论数,对应的index分别是0,1,2
def get_last_three_numbers_appium(driver):
    try:
        elements = driver.find_elements(AppiumBy.XPATH, "//android.widget.TextView")
        if len(elements) < 3:
            return None
        last_three = elements[-3:]
        texts = [el.text for el in last_three]
        if all(re.match(r'^\d+$', t) for t in texts):
            return texts
    except Exception as e:
        print(f"获取互动数据失败:{e})")
    return None

def get_detail_info(driver,share_btn,is_all=False):
    # 调用这个方法之前需要确认已经进入详情页面了
    note_id = ""
    comment_num = ""
    favorites_num =""
    like_num =""
    # 默认为普通图文类型
    note_type="normal"
    httpurl=""
    title=""
    date=""
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
                like_num = interaction_metrics[0]
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
        # try:
        #     share_btn = driver.find_element(AppiumBy.XPATH, ".//*[@content-desc='分享']")
        # except:
        #     share_btn = driver.find_element(AppiumBy.ID, "com.xingin.xhs:id/moreOperateIV")

        if share_btn:
            share_btn.click()
            # time.sleep(1)
            # 2. 在弹窗中点击“复制链接”
            copy_btn = WebDriverWait(driver, 10).until(EC.presence_of_element_located((AppiumBy.XPATH, "//*[@text='复制链接']")))
            copy_btn.click()
            time.sleep(1)
            # 3.获取剪贴板内容
            share_link = driver.get_clipboard_text()
            title = share_link[:share_link.find("http")].strip()
            # print(f"share_link:{share_link}")
            httpurl = extract_one_url(share_link)
            lonurl = expand_short_url(httpurl)
            #     # 4. 从链接中提取笔记ID
            #     # 链接格式示例：https://www.xiaohongshu.com/discovery/item/笔记ID?source=...
            match = re.search(r'/item/([a-zA-Z0-9]+)', lonurl)
            if match:
                note_id = match.group(1)


        if is_all:
            date_pattern = re.compile(
                r"\d{1,2}-\d{1,2}|\d{4}-\d{1,2}-\d{1,2}|\d+分钟前|\d+小时前|刚刚|今天|昨天|\d+天前")
            # 展开获取日期
            if note_type == 'video':
                pass
                # 这个展开不大准确
                # time.sleep(1)
                is_click = click_expand_by_coordinate(driver, '展开')
                if is_click:
                    # 展示开必须能找到评论两个字,否则可能是点错位置了
                    # elements = driver.find_elements(AppiumBy.XPATH,"//android.widget.TextView[contains(@text, '评论')]")
                    # 用评论判断是否展开了可能不大准确,没有评论可能也展开了,先观察下
                    els = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located(
                        (AppiumBy.XPATH, "//android.widget.TextView[contains(@text, '评论')]")))
                    if len(els) > 0:
                        try:
                            # 评论内容太多往下拉下
                            for i in range(20):
                                views = driver.find_elements(AppiumBy.XPATH, "//android.view.View")
                                for view in views:
                                    # 优先检查 content-desc
                                    content_desc = view.get_attribute("content-desc")
                                    if content_desc and date_pattern.search(content_desc):
                                        match = list(re.finditer(r'\d', content_desc))
                                        if match:
                                            last_digit_pos = match[-1].start()
                                            date = content_desc[:last_digit_pos + 1].replace("编辑于", "")
                                        break
                                if not date and len(date) < 2:
                                    scroll_small_step(driver, 0.2)
                                    time.sleep(0.1)
                                else:
                                    break
                        except:
                            pass
                    driver.back()
            else:
                # 最多下划20次
                for i in range(20):
                    scroll_small_step(driver, 0.2)
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
                                date = content_desc[:last_digit_pos + 1].replace("编辑于", "")
                                # date = content_desc.replace(" 已声明原创","").replace(" 内容为自主拍摄","").rceplace(" 已声明原创","").rstrip(' ')
                                break
                    if date and len(date) > 2:
                        break
    except Exception as e:
        print(f"获取笔记详情失败:{e}")

    return {
            "title": title,
            "note_id": note_id,
            "author": "",
            "date": date,
            "like_num": like_num,
            "comment_num": comment_num,
            "favorites_num": favorites_num,
            "note_type": note_type,
            "share_link": httpurl
            }

def detail_click_suc(driver):
    try:
        share_btn=WebDriverWait(driver, 5).until(EC.presence_of_element_located((AppiumBy.ID, "com.xingin.xhs:id/moreOperateIV")))
        return True,share_btn
    except:
        pass
    # 用是否出现评论来判断详情页，是否点击成功
    try:
        share_btn=WebDriverWait(driver, 3).until(EC.presence_of_element_located( (AppiumBy.XPATH, ".//*[@content-desc='分享']")))
        return True, share_btn
    except:
       pass

    try:
       share_btn=WebDriverWait(driver, 1).until(EC.presence_of_element_located((AppiumBy.XPATH, "//android.widget.ImageView[@content-desc='分享']")))
       return True, share_btn
    except:
        pass

    # # 用是否出现评论来判断详情页，是否点击成功
    # try:
    #     WebDriverWait(driver, 10).until(EC.presence_of_element_located(
    #         (AppiumBy.XPATH, "//android.widget.Button[starts-with(@content-desc, '评论')]")))
    #     return True
    # except:
    #     pass
    #
    #     # 不可评论的详情页
    # try:
    #     WebDriverWait(driver, 10).until(EC.presence_of_element_located(
    #         (AppiumBy.XPATH, "//android.widget.TextView[contains(@text, '评论')]")))
    #     return True
    # except:
    #     pass

    return False,None


