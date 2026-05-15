from .xhs_common import *
# python openappcli.py xhs-index discover  --limit 5

def collect_note_cards(driver,target_count: int,max_swipe_count=10):
    """
    滚动并收集小红书笔记卡片信息
    :param driver: 设备
    :param limit: 需要收集的卡片数量
    :param max_scrolls: 最大滚动次数，防止无限循环
    :return: 列表，每个元素为 dict {"title": str, "author": str, "date": str, "likes": str}
    """
    collected = []  # 存放已抓取卡片的数据



    title_ary=[]  #用标题来去重
    swipe_count=0
    while len(collected) < target_count:
        # 定位 content-desc 以“笔记”或“视频”开头的元素
        xpath = "//*[starts-with(@content-desc, '笔记') or starts-with(@content-desc, '视频')]"
        # elements = driver.find_elements(AppiumBy.XPATH, xpath)
        elements=WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((AppiumBy.XPATH, xpath)))
        # desc_list = [elem.get_attribute("content-desc") for elem in elements]
        for elem in elements:
            try:
                desc=elem.get_attribute("content-desc")
            except:
                break

            date=""

            # pattern = r'^(笔记|视频|直播)\s+(.+?)\s+来自\s*(.+?)\s*([\d.]+[万]?)?\s*(赞|人观看)$'
            pattern = r'^(笔记|视频)\s+(.+?)\s+来自\s*(.+?)\s*([\d.]+[万]?)?赞$'
            # print(f"desc:{desc}")
            match = re.match(pattern, desc)
            if not match:
                break

            type_, title, author, likes = match.groups()

            if not likes:
                likes="0"

            # print(f"type_:{type_},title:{title},author:{author},likes:{likes}")
            # 存在就不要放子
            if title in title_ary or title=="" or title is None or type_=='直播' or type_=="":
                continue
            elem.click()
            dsc,share_btn=detail_click_suc(driver)
            if not dsc:
                print(f"详情页不可获取,collect_note_cards:{title}")
                continue
            detailNote=get_detail_info(driver,share_btn,True)
            note_id=detailNote.get("note_id")
            note_type=detailNote.get("note_type")
            comment_num=detailNote.get("comment_num")
            favorites_num=detailNote.get("favorites_num")
            share_link=detailNote.get("share_link")
            date=detailNote.get("date")
            location = detailNote.get("location")
            distance = detailNote.get("distance")
            #退出详情页
            driver.back()
            if not note_id or len(note_id)<5:
                continue
            title_ary.append(title)
            note = {
                "title": title,
                "note_id": note_id,
                "author": author,
                "date": date,
                "like_num": likes,
                "comment_num": comment_num,
                "favorites_num": favorites_num,
                "location": location,
                "distance": distance,
                "note_type": note_type,
                "share_link": share_link
            }
            collected.append(note)
            print(f"已获取{len(collected)}篇,共需要获取{target_count}篇笔记")
            if len(collected) >= target_count:
                return collected

        if  swipe_count>=max_swipe_count:
            break
        # 4. 滚动加载更多
        scroll_small_step(driver, 0.2)
        time.sleep(1)
        swipe_count=swipe_count+1
    return collected
def run(args):
    start_time = time.time()
    driver = get_driver()
    result = {}
    notes=[]
    try:
        found_tab = find_index_tab(driver, "发现")
        if found_tab:
            tab_text = found_tab.get_attribute("content-desc")
            found_tab.click()
            # 确认local页面找到
            if is_on_local(driver, tab_text):
                notes = collect_note_cards(driver, args.limit,35)
                result["notes"] = notes
    except Exception as e:
        print(f"({e})")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    elapsed = time.time() - start_time
    hours, rem = divmod(elapsed, 3600)
    minutes, seconds = divmod(rem, 60)
    print(f"读取[首页>发现]笔记{len(notes)}篇 总耗时: {int(hours):02d}:{int(minutes):02d}:{seconds:05.2f}")