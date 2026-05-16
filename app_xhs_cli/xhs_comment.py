from util import *


def send_mark():
    return element_on_clickable(10, (AppiumBy.XPATH, "//android.widget.TextView[@text='发送']"))

def input_mark():
    return element_on_clickable(10,(AppiumBy.XPATH, "//android.widget.EditText"),1)


def goto_mark(note_type):
    if note_type=="video":
        return  element_on_clickable(10, (AppiumBy.XPATH, "//android.widget.TextView[@text='说点什么...']"))

    return element_on_clickable(10, (AppiumBy.ACCESSIBILITY_ID, '评论框'))


# python openappcli.py xhs-comment --note_id "6a03f12e000000003503a6b0" --text "不错找个时间去看下" --note_type normal
# python openappcli.py xhs-comment --note_id "6a01920f0000000036033ce7" --text "不错找个时间去看下!!" --note_type video
def run(args):
    driver = get_driver()
    driver.execute_script('mobile: shell', {
        'command': 'settings',
        'args': ['put', 'secure', 'default_input_method', load_config().get("IME")]
    })
    try:
        deep_link_url = f"xhsdiscover://item/{args.note_id}?type={args.note_type}"
        driver.execute_script('mobile: deepLink', { 'url': f'{deep_link_url}',})
        #找到评论输入框,并点击
        goto_mark(args.note_type)
        #点击弹出的输入框架内
        edit_text=input_mark()
        edit_text.clear()
        edit_text.send_keys(args.text)
        send_mark()
        print("评论已发布")
    except Exception as e:
        print(f"run错误: {e}")
        sys.exit(2)


