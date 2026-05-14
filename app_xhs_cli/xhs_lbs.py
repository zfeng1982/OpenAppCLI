import sys

from .xhs_common import *


# def check_card_structure(frame_element):
#     desc = frame_element.get_attribute("content-desc")
#     print(f"处理卡片: {desc}")
#     try:
#         # 使用后代查找，获取第一个 LinearLayout（通常是内容容器）
#         linear_layouts = frame_element.find_elements(AppiumBy.XPATH, ".//android.widget.LinearLayout")
#         if not linear_layouts:
#             print("  未找到任何 LinearLayout，跳过")
#             return False
#         linear_layout = linear_layouts[0]  # 取第一个
#         # 继续查找其下的 RelativeLayout 和 TextView
#         relative_layouts = linear_layout.find_elements(AppiumBy.XPATH, ".//android.widget.RelativeLayout")
#         text_views = linear_layout.find_elements(AppiumBy.XPATH, ".//android.widget.TextView")
#         linear_compat = linear_layout.find_elements(AppiumBy.XPATH, ".//androidx.appcompat.widget.LinearLayoutCompat")
#
#         # print(f"  RelativeLayout 数量: {len(relative_layouts)}")
#         # print(f"  TextView 数量: {len(text_views)}")
#         # print(f"  linear_compat 数量: {len(linear_compat)}")
#         return len(relative_layouts) > 0 and len(text_views) > 0 and len(linear_compat)>0
#     except Exception as e:
#             print(f"卡片不完整{desc} | 跳过")
#             print(e)
#             pass
#     return False

# def get_address(frame_element):
#     location=""
#     distance=""
#     try:
#         # 使用后代查找，获取第一个 LinearLayout（通常是内容容器）
#         linear_layouts = frame_element.find_elements(AppiumBy.XPATH, ".//android.widget.LinearLayout")
#         if not linear_layouts:
#             print("  未找到任何 LinearLayout，跳过")
#             return False
#         linear_layout = linear_layouts[0]  # 取第一个
#         linear_compat = linear_layout.find_elements(AppiumBy.XPATH, ".//androidx.appcompat.widget.LinearLayoutCompat")
#         if len(linear_compat)>0:
#             linear_compat2 = linear_compat[0].find_elements(AppiumBy.XPATH, ".//androidx.appcompat.widget.LinearLayoutCompat")
#             if len(linear_compat2) > 0:
#                 location_tv = linear_compat2[0].find_element(
#                     AppiumBy.XPATH,
#                     ".//androidx.appcompat.widget.LinearLayoutCompat//android.widget.TextView[1]"
#                 )
#                 location = location_tv.text  # '深圳前海壹方城'
#                 distance_tv = frame_element.find_element(
#                     AppiumBy.XPATH,
#                     ".//androidx.appcompat.widget.LinearLayoutCompat//android.widget.TextView[2]"
#                 )
#                 distance = distance_tv.text  # '1.2km'
#     except Exception as e:
#         location=distance=""
#         print(f"没有Lbs:{location}|{distance}")
#         # print(e)
#         pass
#
#     return location,distance

def collect_note_cards(driver,local,target_count: int,max_swipe_count=10):
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
        elements=WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((AppiumBy.XPATH, xpath)))
        for elem in elements:
            try:
                desc=elem.get_attribute("content-desc")
            except:
                break
            pattern = r'^(笔记|视频)\s+(.+?)\s+来自\s*(.+?)\s*([\d.]+[万]?)?赞$'
            # print(f"desc:{desc}")
            match = re.match(pattern, desc)
            if not match:
                break
            # # 确认是一个完整card
            # if not check_card_structure(elem):
            #     break
            type_, title, author, likes = match.groups()
            if not likes:
                likes="0"
            # print(f"type_:{type_},title:{title},author:{author},likes:{likes}")
            # 存在就不要放子
            if title in title_ary or title=="" or title is None or type_=='直播' or type_=="":
                continue
            # # 获得地址
            # location,distance=get_address(elem)
            # print(f"location:{location},distance:{distance}")
            elem.click()
            dsc,share_btn=detail_click_suc(driver)
            if not dsc:
                print(f"详情页不可获取,collect_note_cards:{title}")
                sys.exit(1)
                # continue
            detailNote=get_detail_info(driver,share_btn,True)
            note_id=detailNote.get("note_id")
            note_type=detailNote.get("note_type")
            comment_num=detailNote.get("comment_num")
            favorites_num=detailNote.get("favorites_num")
            share_link=detailNote.get("share_link")
            date=detailNote.get("date")
            location=detailNote.get("location")
            distance=detailNote.get("distance")
            #退出详情页
            driver.back()
            #详情页是否退出成功
            if not is_on_local(driver, local):
                print(f"详情页返回失败:{title}")
                sys.exit(1)
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
            get_progress(target_count, len(collected))
            if len(collected) >= target_count:
                return collected

        if  swipe_count>=max_swipe_count:
            break
        # 4. 滚动加载更多
        scroll_small_step(driver, 0.2)
        time.sleep(1)
        swipe_count=swipe_count+1
    return collected
def is_on_local(driver,local):
    """
    判断当前是否在深圳页面
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



def run(args):
    start_time = time.time()
    driver = get_driver()
    result = {}
    notes=[]
    tab_text="lbs"
    try:
        found_tab = find_index_tab(driver, "lbs")
        if found_tab:
            tab_text=found_tab.get_attribute("content-desc")
            found_tab.click()
            #确认local页面找到
            if is_on_local(driver,tab_text):
                notes = collect_note_cards(driver,tab_text, args.limit, 35)
                result["notes"] = notes
    except Exception as e:
        print(f"({e})")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    elapsed = time.time() - start_time
    hours, rem = divmod(elapsed, 3600)
    minutes, seconds = divmod(rem, 60)
    print(f"读取[首页>{tab_text}]笔记{len(notes)}篇 总耗时: {int(hours):02d}:{int(minutes):02d}:{seconds:05.2f}")