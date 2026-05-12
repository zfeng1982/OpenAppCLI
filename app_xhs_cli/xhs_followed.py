from .xhs_common import *
# python openappcli.py xhs-index followed  --limit 2
def collect_note_cards(driver,target_count: int,max_swipe_count=10):
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
    # size = driver.get_window_size()
    # start_x = size["width"] // 2
    # start_y = int(size["height"] * 0.8)
    # end_y = int(size["height"] * 0.2)

    scroll_small_step(driver)
    time.sleep(2)  # 额外等待页面渲染
    deduplicate_char=[]  #标题要进入详情页取,使用作者+时间+点赞数来去重,除非同一个作者同一天发两条,而点赞数一让,这种去掉一条也没关系.
    swipe_count=0
    while len(collected) < target_count:
        # 2. 获取当前屏幕内所有可能的卡片容器（RecyclerView的直接子FrameLayout）
        cards = driver.find_elements(AppiumBy.XPATH,"//androidx.recyclerview.widget.RecyclerView/android.widget.FrameLayout")
        for card in cards:
            # 递归获取所有TextView和ImageView
            try:
                text_views = card.find_elements(AppiumBy.XPATH, ".//android.widget.TextView")
                image_views = card.find_elements(AppiumBy.XPATH, ".//android.widget.ImageView")
            except Exception as e:
                print(f"text_views/image_views失败:{e}")
                break
            if not text_views or not image_views:
                continue  # 缺少文本或图片，直接跳过

            # 解析日期和点赞数
            date_pattern = re.compile(r"\d{1,2}-\d{1,2}|\d{4}-\d{1,2}-\d{1,2}|\d+分钟前|\d+小时前|刚刚|今天|昨天|\d+天前")

            # for idx in range(len(text_views)):
            for idx, tv in enumerate(text_views):
                time.sleep(0.5)
                try:
                    text = tv.text.strip()
                except Exception as e:
                    print(f"v.text.strip失败:{e}")
                    break
                # print(f"text({idx}):{text}")
                # 检查日期,如是出现了日期则日期前一个为作者,前两个为标题,后一个为点赞数
                if date_pattern.search(text) and  image_views[0] and image_views[0].is_enabled():
                    if idx!=1:
                        continue
                    date = text
                    author = text_views[idx - 1].text.strip()
                    like_num = text_views[idx + 1].text.strip()
                    if like_num=="赞":
                        like_num="0"
                        # 作者+时间+点赞
                    ded = author + date + like_num
                    if ded in deduplicate_char:
                        continue
                    deduplicate_char.append(ded)
                    # 进入详情页
                    image_views[0].click()
                    time.sleep(4)

                    # 得到详情页
                    detailNote = get_detail_info(driver)
                    time.sleep(1)
                    driver.back()
                    time.sleep(1)
                    title=detailNote.get("title")
                    note_id=detailNote.get("note_id")
                    comment_num=detailNote.get("comment_num")
                    favorites_num=detailNote.get("favorites_num")
                    note_type=detailNote.get("note_type")
                    share_link=detailNote.get("share_link")
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
                    # 存在就不要放了
                    if  title == "" or title is None or note_type == '直播' or note_type == "":
                        continue

                    collected.append(note)
                    print(f"已获取第{len(collected)},共需要获取{target_count}篇笔记")
                    # 放够了直接返回吧
                    if len(collected) >= target_count:
                        return collected
        if  swipe_count>=max_swipe_count:
            break
        #迷路检查
        if not check_current_page(driver,['首页', '发现', '关注']):
            ##回到首页关注页面重新开始
            back_index(driver, ['首页', '发现', '关注'])
            follow_tab = driver.find_element(AppiumBy.XPATH,"//androidx.appcompat.app.ActionBar.Tab[@content-desc='关注']")
            follow_tab.click()
            print("迷路了重新开始吧")
        else:
            # 滚动加载更多
            print("滚动加载更多")
            scroll_small_step(driver, 0.3)
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
        notes = collect_note_cards(driver, args.limit,30)
        result["notes"] = notes
    except Exception as e:
        print(f"({e})")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"notes len:{len(notes)}")