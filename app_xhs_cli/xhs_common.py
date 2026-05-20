import sys
from core import *
import requests
from util import element_on_clickable, element_located

def extract_one_url(text: str) -> str:
    match = re.search(r'https?://\S+', text)
    return match.group(0) if match else ""
def calculate_max_swipe(target_count: int):
     return round(target_count / 2)

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

def get_address(driver,type:str):
    location=""
    distance=""
    try:
        if type=="video":
            # 定位所有符合条件的 LinearLayout
            xpath = ("//android.widget.LinearLayout[count(child::*) = 4 "
                     "and child::*[1][self::android.widget.ImageView] "
                     "and child::*[2][self::android.widget.TextView] "
                     "and child::*[3][self::android.view.View] "
                     "and child::*[4][self::android.widget.TextView and ( translate(@text, '0123456789.', '') = 'm' or translate(@text, '0123456789.', '') = 'km'  )]]")
            layouts = driver.find_elements(AppiumBy.XPATH, xpath)
            for layout in layouts:
                imgs = layout.find_elements(AppiumBy.XPATH, ".//android.widget.ImageView")
                # 查找所有 TextView
                texts = layout.find_elements(AppiumBy.XPATH, ".//android.widget.TextView")
                # 查找所有 View（注意：android.view.View 是通用视图，可能包含很多元素，但这里特指你 XML 中的圆点分隔符等）
                views = layout.find_elements(AppiumBy.XPATH, ".//android.view.View")

                # 如果需要按顺序处理，可以遍历组合
                if len(imgs)==1 and  len(texts)==2 and len(views)==1:
                    location=texts[0].text
                    distance=texts[1].text
        else:
            layouts = driver.find_elements(AppiumBy.XPATH, "//android.widget.LinearLayout")
            for ll in layouts:
                children = ll.find_elements(AppiumBy.XPATH, "//*")
                if len(children)==6 and children[2].text.strip()=='地点':
                    location=children[4].text.strip()
                    distance=children[5].text.strip().replace('·',"")

            # # 找到所有文本为“地点”的TextView，且前一个兄弟元素是ImageView
            # text_views = driver.find_elements(AppiumBy.XPATH, "//android.widget.TextView")
            # for idx, tv in enumerate(text_views):
            #     if tv.text == "地点":
            #         location = text_views[idx+1].text
            #         distance = text_views[idx+2].text
    except Exception as e:
        location=distance=""
        print(f"没有Lbs:{location}|{distance}")
        pass
    return location,distance
#一般用于获取广告的喜欢数,收藏数和评论数,对应的index分别是0,1,2
def get_last_three_numbers_appium(driver):
    try:
        elements = driver.find_elements(AppiumBy.XPATH, "//android.widget.TextView")
        if len(elements) < 3:
            return None


        # last_share_btn =element_located(1,(AppiumBy.XPATH, "(//android.widget.ImageView[@content-desc='分享'])[last()]"),False)
        last_share_btn =element_located(1,(AppiumBy.XPATH, "//android.view.ViewGroup[@index=1 and count(child::*) = 4 "
                                                           " and child::*[1][self::android.widget.ImageView and @index=0] "
                                                           " and child::*[2][self::android.widget.ImageView and @index=1] "
                                                           " and child::*[3][self::android.widget.ImageView and @index=2 and @content-desc='分享'] "
                                                           " and child::*[4][self::android.widget.TextView and @index=3] "
                                                           "]"),False)
        if last_share_btn and len(elements)>3:
            last_three = elements[-4:-1]
        else:
            last_three = elements[-3:]


        texts = ["0" if el.text == "抢首评" or el.text == "评论" or el.text=="点赞" or el.text=="收藏" else el.text for el in last_three]
        # if all(re.match(r'^\d+$', t) for t in texts):
        #     print(f"textslen:{len(texts)}")
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
    location=""
    distance=""
    content = ""
    try:
        note_type = "video" if share_btn.get_attribute("content-desc") == "分享" else "normal"
        # # 2. 获取评论数（content-desc 以 '评论' 开头的 Button）
        # try:
        #     # 使用 find_elements 避免找不到时报错
        #     comment_btns = driver.find_elements(AppiumBy.XPATH,
        #                                         "//android.widget.Button[starts-with(@content-desc, '评论')]")
        #     if comment_btns:
        #         comment_num = comment_btns[0].get_attribute("content-desc").replace('评论',"")
        #
        # except Exception as e:
        #     print(f"获取评论数失败")
        #     # 3. 获取收藏数（content-desc 以 '收藏' 开头的 Button）
        # try:
        #     collect_btns = driver.find_elements(AppiumBy.XPATH,
        #                                         "//android.widget.Button[starts-with(@content-desc, '收藏')]")
        #     if collect_btns:
        #         favorites_num = collect_btns[0].get_attribute("content-desc").replace('收藏',"")
        #
        # except Exception as e:
        #     print(f"获取收藏数失败")
        # #用于广告详情页的互动指标
        # # print(f"comment_num:{comment_num},favorites_num:{favorites_num}")

        interaction_metrics=get_last_three_numbers_appium(driver)
        if interaction_metrics and len(interaction_metrics)>=3:
            like_num = interaction_metrics[0]
            # if comment_num == "" and favorites_num == "":
            favorites_num = interaction_metrics[1]
            comment_num=interaction_metrics[2]
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
                #//得到地址
                location,distance=get_address(driver,"video")
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
                                if content == "":
                                    # print(f"title:{title}")
                                    titlecontent,content = get_details_video_text(driver)
                                    if titlecontent != "":
                                        title = titlecontent
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
                    if content=="":
                        # print(f"title:{title}")
                        titlecontent,content=get_details_narmal_text(driver)
                        if titlecontent !="":
                            title=titlecontent
                    for view in views:
                        # 优先检查 content-desc
                        content_desc = view.get_attribute("content-desc")

                        if content_desc and date_pattern.search(content_desc):
                            # date = content_desc.replace(" 已声明原创","").replace(" 内容为自主拍摄","").replace(" 已声明原创","").rstrip(' ')
                            match = list(re.finditer(r'\d', content_desc))
                            if match:
                                last_digit_pos = match[-1].start()
                                date = content_desc[:last_digit_pos + 1].replace("编辑于", "")
                                location, distance = get_address(driver, "narmal")
                                break
                    if date and len(date) > 2:
                        break
    except Exception as e:
        print(f"get_detail_info获取笔记详情失败:{e}")

    return {
            "title": title,
            "content": content,
            "note_id": note_id,
            "author": "",
            "date": date,
            "like_num": like_num,
            "comment_num": comment_num,
            "favorites_num": favorites_num,
            "location": location,
            "distance": distance,
            "note_type": note_type,
            "share_link": httpurl
            }

def detail_click_suc(driver):
    wait = WebDriverWait(driver, 10)   # 总超时秒
    try:
        element = wait.until(
            EC.any_of(
                EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "分享")),
                EC.element_to_be_clickable((AppiumBy.ID, "com.xingin.xhs:id/moreOperateIV"))
            )
        )

        return True, element
    except:
        return False, None

def get_progress(target_count,completed_count):
    # print("\033[F\033[K", end="")
    print( f"共需要获取{target_count}篇笔记,目前进度{round(completed_count/ target_count * 100)}% ({completed_count}篇)...")

def find_index_tab(driver,tab_text:str):
    # 等待所有 Tab 加载完成
    tabs = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((AppiumBy.XPATH, "//androidx.appcompat.app.ActionBar.Tab"))
    )
    # 遍历找到“发现”所在位置，然后取前一个和后一个
    found_tab = None
    for idx, tab in enumerate(tabs):
        #用发现作为锚定标识
        content=tab.get_attribute("content-desc")
        if content == "发现":
            if tab_text == "发现":
                found_tab = tab
                break
            elif tab_text == "关注" and idx > 0:
                found_tab = tabs[idx - 1]  # 关注（文本可变）
                break
            elif tab_text=="lbs" and  idx < len(tabs) - 1:
                found_tab = tabs[idx + 1]  # LBS如深圳（文本可变）
                break

    return found_tab

def is_on_local(driver,local):
    """
    判断当前是否在选中tab
    返回 True/False
    """
    try:
        # 方法1：检查“深圳”Tab是否被选中（最直接）
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((AppiumBy.XPATH,
                f"//androidx.appcompat.app.ActionBar.Tab[@content-desc='{local}' and @selected='true']"))
        )
        return True
    except:
        print(f"没用选中:{local}")
        pass
    return  False
def get_user_index(driver):
    # xpath = "//android.widget.LinearLayout[count(child::*) >= 3 and child::*[1][self::android.view.ViewGroup] and child::*[2][self::android.widget.LinearLayout] and child::*[3][self::android.widget.LinearLayout]]"
    #
    # # 等待至少一个元素出现，并获取所有匹配的元素（返回列表）
    # containers = WebDriverWait(driver, 10).until(
    #     EC.presence_of_all_elements_located((AppiumBy.XPATH, xpath))
    # )
    # # 获取长度
    # print(f"找到 {len(containers)} 个匹配的布局")
    usr={}
    try:
        container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                AppiumBy.XPATH,
                "//android.widget.LinearLayout[count(child::*) >= 3 and child::*[1][self::android.view.ViewGroup] and child::*[2][self::android.widget.LinearLayout] and child::*[3][self::android.widget.LinearLayout]]"
            ))
        )
        if container:
            nickname=""
            ip=""
            job=""
            follow_count=""
            fans_count=""
            likes_count=""
            signature=""
            # age=""
            # location=""
            other_info=""
            share_link=""
            xhs_id=""
            try:
                # children = container.find_elements(AppiumBy.XPATH, "//*")
                # print(f"children:{len(children)}")
                # if len(children) == 6 and children[2].text.strip() == '地点':
                # print("找到用户首页LinearLayout")
                # 获取头像区 ViewGroup
                view_group = container.find_element(AppiumBy.XPATH, "//android.view.ViewGroup")
                nickname = view_group.find_element(AppiumBy.XPATH, "//android.widget.TextView[1]").text
                ip = view_group.find_element(AppiumBy.XPATH, "//android.widget.TextView[2]").text
                job = view_group.find_element(AppiumBy.XPATH, "//android.widget.LinearLayout/android.widget.TextView").text
                if "小红书号：" in job:
                    xhs_id=job.replace("小红书号：","")
                    job = ""

                # print(f"nickname:{nickname} ip:{ip} job:{job}")
                # # 获取统计数据 LinearLayout（关注/粉丝/获赞）
                stats_layout = container.find_element(AppiumBy.XPATH, "//android.widget.LinearLayout[1]")
                follow_count=stats_layout.find_element(AppiumBy.XPATH, "//android.widget.Button[1]/android.widget.TextView[1]").text
                fans_count=stats_layout.find_element(AppiumBy.XPATH, "//android.widget.Button[2]/android.widget.TextView[1]").text
                likes_count=stats_layout.find_element(AppiumBy.XPATH, "//android.widget.Button[3]/android.widget.TextView[1]").text
                # print(f"follow_count:{follow_count} fans_count:{fans_count} likes_count:{likes_count}")
                # # 获取签名/年龄/国家 LinearLayout
                info_layout = container.find_element(AppiumBy.XPATH, "//android.widget.LinearLayout[2]")
                signature=info_layout.find_element(AppiumBy.XPATH, "//android.widget.TextView").text

                textviews=info_layout.find_elements(AppiumBy.XPATH, "//android.widget.LinearLayout//android.widget.TextView")
                for i, tv in enumerate(textviews):
                    text = tv.text.strip()
                    if text and text!="" and text!=signature and text!="•":
                        other_info=other_info + ("|" + text if other_info else text)
                # location=info_layout.find_element(AppiumBy.XPATH, "//android.widget.LinearLayout//android.widget.LinearLayout[2]").get_attribute("content-desc")
                # print(f"signature:{signature} age:{age} location:{location}")

                more_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.ImageView[@content-desc='更多']"))
                )
                more_btn.click()
                # 2. 等待底部菜单出现，并点击“复制链接”选项
                copy_link = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.TextView[@text='复制链接']"))
                )
                copy_link.click()
                share_link = driver.get_clipboard_text().split("?", 1)[0]
                # httpurl = extract_one_url(share_link)
                # lonurl = expand_short_url(httpurl)
                # print(f"share_link:{share_link}")
                # print(f"httpurl:{httpurl} ")
                # print(f"lonurl:{lonurl}")

            except:
                pass
            usr={
                "user_name": nickname,
                "xhs_id": xhs_id,
                "ip_location": ip,
                "job": job,
                "follow_count": follow_count,
                "fans_count": fans_count,
                "likes_collect": likes_count,
                "signature": signature,
                "share_link": share_link,
                "other_info": other_info,
            }
    except:
        print(f"用户首页LinearLayout没找到")
        pass
    return usr

def get_user_note_list(driver,author,target_count: int,max_swipe_count=10):
    collected = []  # 存放已抓取卡片的数据
    title_ary = []  # 用标题来去重
    swipe_count = 0
    #先常规滚动下,否则遇到自己的主页,无法进行轻微的滚动
    scroll_down_screens(driver,1,850)
    while len(collected) < target_count:
        # 定位 content-desc 以“笔记”或“视频”开头的元素
        xpath = "//*[starts-with(@content-desc, '笔记') or starts-with(@content-desc, '视频')]"
        # elements = driver.find_elements(AppiumBy.XPATH, xpath)
        elements = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((AppiumBy.XPATH, xpath)))
        # desc_list = [elem.get_attribute("content-desc") for elem in elements]
        for elem in elements:
            try:
                temp_title = elem.get_attribute("content-desc")
            except:
                break
            # 存在就不要放子
            if temp_title in title_ary or temp_title == "" or temp_title is None :
                continue
            title_ary.append(temp_title)
            elem.click()
            dsc, share_btn = detail_click_suc(driver)
            if not dsc:
                print(f"详情页不可获取,get_user_note_list:{temp_title}")
                continue
            detailNote = get_detail_info(driver, share_btn, True)
            note_id = detailNote.get("note_id")
            title = detailNote.get("title")
            note_type = detailNote.get("note_type")
            comment_num = detailNote.get("comment_num")
            favorites_num = detailNote.get("favorites_num")
            share_link = detailNote.get("share_link")
            like_num = detailNote.get("like_num")
            date = detailNote.get("date")
            location = detailNote.get("location")
            distance = detailNote.get("distance")
            # 退出详情页
            driver.back()
            # 退出详情页是否成功
            note_tab = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.TextView[@text='笔记']"))
            )
            # 确认返回成功否则系统直接退出
            if not note_tab:
                print(f"返回失败,get_user_note_list:{temp_title}")
                sys.exit(1)

            if not note_id or len(note_id) < 5:
                continue

            note = {
                "title": title,
                "note_id": note_id,
                "author": author,
                "date": date,
                "like_num": like_num,
                "comment_num": comment_num,
                "favorites_num": favorites_num,
                "location": location,
                "distance": distance,
                "note_type": note_type,
                "share_link": share_link
            }
            collected.append(note)
            get_progress(target_count, len(collected))
            if len(collected) >= target_count:
                return collected

        if swipe_count >= max_swipe_count:
            break
        # 4. 滚动加载更多
        scroll_small_step(driver, 0.2)

        time.sleep(1)
        swipe_count = swipe_count + 1
    return collected

def get_details_narmal_text(driver):
   title=""
   content=""

   titleAndContent= element_located(3, (
       AppiumBy.XPATH,"//android.widget.LinearLayout[count(child::*) = 2 and child::*[1][self::android.widget.TextView] and child::*[2][self::android.widget.TextView] ]"
   ), False)
   if titleAndContent:
        title = titleAndContent.find_element(AppiumBy.XPATH, "//android.widget.TextView[1]").text
        content = titleAndContent.find_element(AppiumBy.XPATH, "//android.widget.TextView[2]").text
   else:
       content_ele = element_located(3, (AppiumBy.XPATH,"//android.widget.LinearLayout[count(child::*) = 1 and child::*[1][self::android.widget.TextView] ]"),False)
       if content_ele:
            content = content_ele.find_element(AppiumBy.XPATH, "//android.widget.TextView[1]").text
   #只有内容没有title
   # print(f"narmal title:{title[:5]} content:{content[:10]}")
   return title,content

def get_details_video_text(driver):
    content=""
    title=""

    container = element_located(10, (AppiumBy.XPATH,
                         "//android.widget.LinearLayout[count(child::*) = 1 and child::*[1][self::android.widget.TextView and @index=0] ]"),
                    False)
    if container:
        # 视频评论里用换行来分离标题和换行(去掉开头的换行)
        content =  container.find_element(AppiumBy.XPATH, "//android.widget.TextView[1]").text
        # if content.startswith("\n"):
        #     content = content[1:]
        title, _, content = content.partition('\n')
    # print(f"video title:{title[:5]} content:{content[:10]}")
    return title,content

def back_index(driver, max_attempts=10):
    # 如果 driver 无效，尝试重连
    if not driver or not driver.session_id:
        driver.quit()
        driver = get_driver()
        if not driver:
            print("无法创建 driver 会话")
            return

    for attempt in range(max_attempts):
        # 每次循环开始时检查会话有效性
        try:
            _ = driver.current_activity  # 轻量级操作，验证会话
        except WebDriverException:
            print("会话失效，尝试重新连接...")
            driver.quit()
            driver = get_driver()
            if not driver:
                print("重连失败，退出 back_index")
                return
            continue

        if element_on_clickable(1,  (AppiumBy.ACCESSIBILITY_ID,"首页"), 0, False):
            return
        # 否则执行返回操作，并等待页面刷新
        try:
            driver.back()
            time.sleep(0.5)
        except WebDriverException as e:
            print(f"返回操作失败: {e}")

    print(f"⚠️ 尝试 {max_attempts} 次后仍未回到首页，请手动检查")