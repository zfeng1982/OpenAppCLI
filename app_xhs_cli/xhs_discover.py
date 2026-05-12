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
        elements = driver.find_elements(AppiumBy.XPATH, xpath)
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
            if not detail_click_suc(driver):
                print(f"详情页不可获取,collect_note_cards:{title}")
                continue
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
            date_pattern = re.compile(r"\d{1,2}-\d{1,2}|\d{4}-\d{1,2}-\d{1,2}|\d+分钟前|\d+小时前|刚刚|今天|昨天|\d+天前")
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
                                    scroll_small_step(driver,0.2)
                                    time.sleep(0.1)
                                else:
                                    break
                        except:
                            pass
                    driver.back()
            else:
                # 最多下划20次
                for i in range(20):
                    scroll_small_step(driver,0.2)
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
        notes = collect_note_cards(driver, args.limit,35)
        result["notes"] = notes
    except Exception as e:
        print(f"({e})")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    elapsed = time.time() - start_time
    hours, rem = divmod(elapsed, 3600)
    minutes, seconds = divmod(rem, 60)
    print(f"读取[首页>发现]笔记{len(notes)}篇 总耗时: {int(hours):02d}:{int(minutes):02d}:{seconds:05.2f}")