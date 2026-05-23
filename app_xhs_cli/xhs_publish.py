import sys
import random
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException

from util import element_located_all
from .xhs_common import *


def select_images_and_next(driver, num_to_select=2,is_one_tap:str=False):
    # 等待图片列表加载
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((AppiumBy.XPATH, "//androidx.recyclerview.widget.RecyclerView"))
    )

    # 获取所有可点击的图片项
    image_items = driver.find_elements(AppiumBy.XPATH,
                                       "//androidx.recyclerview.widget.RecyclerView//android.widget.FrameLayout[@clickable='true']")

    if len(image_items) < num_to_select:
        print(f"只有 {len(image_items)} 张图片，将全部选择")
        num_to_select = len(image_items)

    # 依次点击前 num_to_select 张
    for i in range(num_to_select):
        image_items[i].click()
        print(f"已选择第 {i + 1} 张图片")
        time.sleep(0.3)

    if is_one_tap:
        # 也可以选择一键成片
        one_tap_parent = driver.find_element(AppiumBy.XPATH, "//android.widget.RelativeLayout[.//android.widget.TextView[@text='一键成片']]")
        one_tap_parent.click()
        print("已点击一键成片")
    else:
        # 等待下一步按钮出现并点击
        next_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "下一步"))
        )
        next_btn.click()
        print("已点击下一步(1)")
        next_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.TextView[@text='下一步']"))
        )
        next_btn.click()
        print("已点击下一步(2)")

def add_topic_via_button(driver, topic_keyword,move=True, hint="添加正文或发语音"):
    # 1. 点击「话题」按钮
    topic_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.TextView[@text='话题']"))
    )
    topic_btn.click()
    time.sleep(0.5)

    # 2. 光标定位到正文末尾
    if move:
        body_input = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((AppiumBy.XPATH, f"//android.widget.EditText[@hint='{hint}']"))
        )
        rect = body_input.rect
        end_x = rect['x'] + rect['width'] - 10
        end_y = rect['y'] + rect['height'] // 2
        driver.tap([(end_x, end_y)])
        time.sleep(0.2)

    # 3. 输入关键词
    driver.execute_script("mobile: type", {"text": topic_keyword})
    # time.sleep(2)  # 等待推荐列表刷新

    # 4. 等待推荐列表中出现目标话题（存在即可，不一定可点击）,小红书的这种机制如果话题没有会新增,不会出现找不到话题的情况
    target_xpath = f"//android.widget.TextView[contains(@text, '{topic_keyword}')]"

    element_on_clickable(3, (AppiumBy.XPATH,target_xpath))

    # 5. 点击完成按钮（关闭话题面板）
    done_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.TextView[@text='完成']"))
    )
    done_btn.click()
    time.sleep(0.5)

def fill_and_publish(driver, title_text, body_text, topics=None,hint='添加正文或发语音'):
    """
    自动填写标题、正文，并添加可点击的话题链接（从推荐列表选择）
    :param driver: Appium driver
    :param title_text: 标题
    :param body_text: 正文内容（不含话题）
    :param topics: 话题列表，例如 ["自动化", "小红书"]
    """
    # 1. 填写标题
    title_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.EditText[@hint='添加标题']"))
    )
    title_input.click()
    title_input.clear()
    title_input.send_keys(title_text)
    # 点击空白区域收起键盘（替代hide_keyboard）
    driver.find_element(AppiumBy.XPATH, "//android.widget.ScrollView").click()
    time.sleep(0.5)

    # 2. 填写正文（普通文本）
    body_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((AppiumBy.XPATH, f"//android.widget.EditText[@hint='{hint}']"))
    )

    body_input.click()
    # 如果正文非空，添加一个换行，使话题与正文分行
    if body_text:
        body_input.send_keys(body_text+"\n")

    # 3. 添加话题（可点击的蓝色话题链接）
    if topics:
        for topic in topics:
            add_topic_via_button(driver,topic,False,hint)

def click_write_idea(driver,idea:str,title_text="", body_text="", topics=None):
    """点击“写想法”按钮"""
    element_on_clickable(10, (AppiumBy.XPATH, "//android.widget.TextView[@text='写想法']"))
    print("✅ 已点击“写想法”")
    try:
        # 等待并定位到编辑框（对应 XML 中的 EditText）
        idea_input=element_on_clickable(10, (AppiumBy.XPATH, "//android.widget.EditText"))
        idea_input.clear()  # 清空已有内容（如果有）
        idea_input.send_keys(idea)
        print(f"✅ 已在“写想法”中输入：{idea}")

        # 等待并点击“下一步”按钮（位于底部中央）
        element_on_clickable(10, (AppiumBy.XPATH,"//android.widget.TextView[@text='下一步']"))
        print("✅ 已点击“下一步”")

        # 先等待卡片区域加载完成（以第一个可见卡片为标志）
        element_located(10, (AppiumBy.XPATH, "//androidx.recyclerview.widget.RecyclerView"))

        # 每次重新查找所有可点击的卡片
        cards =   element_located_all(10, (AppiumBy.XPATH, "//androidx.recyclerview.widget.RecyclerView//android.view.ViewGroup[@clickable='true']"))
        chosen = random.choice(cards)
        # 尝试点击
        chosen.click()
        # 点击下一步
        next_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (AppiumBy.XPATH, "//android.widget.TextView[@text='下一步' and @content-desc='确认']"))
        )
        next_btn.click()
        print("✅ 卡片选择完成,已点击下一步")
        if title_text or body_text:
            fill_and_publish(driver, title_text, body_text, topics, '展开说说')

    except Exception as e:
        print(f"❌ 操作失败: {e}")
        raise

def select_random_layout_and_next(driver):
    """
    在排版选择界面随机选择一个排版，然后点击“下一步”
    :param driver: Appium driver
    """
    # 等待排版列表区域加载（以标题为标志）
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((AppiumBy.XPATH, "//android.widget.TextView[@text='选择喜欢的排版']"))
    )
    # 等一下吧,这里容易出错
    time.sleep(2)
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # 每次重新获取所有可点击的排版项
            layout_items = driver.find_elements(AppiumBy.XPATH,
                "//androidx.recyclerview.widget.RecyclerView//android.view.ViewGroup[@clickable='true']")
            if not layout_items:
                raise Exception("未找到任何排版选项")

            # 随机选择一个
            chosen = random.choice(layout_items)
            # 获取排版名称用于日志（可选）
            try:
                text_elem = chosen.find_element(AppiumBy.XPATH, ".//android.widget.TextView")
                layout_name = text_elem.text
                print(f"✅ 随机选择排版：{layout_name}")
            except:
                print("✅ 已随机选择一个排版")
            chosen.click()
            break  # 成功则退出重试
        except StaleElementReferenceException:
            print(f"排版元素过期，重试 {attempt+1}/{max_retries}...")
            time.sleep(0.5)
            if attempt == max_retries - 1:
                raise
        except Exception as e:
            print(f"选择排版失败: {e}")
            raise

    # 点击“下一步”按钮
    time.sleep(8)
    next_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.TextView[@text='下一步']"))
    )
    next_btn.click()
    print("✅ 排版完成,已点击“下一步”")

def click_use_button(driver, max_retries=3):
    """
        点击AI生成的正文小结中的“使用”按钮
        通过滚动查找，定位“AI已为你自动生成正文小结”后的“使用”按钮
        """
    # 先滚动到正文区域附近，让AI小结有机会出现
    try:
        body_input = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((AppiumBy.XPATH, "//android.widget.EditText[@hint='添加正文或发语音']"))
        )
        # 从正文输入框的坐标向上滑动，露出上方的AI区域
        rect = body_input.rect
        start_y = rect['y'] + rect['height'] // 2
        driver.swipe(540, start_y, 540, start_y - 600, 500)
        time.sleep(1)
        print("已滚动至文章主体区域上方")
    except Exception as e:
        print(f"初始滚动失败: {e}")

    for attempt in range(max_retries):
        try:
            # 使用相对XPath：找到“AI已为你自动生成正文小结”后面的兄弟元素“使用”
            use_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.XPATH,
                    "//android.widget.TextView[@text='AI已为你自动生成正文小结']/following-sibling::android.widget.TextView[@text='使用']"))
            )
            use_btn.click()
            print("✅ 已点击“使用”按钮")
            return
        except (StaleElementReferenceException, NoSuchElementException) as e:
            print(f"⚠️ 未找到或元素过期，重试 {attempt+1}/{max_retries}...")
            # 尝试向上滑动，使该区域完全显示
            driver.swipe(500, 1500, 500, 800, 500)
            time.sleep(1)
            if attempt == max_retries - 1:
                raise

def click_long_content(driver,title:str,content:str,topics):
    """点击“写长文”按钮"""
    long_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.TextView[@text='写长文']"))
    )
    long_btn.click()
    print("✅ 已点击“写长文”")
    """
       在“写长文”页面输入标题和正文，然后点击“一键排版”
       :param driver: Appium driver
       :param title_text: 标题文本
       :param body_text: 正文文本
       """
    # 1. 输入标题（第二个 EditText，hint="输入标题"）
    title_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.EditText[@hint='输入标题']"))
    )
    title_input.click()
    title_input.clear()
    title_input.send_keys(title)
    print(f"✅ 已输入标题：{title}")

    # 2. 输入正文（第一个 EditText，hint包含"粘贴到这里"）
    body_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.EditText[contains(@hint, '粘贴到这里')]"))
    )
    body_input.click()
    body_input.clear()
    body_input.send_keys(content)
    print(f"✅ 已输入正文：{content}")

    # 3. 点击“一键排版”按钮（可能初始为不可点击，等待其启用）
    format_btn = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.TextView[@text='一键排版']"))
    )
    format_btn.click()
    print("✅ 已点击“一键排版”")
    # 这个时间特别长
    time.sleep(10)
    #随机选择一个排版
    select_random_layout_and_next(driver)
    #使用AI生成的小结
    time.sleep(2)
    click_use_button(driver)
    time.sleep(0.5)
    driver.execute_script("mobile: type", {"text": '\n'})
    #添加话题（可点击的蓝色话题链接）
    if topics:
        # 输入一个换行,分隔正文和话题
        for topic in topics:
            add_topic_via_button(driver, topic,False)

# python openappcli.py xhs-publish album --count 5  --title "英国法院裁定三星向中兴赔偿" --content "从公开消息看，中兴通讯在德国、UPC和巴西等法院判决获得了支持。从外媒报道看，从2025年年初，德国、UPC、巴西等法院陆续判决，均支持中兴立场和报价。" --topics "新能源|五一假期|人山人海|辛芷蕾"
def run(args):
    driver = get_driver()
    try:
        type = args.type
        #1.点击+
        driver.find_element(AppiumBy.ACCESSIBILITY_ID, "发布").click()
        wait = WebDriverWait(driver, 10)
        content = args.content.replace('\\n', '\n') if args.content else "" # 字符串或 None
        title = args.title  # 字符串或 None
        topics = args.topics  # 字符串或 None
        arytopics=topics.split("|") if topics is not None else []
        #2.选择发布方式'从相册选择'或'写文字'
        while True:
            if  type=="album":
                image_count = args.count  # 整数，默认1
                one_tap = args.one_tap  # True/False
                # print(f" image_count:{image_count} one_tap:{one_tap} title:{title} content:{content} topics:{topics}")
                # 从相册选择
                album_btn = wait.until(EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.TextView[@text='从相册选择']")))
                album_btn.click()
                # 3.选择图片并点击下一步
                select_images_and_next(driver, image_count,one_tap)
                # 4.输入标题,正文,话题
                fill_and_publish(driver, title, content, arytopics)
                # .发布
                publish_btn = wait.until( EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.Button[@text='发布笔记']")))
                publish_btn.click()
                print("✅ 相册笔记发布成功")
                break
            #点击写文字
            if type == "text":
                write_text_btn=wait.until(EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.TextView[@text='写文字']") ))
                write_text_btn.click()
                if args.txttype=='thinking':
                    #写入想法和展示开说说
                    click_write_idea(driver,args.itxt,title,content,arytopics)
                    # .发布
                    publish_btn = wait.until( EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.Button[@text='发布笔记']")))
                    publish_btn.click()
                    print("✅ 想法笔记发布成功")
                elif args.txttype=='longtxt':
                    click_long_content(driver,title,content,arytopics)
                    # .发布
                    publish_btn = wait.until(
                        EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.Button[@text='发布笔记']")))
                    # time.sleep(1)
                    publish_btn.click()
                    print("✅ 长文本笔记发布成功")
                break
            # 取消
            cancel_btn =wait.until(EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.TextView[@text='取消']")))
            cancel_btn.click()
            break
    except Exception as e:
        print(f"发生未知错误: {e}")
        sys.exit(1)
