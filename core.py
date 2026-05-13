import subprocess
from pathlib import Path
from typing import Optional
import time
import yaml
from appium.webdriver.appium_service import AppiumService
from appium import webdriver as appium_webdriver
from appium.options.common.base import AppiumOptions
from selenium.common.exceptions import WebDriverException
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib.request
from urllib.error import URLError
import json
import os
import re

_driver = None
_config = None
_appium_service = None      # 用于管理本地 Appium 服务的全局实例


def get_config_path():
    """获取配置文件路径，优先级：
    1. 当前工作目录下的 config.yaml
    2. 当前工作目录下的 .openappcli.py/config.yaml
    3. 用户家目录下的 .openappcli.py/config.yaml
    """
    cwd = Path.cwd()
    # 优先级1: ./config.yaml
    config_path = cwd / "config.yaml"
    if config_path.exists():
        return config_path
    # 优先级2: ./.openappcli.py/config.yaml
    config_path = cwd / ".openappcli.py" / "config.yaml"
    if config_path.exists():
        return config_path
    # 优先级3: ~/.openappcli.py/config.yaml
    config_path = Path.home() / ".openappcli.py" / "config.yaml"
    if config_path.exists():
        return config_path
    return None

def load_config(config_path=None):
    """加载 YAML 配置，如果未指定路径则自动查找"""
    if config_path is None:
        config_path = get_config_path()
    if config_path is None:
        print("错误：未找到配置文件，请确保以下位置之一存在配置文件：")
        print("  - ./config.yaml")
        print("  - ./.openappcli.py/config.yaml")
        exit(1)
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_appium_server_url():
    """从配置文件读取 Appium server 地址"""
    config = load_config()
    server_cfg = config.get("appium_server", {})
    url = server_cfg.get("url", "http://127.0.0.1:4723")
    return url.rstrip('/')


def is_local_url(url):
    """判断 URL 是否为本地地址（127.0.0.1 或 localhost 或 ::1），不使用 urlparse"""
    # 去掉协议部分 (http:// 或 https://)
    if '://' in url:
        host_part = url.split('://', 1)[1]
    else:
        host_part = url

    # 去掉端口和路径（取第一个 '/' 或 ':' 之前的内容）
    # 先处理可能包含的路径
    if '/' in host_part:
        host_part = host_part.split('/', 1)[0]
    # 再处理端口
    if ':' in host_part and not (host_part.startswith('[') and ']' in host_part):
        # 非 IPv6 地址格式，直接按冒号切分
        host_part = host_part.split(':', 1)[0]
    elif host_part.startswith('[') and ']' in host_part:
        # IPv6 地址格式如 [::1]:8080
        host_part = host_part.split(']', 1)[0].lstrip('[')

    # 判断是否为本地回环地址
    return host_part in ('127.0.0.1', 'localhost', '::1')


def start_appium_service_if_local():
    """如果配置的 Appium server 是本地地址且服务未运行，则自动启动"""
    url = get_appium_server_url()
    if not is_local_url(url):
        return False   # 非本地地址，不自动启动

    global _appium_service
    if _appium_service is None:
        _appium_service = AppiumService()

    if _appium_service.is_running:
        print("本地 Appium 服务已在运行")
        return True

    print("正在启动本地 Appium 服务...")
    _appium_service.start()
    # 等待服务就绪
    import time
    timeout = 10
    start_time = time.time()
    while not _appium_service.is_running and (time.time() - start_time) < timeout:
        time.sleep(0.5)
    if _appium_service.is_running:
        print(f"本地 Appium 服务已启动，监听 {url}")
        return True
    else:
        print("无法启动本地 Appium 服务，请手动检查")
        return False


def get_attached_devices():
    """通过 adb 获取已连接的设备 udid 列表"""
    try:
        result = subprocess.run(["adb", "devices"], capture_output=True, text=True, check=True)
        lines = result.stdout.strip().split("\n")
        devices = []
        for line in lines[1:]:
            if line.strip() and "device" in line and "offline" not in line:
                udid = line.split()[0]
                devices.append(udid)
        return devices
    except (subprocess.SubprocessError, FileNotFoundError):
        print("无法运行 adb，请确保 ADB 已安装并配置 PATH")
        return []


def get_driver(app_package: Optional[str] = None, app_activity: Optional[str] = None):
    global _driver
    if _driver is None:
        config = load_config()
        device_config = config.get("device", {})
        if not device_config:
            print("配置文件中缺少 device 信息")
            exit(1)

        # 创建 AppiumOptions 对象
        options = AppiumOptions()

        # 设置必要参数
        options.platform_name = device_config.get("platformName", "Android")
        options.device_name = device_config.get("deviceName")
        options.set_capability('newCommandTimeout', 300)
        options.grant_permissions = True
        if not options.device_name:
            print("配置文件中 device.deviceName 不能为空")
            exit(1)
        options.automation_name = device_config.get("automationName", "UiAutomator2")
        options.no_reset = device_config.get("noReset", True)
        if "newCommandTimeout" in device_config:
            options.new_command_timeout = device_config["newCommandTimeout"]

        # 可选参数
        if "udid" in device_config:
            options.udid = device_config["udid"]
        if "unicodeKeyboard" in device_config:
            options.set_capability("unicodeKeyboard", device_config["unicodeKeyboard"])
        if "resetKeyboard" in device_config:
            options.set_capability("resetKeyboard", device_config["resetKeyboard"])

        # 传递其他自定义 capabilities（如 appPackage 等，虽然 launch 时才会用到，但可以提前设置）
        for key, value in device_config.items():
            if key not in ["platformName", "deviceName", "automationName", "noReset", "newCommandTimeout", "udid", "unicodeKeyboard", "resetKeyboard"]:
                options.set_capability(key, value)

        if app_package and app_activity:
            options.app_package = app_package
            options.app_activity = app_activity
        server_url = get_appium_server_url()
        try:
            _driver = appium_webdriver.Remote(command_executor=server_url, options=options)
            print(f"已连接设备: {options.device_name} (Appium server: {server_url})")
            if app_package and app_activity:
                _driver.activate_app(options.app_package)
                print(f"激活应用: {app_package}")

        except WebDriverException as e:
            print(f"创建 driver 失败: {e}")
            exit(1)
    return _driver

def reset_driver():
    """重置 driver（用于异常恢复）"""
    global _driver
    if _driver:
        try:
            _driver.quit()
        except:
            pass
        _driver = None
def swipe_left(driver, duration=300):
    """左滑操作"""
    size = driver.get_window_size()
    start_x = size['width'] * 0.8
    end_x = size['width'] * 0.2
    y = size['height'] * 0.5
    driver.swipe(start_x, y, end_x, y, duration)
    time.sleep(0.8)  # 等待动画和加载

def swipe_left_at_bottom(driver, duration=300, y_ratio=0.85):
    """
    在屏幕底部执行左滑操作

    :param driver:   Appium driver
    :param duration: 滑动持续时间（毫秒）
    :param y_ratio:  垂直位置比例，0.85 表示屏幕高度 85% 的位置（底部区域）
    """
    size = driver.get_window_size()
    start_x = size['width'] * 0.8
    end_x = size['width'] * 0.2
    y = size['height'] * y_ratio
    driver.swipe(start_x, y, end_x, y, duration)
    time.sleep(0.8)  # 等待动画和加载

def swipe_right(driver, duration=300):
    """右滑操作"""
    size = driver.get_window_size()
    start_x = size['width'] * 0.2      # 从左侧开始
    end_x = size['width'] * 0.8        # 滑动到右侧
    y = size['height'] * 0.5
    driver.swipe(start_x, y, end_x, y, duration)
    time.sleep(0.8)  # 等待动画和加载

def save_full_screenshot(driver, save_dir="screenshots", prefix="screenshot"):

    """
    直接保存当前屏幕的全屏截图到指定目录
    """
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    filename = f"{prefix}.png"
    filepath = os.path.join(save_dir, filename)
    # 保存截图
    driver.get_screenshot_as_file(filepath)
    return filepath
def check_appium_server():
    """检查配置的 Appium server 是否可访问（使用标准库，无需 requests）"""
    url = get_appium_server_url()
    try:
        req = urllib.request.Request(f"{url}/status", method="GET")
        with urllib.request.urlopen(req, timeout=3) as response:
            if response.status != 200:
                return False
            data = json.loads(response.read().decode('utf-8'))
            return data.get("value", {}).get("ready") is True
    except (URLError, json.JSONDecodeError, KeyError):
        return False

# 轻微滚动屏幕
def scroll_small_step(driver, step_ratio=0.1, up=True):
    """滚动 step_ratio 屏幕高度的距离，up=True 表示向上滑动（加载更多）"""
    size = driver.get_window_size()
    h = size["height"]
    w = size["width"]
    start_x = w // 2
    start_y = h // 2
    offset = int(h * step_ratio)
    end_y = start_y - offset if up else start_y + offset
    driver.swipe(start_x, start_y, start_x, end_y, duration=200)


def scroll_down_screens(driver, screens=1, swipe_duration=300):
    """
    在当前页面向下滚动两屏（每次滑动屏幕高度的 80%）
    :param driver: Appium WebDriver 实例
    :param screens: 要滚动的屏数（默认1）
    :param swipe_duration: 每次滑动持续时间（毫秒）
    """
    # 获取屏幕尺寸
    size = driver.get_window_size()
    start_x = size['width'] // 2
    start_y = int(size['height'] * 0.8)  # 从屏幕 80% 高度处开始
    end_y = int(size['height'] * 0.2)  # 滑动到屏幕 20% 高度处

    for _ in range(screens):
        success = False
        for retry in range(3):  # 重试最多3次
            try:
                driver.swipe(start_x, start_y, start_x, end_y, swipe_duration)
                success = True
                break
            except Exception as e:
                print(f"滑动失败，重试 {retry + 1}: {e}")
                time.sleep(2)
                # 可选：重新获取屏幕尺寸（如果分辨率改变）
                size = driver.get_window_size()
                start_y = int(size['height'] * 0.8)
                end_y = int(size['height'] * 0.2)
        if not success:
            raise Exception("滑动多次失败，连接可能已断开")
        time.sleep(2)  # 等待内容加载


def back_index(driver, xpath_texts: list, max_attempts=10):
    """
    通过多次返回操作回到首页，直到页面同时包含所有指定的文本元素。

    :param driver: Appium driver 实例
    :param xpath_texts: 需要同时存在的文本列表，例如 ['首页', '推荐']
    :param max_attempts: 最大尝试次数（返回操作的次数）
    """
    # 如果 driver 无效，尝试重连
    if not driver or not driver.session_id:
        driver.quit()
        driver = get_driver()
        if not driver:
            print("无法创建 driver 会话")
            return

    for attempt in range(max_attempts):
        # 每次循环开始时检查会话有效性
        try:
            _ = driver.current_activity  # 轻量级操作，验证会话
        except WebDriverException:
            print("会话失效，尝试重新连接...")
            driver.quit()
            driver = get_driver()
            if not driver:
                print("重连失败，退出 back_index")
                return
            continue

        # 检查所有指定的文本是否同时存在
        all_found = True
        try:
            for text in xpath_texts:
                elements = driver.find_elements(
                    AppiumBy.XPATH, f"//android.widget.TextView[@text='{text}']"
                )
                if not elements:
                    all_found = False
                    break
        except WebDriverException as e:
            # 查找元素时发生连接异常，认为会话可能失效，下次循环会重连
            print(f"查找首页标签时连接异常: {e}，将在下一次循环重试")
            continue

        # 如果所有文本都存在，则认为已回到首页，直接返回
        if all_found:
            return

        # 否则执行返回操作，并等待页面刷新
        try:
            driver.back()
            time.sleep(0.5)
        except WebDriverException as e:
            print(f"返回操作失败: {e}")

    print(f"⚠️ 尝试 {max_attempts} 次后仍未回到首页，请手动检查")

def click_expand_by_coordinate(driver,text, offset_ratio=0.2):
    """
    通过 XPath 找到可点击的“展开” TextView，
    获取其 bounds，计算点击坐标（右下角向左偏移），然后模拟点击。
    """
    try:
        # 定位包含“展开”且可点击的 TextView
        expand_elem=WebDriverWait(driver, 5).until(EC.presence_of_element_located((AppiumBy.XPATH, f"//android.widget.TextView[contains(@text, '{text}') and @clickable='true']")))
        bounds = expand_elem.get_attribute("bounds")
        if not bounds:
            return False

        # 解析 bounds 字符串，格式为 "[x1,y1][x2,y2]"
        coords = list(map(int, re.findall(r"\d+", bounds)))
        if len(coords) != 4:
            return False
        x1, y1, x2, y2 = coords

        # 计算点击坐标：x 取右侧向左偏移 offset_ratio 宽度，y 取中间
        width = x2 - x1
        click_x = x2 - int(width * offset_ratio)
        click_y = (y1 + y2) // 2

        # 模拟点击
        driver.tap([(click_x, click_y)], duration=50)
        # print(f"点击展开成功，坐标({click_x}, {click_y})")
        return True
    except Exception as e:
        # print(f"'{text}'不存,不能点击")
        return False

def check_current_page(driver, xpath_texts: list):
    try:
        # 如果 driver 无效，尝试重连
        if not driver or not driver.session_id:
            driver.quit()
            driver = get_driver()
            if not driver:
                print("无法创建 driver 会话")
                return False
        for text in xpath_texts:
            elements = driver.find_elements( AppiumBy.XPATH, f"//android.widget.TextView[@text='{text}']")
            if not elements:
                return False
        return True
    except WebDriverException as e:
        print()
    return  False


