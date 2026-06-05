#!/usr/bin/env python3
"""
openappcli - 通过 Appium 操作手机的命令行工具
"""
import argparse
import sys
from pathlib import Path

from app_wx_cli.wx_button_pos import *
from app_wx_cli.wx_commom import get_img_and_text
from app_wx_cli.wx_page_identify import friend_chat_page_indentify
from app_wx_cli import wx_send_msg

sys.path.insert(0, str(Path(__file__).parent))
from sys_cli import list_cli
from sys_cli import connected_device
from sys_cli import check_status
from sys_cli import launch_app
from sys_cli import push_file
from core import *


def main():
    parser = argparse.ArgumentParser(description="openappcli - 通过 Appium 操作手机的命令行工具")
    # 系统命令
    subparsers = parser.add_subparsers(dest="cli", required=True, help="子命令")
    # subparsers.add_parser("list-cli", help="列出所有命令")
    subparsers.add_parser("connected-device", help="显示已连接的设备，并检查 Appium server 配置")
    subparsers.add_parser("check-status", help="检查整体状态")

    # driver.save_screenshot(os.path.join(".", f"scroll_0_{timestamp}.png"))
    # print(f"已保存滚动前截图: scroll_0_{timestamp}.png")
    # Base64 字符串解码后得到的就是 PNG 图片数据。
    # b64_str = driver.get_screenshot_as_base64()
    # print("下面是base64的PNG图片格式")
    # print(b64_str)
    subparsers.add_parser("screenshot", help="截屏")
    subparsers.add_parser("scroll-screens", help="滚动屏幕")

    launch_parser = subparsers.add_parser("launch", help="启动应用")
    launch_parser.add_argument("app_name", choices=["wx", "xhs", "douyin"],
                               help="要启动的应用 (wx:微信, xhs:小红书, douyin:抖音)")
    save_page_src_parser = subparsers.add_parser("sps", help="保存应用页面代码")
    save_page_src_parser.add_argument("file_name", help="保存文件名(含路径)")
    push_file_parser = subparsers.add_parser("push-file", help="发送文件到手机(包括图片,文本)")
    push_file_parser.add_argument("filepath", help="本地文件路径")

    scroll_small_parser = subparsers.add_parser("scroll-small", help="轻微滚动屏幕")
    scroll_small_parser.add_argument("type", choices=["up", "down"], help="滚动屏幕方向")

    scroll_general_parser= subparsers.add_parser("scroll-general", help="常规滚动屏幕")
    scroll_general_parser.add_argument("type", choices=["up", "down"], help="滚动屏幕方向")

    # 应用命
    subparsers.add_parser("wx-init", help="初始化微信功能坐标")
    subparsers.add_parser("wx-test", help="初始化微信功能坐标")
    send_send_mag_parser=subparsers.add_parser("wx-send-msg", help="初始化微信功能坐标")
    send_send_mag_parser.add_argument("--friend",required=True, help="好友昵称")
    send_send_mag_parser.add_argument("--msg",required=True, help="发送的消息")

    args = parser.parse_args()

    # 检查配置文件是否存在（使用新的查找函数）
    if get_config_path() is None:
        print("错误：未找到配置文件，请确保以下位置之一存在配置文件：")
        print("  - ./config.yaml")
        print("  - ./.openappcli/config.yaml")
        sys.exit(1)
    config = load_config()
    apps = config.get("apps", {})
    driver = None
    try:
        if args.cli == "list-cli":
            list_cli.run(args)
        elif args.cli == "connected-device":
            driver = get_driver()
            connected_device.run(driver, args)
        elif args.cli == "check-status":
            driver = get_driver()
            check_status.run(driver, args)
        # python openappcli.py push-file "C:\Users\Administrator\Videos\Cities Skylines\1.png"
        elif args.cli == "push-file":
            driver = get_driver()
            push_file.run(driver, args)
        elif args.cli == "launch-app":
            launch_app.run(args)
        # python openappcli.py sps search.xml
        elif args.cli == "sps":
            save_page_src(args.file_name)
        elif args.cli == "scroll-small":
            scroll_small_step(get_driver())
        elif args.cli == "scroll-general":
            scroll_down_screens(get_driver())
        #微信相关命令
        elif args.cli.startswith("wx-"):
            app_caps = apps["wx"]
            driver = get_driver(app_caps['appPackage'], app_caps['appActivity'])
            if args.cli=="wx-init":
                get_click_pos_conf()
            elif args.cli == "wx-send-msg":
                wx_send_msg.run(args)
        else:
            parser.print_help()
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    main()