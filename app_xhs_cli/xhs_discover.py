from core import load_config, check_appium_server, reset_driver
from selenium.common.exceptions import WebDriverException

def run(driver,args):
    config = load_config()
    device_config = config.get("device", {})
    device_name = device_config.get("deviceName", "未配置")
    udid = device_config.get("udid", "未配置")

    print("=== 配置信息 ===")
    print(f"设备名: {device_name}")
    print(f"udid: {udid}")

    print("\n=== Appium server ===")
    server_ok = check_appium_server()
    print("可访问:", "✓" if server_ok else "✗")

    print("\n=== Driver 会话 ===")
    try:
        _=driver.session_id
        print("状态: ✓ 活跃")
    except WebDriverException:
        print("状态: ✗ 已失效")
        reset_driver()
    except Exception as e:
        print(f"状态: - 未创建 ({e})")