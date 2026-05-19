import sys
import time

from .xhs_common import *
def back_search_suc(driver):
    try:
        WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((AppiumBy.XPATH, "//android.widget.TextView[@text='问一问']")))
        return True
    except:
        pass
    return  False
def collect_note_search_cards(driver,target_count: int,max_swipe_count=10):
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

    collected = []  # 存放已抓取卡片的数据

    scroll_small_step(driver)
    time.sleep(2)  # 额外等待页面渲染
    title_ary=[]  #用标题来去重
    swipe_count=0
    while len(collected) < target_count:
        # 2. 获取当前屏幕内所有可能的卡片容器（RecyclerView的直接子FrameLayout）
        cards =wait.until(EC.presence_of_all_elements_located((AppiumBy.XPATH,  "//androidx.recyclerview.widget.RecyclerView/android.widget.FrameLayout")))
        for card in cards:
            # 递归获取所有TextView和ImageView
            try:
                text_views = card.find_elements(AppiumBy.XPATH, ".//android.widget.TextView")
                image_views = card.find_elements(AppiumBy.XPATH, ".//android.widget.ImageView")
            except Exception as e:
                print(f"text_views/image_views: {e}")
                break

            # text_views[0].click()

            if not text_views or not image_views or len(text_views)<4 or len(image_views)<2:
                continue  # 缺少文本或图片，直接跳过

            # 解析日期和点赞数
            date_pattern = re.compile(r"\d{1,2}-\d{1,2}|\d{4}-\d{1,2}-\d{1,2}|\d+分钟前|\d+小时前|刚刚|今天|昨天|\d+天前")
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
                    date = text
                    title=text_views[idx-2].text.strip()
                    author = text_views[idx - 1].text.strip()
                    like_num = text_views[idx + 1].text.strip()
                    # 标题已经存在则跳过.或者出现错误位的情况,如标题是数字或者日期,作者错位
                    if title in title_ary or title.isdigit() or date_pattern.search(title) or author=="关注":
                        # print(f"title continue:{title} author:{author}")
                        continue
                    # print(f"点击详情{title}")
                    tv.click()
                    dsc, share_btn = detail_click_suc(driver)
                    if not dsc:
                        print(f"详情页不可获取,collect_note_cards:{title}")
                        #还是点一下返回?
                        # tv.click()
                        # break
                        sys.exit(1)
                    detailNote = get_detail_info(driver,share_btn)
                    note_id = detailNote.get("note_id")
                    note_type = detailNote.get("note_type")
                    comment_num = detailNote.get("comment_num")
                    favorites_num = detailNote.get("favorites_num")
                    share_link = detailNote.get("share_link")
                    time.sleep(0.5)
                    # print(f"点击返回:{title}")
                    driver.back()
                    # 确认返回成功否则系统直接退出
                    if not back_search_suc(driver):
                        print(f"返回失败,collect_note_cards:{title}")
                        sys.exit(1)
                    # time.sleep(0.5)
                    # print(f"已返回:{title}")
                    title_ary.append(title)
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
                    get_progress(target_count,len(collected))
                    # 放够了直接返回吧
                    if len(collected) >= target_count:
                        return collected

        if  swipe_count>=max_swipe_count:
            break
        # 4. 滚动加载更多
        scroll_small_step(driver,0.2)
        swipe_count=swipe_count+1
    return collected

def run(args):
    driver=get_driver()
    start_time = time.time()
    try:
        keyword = args.keyword  # 字符串或 None
        wait = WebDriverWait(driver, 10)
        # 1. 点击首页顶部的搜索按钮（content-desc="搜索"）
        search_btn = wait.until(EC.element_to_be_clickable(
            (AppiumBy.XPATH, "//android.widget.Button[@content-desc='搜索']")
        ))
        search_btn.click()
        # 2. 等待搜索输入框出现（通常是 EditText）
        input_box = wait.until(EC.presence_of_element_located(
            (AppiumBy.CLASS_NAME, "android.widget.EditText")
        ))
        input_box.send_keys(keyword)
        time.sleep(1) #输入完后等待一下

        driver.execute_script('mobile: performEditorAction', {'action': 'search'})
        time.sleep(1)  # 简单等待，或使用显式等待某个结果元素
        result = {}
        if args.type=='user':
            user_tab = wait.until(EC.element_to_be_clickable(
                (AppiumBy.XPATH, "//android.widget.TextView[@text='用户']")
            ))
            user_tab.click()
            # print("✓ 已切换到“用户”标签页")
            time.sleep(1)  # 等待用户列表加载
            # 点击第一个用户条目
            first_user = wait.until(
                EC.presence_of_all_elements_located((AppiumBy.XPATH, "//android.view.ViewGroup[contains(@content-desc, '粉丝')][1]"))
            )
            # first_user=driver.find_elements(AppiumBy.XPATH, "//android.view.ViewGroup[contains(@content-desc, '粉丝')][1]")
            # 有搜索结果
            if first_user:
                first_user[0].click()

                usr =get_user_index(driver)
                result["user"] =usr
                result["notes"]=[]
                # if args.note:
                #     if  not element_located(1, (AppiumBy.XPATH, "//android.widget.TextView[@text='浏览记录']"), False):
                #         notes = get_user_note_list(driver,usr.get("user_name"), args.limit, 70)
                #         result["notes"] = notes
                #     else:
                #         print("暂不支持查看自己的笔记列表")
                notes = get_user_note_list(driver, usr.get("user_name"), args.limit, 70)
                result["notes"] = notes

        # 搜索笔记
        elif args.type == 'note':
            hot_desc=""
            first_card = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (AppiumBy.XPATH, "(//androidx.recyclerview.widget.RecyclerView/android.widget.FrameLayout)[2]")
                )
            )
            # 在卡片内找第三个 TextView
            text_views = first_card.find_elements(AppiumBy.CLASS_NAME, "android.widget.TextView")
            if len(text_views) >= 3:
                hot_desc = text_views[2].text
                # print(f"正文内容:{hot_desc}")
            result["hot_keyword_desc"] = hot_desc
            result["notes"] = []

            # 查看有无最新的按钮,不是所有的搜索都有排序
            if args.order=='new':
                # latest_btns = driver.find_elements(AppiumBy.XPATH, "//android.widget.FrameLayout[.//android.widget.TextView[@text='最新']]")
                latest_btns = driver.find_elements(AppiumBy.XPATH, "//android.widget.TextView[@text='最新']")
                if latest_btns:
                    latest_btns[0].click()
                    time.sleep(1)#点击后等待

            notes=collect_note_search_cards(driver,args.limit,70)
            result["notes"] = notes
        print(json.dumps(result, ensure_ascii=False, indent=2))
        elapsed = time.time() - start_time
        hours, rem = divmod(elapsed, 3600)
        minutes, seconds = divmod(rem, 60)
        if args.type == 'user':
            print(f"搜索用户信息,笔记{len(result["notes"])}篇 总耗时: {int(hours):02d}:{int(minutes):02d}:{seconds:05.2f}")
        if args.type == 'note':
            print(f"读取[搜索]笔记{len(result.get("notes"))}篇 总耗时: {int(hours):02d}:{int(minutes):02d}:{seconds:05.2f}")
    except Exception as e:
        print(f"发生未知错误a: {e}")

