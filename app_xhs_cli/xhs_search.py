from .xhs_common import *

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
            text_views = card.find_elements(AppiumBy.XPATH, ".//android.widget.TextView")
            image_views = card.find_elements(AppiumBy.XPATH, ".//android.widget.ImageView")

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
                    tv.click()
                    dsc, share_btn = detail_click_suc(driver)
                    if not dsc:
                        print(f"详情页不可获取,collect_note_cards:{title}")
                        # 整张卡片都不要
                        break
                    detailNote = get_detail_info(driver,share_btn)
                    note_id = detailNote.get("note_id")
                    note_type = detailNote.get("note_type")
                    comment_num = detailNote.get("comment_num")
                    favorites_num = detailNote.get("favorites_num")
                    share_link = detailNote.get("share_link")
                    driver.back()
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
                    print(f"已获取{len(collected)}篇,共需要获取{target_count}篇笔记")
                    # 放够了直接返回吧
                    if len(collected) >= target_count:
                        return collected

        if  swipe_count>=max_swipe_count:
            break
        # 4. 滚动加载更多
        scroll_small_step(driver, 0.2)
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
            # first_user = WebDriverWait(driver, 10).until(
            #     EC.element_to_be_clickable((AppiumBy.XPATH, "//android.view.ViewGroup[contains(@content-desc, '粉丝')][1]"))
            # )
            first_user=driver.find_elements(AppiumBy.XPATH, "//android.view.ViewGroup[contains(@content-desc, '粉丝')][1]")
            # 有搜索结果
            if first_user:
                first_user[0].click()
                time.sleep(2)  # 等待用户列表加载
                textView = driver.find_elements(AppiumBy.XPATH,"//android.widget.TextView")
                # 用户名
                use_name=textView[0].text.strip()
                # # 职业
                # print(f"text1:{textView[1].text}")
                # # 简介
                # print(f"desc:{textView[5].text}")
                # 小红书号
                xhs_id_elem = driver.find_element(AppiumBy.XPATH, "//android.widget.TextView[contains(@text, '小红书号：')]")
                xhs_id = xhs_id_elem.text.split('：')[-1].strip()
                # IP属地
                ip_elem = driver.find_element(AppiumBy.XPATH, "//android.widget.TextView[contains(@text, 'IP属地：')]")
                ip_location = ip_elem.text.split('：')[-1].strip()

                follow_btn = driver.find_element(AppiumBy.XPATH,"//android.widget.Button[.//android.widget.TextView[@text='关注']]")
                follow_count = follow_btn.find_element(AppiumBy.XPATH, ".//android.widget.TextView[1]").text

                # 粉丝数（取按钮内第一个 TextView 的数字文本）
                fans_btn = driver.find_element(AppiumBy.XPATH, "//android.widget.Button[contains(@content-desc, '粉丝')]")
                fans_count = fans_btn.find_element(AppiumBy.XPATH, ".//android.widget.TextView[1]").text

                # 获赞与收藏（取按钮内第一个 TextView 的数字文本）
                likes_btn = driver.find_element(AppiumBy.XPATH,
                                                "//android.widget.Button[contains(@content-desc, '获赞与收藏')]")
                likes_collect = likes_btn.find_element(AppiumBy.XPATH, ".//android.widget.TextView[1]").text

                result["user"] = {
                    "user_name": use_name,
                    "xhs_id": xhs_id,
                    "ip_location": ip_location,
                    "follow_count": follow_count,
                    "fans_count": fans_count,
                    "likes_collect": likes_collect,
                }
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

            notes=collect_note_search_cards(driver,args.limit,30)
            result["notes"] = notes
        print(json.dumps(result, ensure_ascii=False, indent=2))
        elapsed = time.time() - start_time
        hours, rem = divmod(elapsed, 3600)
        minutes, seconds = divmod(rem, 60)
        if args.type == 'note':
            print(f"读取[搜索]笔记{len(result.get("notes"))}篇 总耗时: {int(hours):02d}:{int(minutes):02d}:{seconds:05.2f}")
    except Exception as e:
        print(f"发生未知错误: {e}")

