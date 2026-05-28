import sys
import yaml
from core import get_driver,load_config  # 假定你的自定义模块
from PIL import Image
import easyocr
import io
import numpy as np
from . import _WX_INDEX_TAB_KEYWORD_,_EA_READER_
from .wx_commom import get_img_and_text


#判断是否是首页
def index_page_indentify():
    img_np,results=get_img_and_text()
    h, w = img_np.shape[:2]
    tabs = []
    for (bbox, text, prob) in results:
        # 四个tab的文本在屏幕最下方85%处的
        if text in _WX_INDEX_TAB_KEYWORD_ and bbox[0][1] > h * 0.85:
            # print(f"test: {text.strip()}  bbox[0][0] X:{bbox[0][0]} bbox[0][1] Y:{bbox[0][1]}")
            tabs.append({
                'name': text.strip(),
                'left_up_x': bbox[0][0],
                'left_up_y': bbox[0][1],
                'right_up_x': bbox[1][0],
                'right_up_y': bbox[1][1],
            })
    tabs.sort(key=lambda k: k['left_up_x'])
    return len(tabs)==4,tabs,results