import sys
import time

import yaml
from core import get_driver,load_config  # 假定你的自定义模块
from PIL import Image
import easyocr
import io
import numpy as np
from . import _WX_INDEX_TAB_KEYWORD_,_EA_READER_
from .wx_button_pos import get_click_pos
from .wx_commom import get_img_and_text
from .wx_page_identify import friend_chat_page_indentify, index_page_indentify

_wx_interval_time=1

def switch_text_input(img_np, read_txt):
    # for (bbox, text, prob) in read_txt:
    #     print(text)
    print("XXXXXXXXX")

def send_msg(driver,msg,img_np, read_txt):
       # 先切换成文字输入
       switch_text_input(img_np, read_txt)

       # # 还是要先点击一下,再切换输入法
       # driver.tap([(get_click_pos("input_box_pos"))])
       # time.sleep(0.5)
       # # 切换这个输入法才能实现全选功能
       # driver.execute_script('mobile: shell', {
       #     'command': 'settings',
       #     'args': ['put', 'secure', 'default_input_method', load_config().get("IME")]
       # })
       # time.sleep(1)
       # driver.press_keycode(29, 28672)
       # time.sleep(0.5)
       # driver.press_keycode(67)
       # text = "什么时候回家!"
       # driver.set_clipboard_text(text)
       # time.sleep(0.5)
       # # 粘贴
       # driver.press_keycode(50, 28672)
       # time.sleep(1)
       # # 切换回来,把输入法收起来才能正确找到发送按钮
       # driver.execute_script('mobile: shell', {
       #     'command': 'settings',
       #     'args': ['put', 'secure', 'default_input_method', "io.appium.settings/.UnicodeIME"]
       # })
       # time.sleep(0.5)
       # driver.tap([(get_click_pos("send_button_pos"))])
       return True

def run(args):
    driver = get_driver()
    is_send_suc=False
    try:
        #判断是否是好友聊天界面
        img_np, read_txt = get_img_and_text()
        friend=args.friend
        if  friend_chat_page_indentify(friend, img_np, read_txt):
            print(f"👍 微信为当前好友[{friend}]聊天界面")
            is_send_suc=send_msg(friend, args.msg, img_np, read_txt)
        else:
            print(f"⏳ 微信为非当前好友[{friend}]聊天界面,尝试返回微信首页")
            #不是好友聊天界面，点返回到首页
            isIndex, _, read_txt = index_page_indentify(img_np,read_txt)
            # 不是首页，试着点一下返回
            if not isIndex:
                driver.back()
                time.sleep(_wx_interval_time)
                isIndex,img_np,read_txt=index_page_indentify()
                # 返回后还不是首页则直接退出吧
                if not isIndex:
                    print("⚠️为保证执行安全，请在手机上手动切换到微信首页")
                    return
            #选择好友
            for i,(bbox, text, prob) in enumerate(read_txt):
                if text == friend and i+1< len(read_txt):
                   next_bbox, next_text, next_prob = read_txt[i + 1]
                   h, w = img_np.shape[:2]
                   # print(f"next_bbox[1][0]W:{next_bbox[1][0]} w:{w} bbox[0][1]Y：{bbox[0][1]} | next_bboxY {next_bbox[0][1]}")
                   # 昵称称和日期Y坐标偏移不超过10，并且日期在屏幕最左边95%处
                   if next_bbox[1][0]/w>0.95 and abs(next_bbox[0][1]- bbox[0][1])<10:
                       center_x = (bbox[0][0] + bbox[2][0]) / 2   # (100 + 300) / 2 = 200
                       center_y = (bbox[0][1] + bbox[2][1]) / 2   # (200 + 250) / 2 = 225
                       driver.tap([(center_x, center_y)])
                       time.sleep(_wx_interval_time)
                       # 确认下是否进入了聊天界面
                       img_np_chat, read_txt_chat = get_img_and_text()
                       if friend_chat_page_indentify(friend, img_np_chat, read_txt_chat):
                            print(f"微信已切换到当前好友[{friend}]聊天界面")
                            is_send_suc=send_msg(friend, args.msg, img_np_chat, read_txt_chat)
                       break

        print("✅  消息发送成功" if is_send_suc else "❌  消息发送失败")

        # 发送消息
        # driver.tap([(get_click_pos("send_button_pos"))])
        # 全选 (Ctrl + A) driver.press_keycode(29, 28672)
        # 粘贴 (Ctrl + V) driver.press_keycode(50, 28672)
        # 删除 driver.press_keycode(67)

        # for (bbox, text, prob) in read_txt:
        #    if text=="爸爸":
        #        center_x = (bbox[0][0] + bbox[2][0]) / 2   # (100 + 300) / 2 = 200
        #        center_y = (bbox[0][1] + bbox[2][1]) / 2   # (200 + 250) / 2 = 225
        #        driver.tap([(center_x, center_y)])
        #        time.sleep(0.5)
        #
        #        # 还是要先点击一下,再切换输入法
        #        driver.tap([(get_click_pos("input_box_pos"))])
        #        time.sleep(0.5)
        #        # 切换这个输入法才能实现全选功能
        #        driver.execute_script('mobile: shell', {
        #            'command': 'settings',
        #            'args': ['put', 'secure', 'default_input_method', load_config().get("IME")]
        #        })
        #        time.sleep(1)
        #        driver.press_keycode(29, 28672)
        #        time.sleep(0.5)
        #        driver.press_keycode(67)
        #        text = "什么时候回家!"
        #        driver.set_clipboard_text(text)
        #        time.sleep(0.5)
        #        # 粘贴
        #        driver.press_keycode(50, 28672)
        #        time.sleep(1)
        #        # 切换回来,把输入法收起来才能正确找到发送按钮
        #        driver.execute_script('mobile: shell', {
        #            'command': 'settings',
        #            'args': ['put', 'secure', 'default_input_method', "io.appium.settings/.UnicodeIME"]
        #        })
        #        time.sleep(0.5)
        #        driver.tap([(get_click_pos("send_button_pos"))])




    except Exception as e:
        print(f"发生未知错误: {e}")
        sys.exit(1)
