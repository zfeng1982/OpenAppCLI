from .xhs_common import *
# python openappcli.py xhs-discover  --limit 2
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
            date_pattern = re.compile(r"\d{1,2}-\d{1,2}|\d{4}-\d{1,2}-\d{1,2}|\d+分钟前|\d+小时前|刚刚|今天|昨天|\d+天前")
            # likes_pattern = re.compile(r"^[\d,]+(\.\d+)?[万wW]?$")
            view_len=len(text_views)
            for idx, tv in enumerate(text_views):
                text = tv.text.strip()
                print(f"text({idx}):{text}")
                # 检查日期,如是出现了日期则日期前一个为作者,前两个为标题,后一个为点赞数
                if date_pattern.search(text):
                    print(f" date_patterntext:{text}")

                    # # 防止 list index out of range
                    if idx<2 or (idx>view_len-1):
                        continue
                    # title=text_views[idx-2].text.strip()
                    image_views[0].click()
                    time.sleep(2)

                    author = text_views[idx - 1].text.strip()

                    detailNote = get_detail_info(driver)
                    driver.back()

                    date = text
                    like_num =text_views[idx+1].text.strip()
                    note = {
                        "title": "title",
                        "note_id": "note_id",
                        "author": author,
                        "date": date,
                        "like_num": like_num,
                        "comment_num": "comment_num",
                        "favorites_num": "favorites_num",
                        "note_type": "note_type",
                        "share_link": "share_link"
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
def run(args):
    driver = get_driver()
    result = {}
    notes=[]
    try:
        follow_tab = driver.find_element(AppiumBy.XPATH, "//androidx.appcompat.app.ActionBar.Tab[@content-desc='关注']")
        follow_tab.click()
        time.sleep(3)
        notes = collect_note_cards(driver, args.limit,15)
        result["notes"] = notes
    except Exception as e:
        print(f"({e})")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"notes len:{len(notes)}")