import sys
import yaml
from core import get_driver,load_config  # 假定你的自定义模块
from PIL import Image
import easyocr
import io
import numpy as np
from . import _WX_INDEX_TAB_KEYWORD_,_WX_CONF_PATH_
from .wx_page_identify import index_page_indentify


# bbox 用二维数组表示，每个元素是一个角的 [x, y] 坐标：
#  bbox[0]                  bbox[1]
#          ┌──────────────┐
#          │     占位      │
#          └──────────────┘
#  bbox[3]                 bbox[2]
#
# bbox = [
#     [x1, y1],   # bbox[0]  左上角
#     [x2, y2],   # bbox[1]  右上角
#     [x3, y3],   # bbox[2]  右下角
#     [x4, y4]    # bbox[3]  左下角
# ]
# 访问方式：
# ┌─────────────────────────────────────────┐
# │                                         │
# │   bbox[0] = [x1, y1]  左上角             │
# │        ↓                                │
# │   bbox[0][0] = x1  (横坐标)              │
# │   bbox[0][1] = y1  (纵坐标)              │
# │                                         │
# │   bbox[1] = [x2, y2]  右上角             │
# │   bbox[1][0] = x2                       │
# │   bbox[1][1] = y2                       │
# │                                         │
# │   bbox[2] = [x3, y3]  右下角             │
# │   bbox[2][0] = x3                       │
# │   bbox[2][1] = y3                       │
# │                                         │
# │   bbox[3] = [x4, y4]  左下角             │
# │   bbox[3][0] = x4                       │
# │   bbox[3][1] = y4                       │
# └─────────────────────────────────────────┘
# 实际例子：
# bbox = [
#     [100, 200],   # bbox[0]  左上
#     [300, 200],   # bbox[1]  右上
#     [300, 250],   # bbox[2]  右下
#     [100, 250]    # bbox[3]  左下
# ]
# 计算中心点：
# center_x = (bbox[0][0] + bbox[2][0]) / 2   # (100 + 300) / 2 = 200
# center_y = (bbox[0][1] + bbox[2][1]) / 2   # (200 + 250) / 2 = 225
# 计算宽度：
# width = bbox[2][0] - bbox[0][0]   # 300 - 100 = 200
# 计算高度：
# height = bbox[2][1] - bbox[0][1]  # 250 - 200 = 50



def read_raw_config(device_id):
    """读取原始字符串配置"""
    with open(_WX_CONF_PATH_, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    if not data['pos'] or not data['pos'][device_id]:
        return None
    return data['pos'][device_id]


def get_click_pos_conf():
    driver = get_driver()
    device_name = driver.capabilities.get('deviceName')
    if not device_name or len(device_name)<5:
        print("读取不到deviceName,请确认config.yaml是配置正确")
        sys.exit(1)

    raw_config= read_raw_config(device_name)
    if  raw_config and len(raw_config)==7:
       # print("从配置中读取click pos")
       return raw_config
    is_index,tabs,_=index_page_indentify()
    if len(tabs)!=4:
        print("请确认微信已切换到聊天列表tab")
        return False,None
    # 计算语音和文字输入切换按键的坐标,直接使用"微信"两个字左边上角的坐标即可
    switch_button_pos=(tabs[0].get("left_up_x"),tabs[0].get("left_up_y"))
    # 计算输入框位置,直接用'通讯录'右上角坐
    input_box_pos=(tabs[1].get("right_up_x"),tabs[1].get("right_up_y"))
    # 计算发送按刍位置,直接用'我'右上角坐
    send_button_pos = (tabs[3].get("right_up_x"), tabs[3].get("right_up_y"))
    data = {
        "pos": {
            device_name: {  # 动态设备ID
                "tab_ws_pos": f"{tabs[0].get("left_up_x")},{tabs[0].get("left_up_y")}",
                "tab_address_pos": f"{tabs[1].get("left_up_x")},{tabs[1].get("left_up_y")}",
                "tab_discover_pos": f"{tabs[2].get("left_up_x")},{tabs[2].get("left_up_y")}",
                "tab_self_pos": f"{tabs[3].get("left_up_x")},{tabs[3].get("left_up_y")}",
                "switch_button_pos": f"{switch_button_pos[0]},{switch_button_pos[1]}",
                "input_box_pos": f"{input_box_pos[0]},{input_box_pos[1]}",
                "send_button_pos": f"{send_button_pos[0]},{send_button_pos[1]}",
            }
        }
    }
    with open(_WX_CONF_PATH_, "w", encoding="utf-8") as f:
        yaml.dump(
            data,
            f,
            allow_unicode=True,  # 避免编码问题
            sort_keys=False  # 不自动排序键，保持原结构
        )
    # 从文件中直接获取
    return read_raw_config(device_name)

def get_click_pos(key):
    raw=get_click_pos_conf()
    return tuple(map(int, raw[key].split(',')))
