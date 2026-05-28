import sys
import yaml
from core import get_driver,load_config  # 假定你的自定义模块
from PIL import Image
import easyocr
import io
import numpy as np
from . import _WX_INDEX_TAB_KEYWORD_,_EA_READER_
def get_img_and_text():
    driver = get_driver()
    screen = driver.get_screenshot_as_png()
    img = Image.open(io.BytesIO(screen)).convert('RGB')
    img_np = np.array(img)
    results = _EA_READER_.readtext(img_np)
    return img_np,results
