
import time
import json

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .xhs_common import collect_note_cards




def run(driver,args):
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

            notes=collect_note_cards(driver,args.limit)
            print(f"notes len:{len(notes)}")
            result["notes"] = notes
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"发生未知错误: {e}")

