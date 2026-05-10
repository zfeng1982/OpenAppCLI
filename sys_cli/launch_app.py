import sys
from core import load_config, get_driver, reset_driver


def run(args):
    driver=None
    app_name = args.app_name
    config = load_config()
    apps = config.get("apps", {})
    if app_name not in apps:
        print(f"未知应用: {app_name}，请在配置文件的 'apps' 下定义")
        sys.exit(1)
    app_caps = apps[app_name]
    required_keys = ["appPackage", "appActivity","description"]
    for key in required_keys:
        if key not in app_caps:
            print(f"应用 {app_name} 配置缺少 {key}")
            sys.exit(1)
    driver = get_driver(app_caps['appPackage'],app_caps['appActivity'])
    print(f"正在启动 {app_name} ({app_caps['description']}) ...")
    try:
        driver.activate_app(app_caps['appPackage'])
        print(f"{app_name} ({app_caps['description']}) 启动成功")
    except Exception as e:
        print(f"发生未知错误: {e}")
    finally:
        if driver:
            driver.quit()