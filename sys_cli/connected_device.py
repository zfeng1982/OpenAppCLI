from core import (
    get_appium_server_url,
    check_appium_server,
    start_appium_service_if_local,
    is_local_url,
    load_config,
    reset_driver
)

def run(driver,args):
    config = load_config()
    device_config = config.get("device", {})
    device_name = device_config.get("deviceName")
    udid = device_config.get("udid")

    print("=== Appium 配置信息 ===")
    print(f"Appium server: {get_appium_server_url()}")
    print(f"配置的设备名: {device_name}")
    if udid:
        print(f"配置的 udid: {udid}")
    else:
        print("未配置 udid，将使用 deviceName 作为标识")

    server_url = get_appium_server_url()
    if is_local_url(server_url):
        start_appium_service_if_local()
    else:
        print("当前为远程 Appium server，请确保服务已手动启动且设备已连接")

    # 检查 Appium server 是否可访问
    if not check_appium_server():
        print("✗ Appium server 无法访问，请检查地址是否正确且服务已启动")
        return

    print("✓ Appium server 可访问")
    print("正在尝试连接设备并获取屏幕信息...")

    # 尝试创建 driver 并获取屏幕尺寸
    try:
        window_size = driver.get_window_size()
        print(f"✓ 设备已成功连接！屏幕尺寸: 宽度={window_size['width']}, 高度={window_size['height']}")
    except Exception as e:
        print(f"✗ 连接设备失败: {e}")
        reset_driver()
        print("请检查：")
        print("  1. 设备是否通过 USB/Wi-Fi 连接到 Appium server 所在机器")
        print("  2. 配置文件中的 deviceName/udid 是否与远程设备匹配")
        print("  3. 设备是否已解锁屏幕并允许 USB 调试")