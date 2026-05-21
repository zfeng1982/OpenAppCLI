import time

from util import *


def send_mark():
    return element_on_clickable(10, (AppiumBy.XPATH, "//android.widget.TextView[@text='发送']"))

def goto_favorites(note_type):
    if note_type == "video":
        ele = element_located(1, (AppiumBy.XPATH, "//android.widget.Button[@index=1 and count(child::*) = 2 "
                                                  " and child::*[1][self::android.widget.ImageView and @index=0] "
                                                  " and child::*[2][self::android.widget.TextView and @index=1] "
                                                  "]"), False)
    else:
        ele = element_located(1, (AppiumBy.XPATH, "//android.widget.Button[@index=2 and count(child::*) = 2 "
                                                  " and child::*[1][self::android.widget.ImageView and @index=0] "
                                                  " and child::*[2][self::android.widget.TextView and @index=1] "
                                                  "]"), False)
    if ele:
        ele.click()
        return True
    return False

# starts-with(@text, '评论')
def goto_like(note_type):
    if note_type == "video":
         ele=element_located(5, (AppiumBy.XPATH, "//android.widget.LinearLayout[@index=0 and count(child::*) = 2 "
                                                             " and child::*[1][self::android.widget.ImageView and @index=0] "
                                                             " and child::*[2][self::android.widget.TextView and @index=1  ] "
                                                            "  and parent::android.widget.LinearLayout[@index=1]"
                                                             "]"),False)
    else:
        ele= element_located(5, (AppiumBy.XPATH, "//android.widget.Button[@index=1 and count(child::*) = 2 "
                                            " and child::*[1][self::android.widget.ImageView and @index=0] "
                                            " and child::*[2][self::android.widget.TextView and @index=1  ] "
                                            "]"),False)
        # android.widget.LinearLayout[
        #     @index=0
        #     and count(child::*) = 2
        #     and child::*[1][self::android.widget.ImageView and @index=0]
        #     and child::*[2][self::android.widget.TextView and @index=1 and not(@text='说点什么...') and not(@text='公开可见')]
        #     and parent::android.widget.LinearLayout[@index=1]
        # ]
    if ele:
        ele.click()
        return True
    return False


# python openappcli.py xhs-interaction --note_id "69f13c090000000023017c85" --note_type normal --action like
# python openappcli.py xhs-interaction --note_id "69435de2000000001e039058" --note_type video --action favorites
# python openappcli.py xhs-interaction --note_id "69435de2000000001e039058" --note_type video --action like
# python openappcli.py xhs-interaction --note_id "69c3e9b4000000001f00627c" --note_type video --action like
def run(args):
    try:
        driver = get_driver()
        deep_link_url = f"xhsdiscover://item/{args.note_id}?type={args.note_type}"
        driver.execute_script('mobile: deepLink', {'url': f'{deep_link_url}', })
        result=False
        if args.action=="like":
            result=goto_like(args.note_type)
        else:
            result=goto_favorites(args.note_type)
        if result:
            print("✅ 操作成功")
        else:
            print("❎ 操作失败")
    except Exception as e:
        print(f"run错误: {e}")
        sys.exit(2)


