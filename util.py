import sys
import time

from core import *
import inspect
def element_located(timeout,locator: tuple[str, str],is_exit=True):
    # 等待元素出现在DOM中（即页面源码中存在该元素），但不一定可见或可交互。
    # 只要元素存在（哪怕被遮挡、透明度为0、display: none、disabled等），就会返回元素。
    # 通常用于等待元素加载完成，但后续还需要进一步判断可见性或可点击性。
    ele = None
    try:
        ele = WebDriverWait(get_driver(), timeout).until(EC.presence_of_element_located((locator[0], locator[1])))
    except Exception as e:
        method_name = inspect.currentframe().f_back.f_code.co_name
        print(f"等待超时,timeout:{timeout},exit:{is_exit},mark:{method_name},path:{locator[1]}")
        if ele is None and is_exit:
            sys.exit(1)
    return ele

def element_clickable(timeout,locator: tuple[str, str],is_exit=True):
    # 等待元素满足以下所有条件：
    # 元素存在于 DOM 中
    # 元素可见（visibility：宽高 > 0，且不被隐藏）
    # 元素可点击（enabled 并且未被禁用）
    # 适用于按钮、链接等需要点击的元素
    ele =None
    try:
       ele =WebDriverWait(get_driver(), timeout).until(EC.element_to_be_clickable((locator[0], locator[1])))
    except Exception as e:
        if ele is None and is_exit:
            method_name = inspect.currentframe().f_back.f_code.co_name
            print(f"等待超时,timeout:{timeout},exit:{is_exit},mark:{method_name},path:{locator[1]}")
            sys.exit(1)
    return ele

def element_on_clickable(timeout,locator: tuple[str, str],sleep_time=0,is_exit=True):
    # 等待元素满足以下所有条件：
    # 元素存在于 DOM 中
    # 元素可见（visibility：宽高 > 0，且不被隐藏）
    # 元素可点击（enabled 并且未被禁用）
    # 适用于按钮、链接等需要点击的元素
    ele =None
    try:
       ele =WebDriverWait(get_driver(), timeout).until(EC.element_to_be_clickable((locator[0], locator[1])))
       ele.click()
       if sleep_time>0:
           time.sleep(sleep_time)
    except Exception as e:
        if ele is None and is_exit:
            method_name = inspect.currentframe().f_back.f_code.co_name
            print(f"等待超时,timeout:{timeout},exit:{is_exit},mark:{method_name},path:{locator[1]}")
            sys.exit(1)
    return ele
