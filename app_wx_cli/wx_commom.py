import sys
from typing import Any

import yaml
from numpy import ndarray, dtype
from datetime import datetime

from core import get_driver,load_config  # 假定你的自定义模块
from PIL import Image
import easyocr
import io
import numpy as np
from . import _WX_INDEX_TAB_KEYWORD_,_EA_READER_
def get_img_and_text() :
    driver = get_driver()
    screen = driver.get_screenshot_as_png()
    # # 生成文件名：时间精确到毫秒
    # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # 去掉最后3位微秒，保留毫秒
    # filename = f"screenshot_{timestamp}.png"
    # with open(filename, "wb") as f:
    #     f.write(screen)
    # print(f"截图已保存: {filename}")
    img = Image.open(io.BytesIO(screen)).convert('RGB')
    img_np = np.array(img)
    read_txt = _EA_READER_.readtext(img_np)
    return img_np,read_txt
