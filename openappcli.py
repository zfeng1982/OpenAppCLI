#!/usr/bin/env python3
"""
openappcli - 通过 Appium 操作手机的命令行工具
"""
import argparse
import sys
from pathlib import Path

from app_xhs_cli.xhs_common import back_index

sys.path.insert(0, str(Path(__file__).parent))
from sys_cli import list_cli
from sys_cli import connected_device
from sys_cli import check_status
from sys_cli import launch_app
from sys_cli import push_file
from app_xhs_cli import xhs_publish, xhs_comment_list
from app_xhs_cli import xhs_search
from app_xhs_cli import xhs_details
from app_xhs_cli import xhs_discover
from app_xhs_cli import xhs_followed
from app_xhs_cli import xhs_lbs
from app_xhs_cli import xhs_comment
from app_xhs_cli import xhs_interaction
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

    # 应用命令
    # 小红书发布相关命令
    xhs_publish_parser = subparsers.add_parser("xhs-publish", help="发布小红书笔记")
    xhs_publish_parser.add_argument("type", choices=["album", "text"], help="发布的类型 (album:从相册选择, text:文本)")
    xhs_publish_parser.add_argument("--count", type=int, default=1, help="选择图片数量（仅当 type=album 时有效，默认1张）")
    xhs_publish_parser.add_argument("--one-tap", action="store_true", help="是否一键成片")
    xhs_publish_parser.add_argument("--title", type=str, help="标题")
    xhs_publish_parser.add_argument("--content", type=str, help="内容")
    xhs_publish_parser.add_argument("--itxt", type=str, help="想法")
    xhs_publish_parser.add_argument("--topics", type=str, help="话题,话题之间用|分隔如:自动化|小红书")
    xhs_publish_parser.add_argument("--txttype", choices=["idea", "longtxt"], help="选择'写想法'或'写长文'")

    # 小红书搜索
    xhs_search_parser = subparsers.add_parser("xhs-search", help="小红书搜索笔记")
    xhs_search_parser.add_argument("type", choices=["user", "note"], help="搜索类型")
    xhs_search_parser.add_argument("--keyword", help="搜索关键字")
    xhs_search_parser.add_argument( "--note",action="store_true",default=False,help="是否需要笔记列表，默认不需要")
    xhs_search_parser.add_argument("--order", choices=["com", "new"], default="com", help="排序方式,默认为(只用搜索日志)")
    xhs_search_parser.add_argument("--limit", type=int, default=10, help="返回笔记条数")

    # 小红书根据笔记标题进入笔记详情页
    xhs_details_parser = subparsers.add_parser("xhs-details",
                                               help="小红书笔记标题进入详情,使用这个命令要行进入笔记的列表页面,可以是'发现',搜索列表,个人首页笔记列表")
    xhs_details_parser.add_argument("--note_id", required=True, help="精准匹配(必填)")
    xhs_details_parser.add_argument("--note_type", required=True, choices=["video", "normal"], help="精准匹配(必填)")
    xhs_details_parser.add_argument("--dir", required=True, help="文件保存目录包括视频,图片(必填)")

    xhs_index_parser = subparsers.add_parser("xhs-index", help="首页")
    xhs_index_parser.add_argument("type", choices=["discover", "followed", "lbs"], help="关注,发现,LBS")
    xhs_index_parser.add_argument("--limit", type=int, default=10, help="返回笔记条数")

    xhs_comment_parser = subparsers.add_parser("xhs-comment", help="评论笔记")
    xhs_comment_parser.add_argument("--note_id", required=True, help="精准匹配(必填)")
    xhs_comment_parser.add_argument("--text", required=True, help="评论内容必填")
    xhs_comment_parser.add_argument("--note_type", required=True, choices=["video", "normal"], help="笔记类型精准匹配(必填)")

    xhs_interaction_parser = subparsers.add_parser("xhs-interaction", help="笔记互动操作")
    xhs_interaction_parser.add_argument("--note_id", required=True, help="精准匹配(必填)")
    xhs_interaction_parser.add_argument("--note_type", required=True, choices=["video", "normal"],help="笔记类型精准匹配(必填)")
    xhs_interaction_parser.add_argument("--action", required=True, choices=["like", "favorites"], help="like喜欢,favorites收藏,同一篇笔记第一次点击为确认,第二次点击为取消")

    xhs_comment_list_parser = subparsers.add_parser("xhs-comment-list", help="获得评论列表")
    xhs_comment_list_parser.add_argument("--note_id", required=True, help="精准匹配(必填)")
    xhs_comment_list_parser.add_argument("--note_type", required=True, choices=["video", "normal"],help="笔记类型精准匹配(必填)")
    xhs_comment_list_parser.add_argument("--limit", type=int, default=10, help="返回评论条数")

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
        # python openappcli.py xhs-publish album --count 2  --title "英国法院裁定三星向中兴赔偿" --content "从公开消息看，中兴通讯在德国、UPC和巴西等法院判决获得了支持。从外媒报道看，从2025年年初，德国、UPC、巴西等法院陆续判决，均支持中兴立场和报价。" --topics "新能源|五一假期"
        # python openappcli.py xhs-publish text --txttype thinking --itxt "多国法院支持中兴通讯的诉求" --title "多国法院支持中兴通讯的诉求" --content "更值得注意的是，英国法院自己在审理“Optis VS Apple”案时也曾使用Top-down进行交叉验证。" --topics "人山人海|五一假期"
        # python openappcli.py xhs-publish text --txttype longtxt --topics "辛芷蕾|五一假期" --title "辛芷蕾五一节和闺蜜自驾游，骑着10万元的自行车，还撞树手臂流血" --content "五一小长假大家都玩嗨了吧，平时忙到脚不沾地的明星，也终于能抽出时间好好放松了。咱们熟悉的女演员辛芷蕾，这次她这次晒图不小心把自己开的座驾露了出来，蓝色的家用车，市价大概在28万元左右，不算什么夸张的顶级豪车，走的就是实用舒适路线。大块头的车衬得人愈发小巧，辛芷蕾往那儿一站，气质优雅妩媚，谁能猜出来她已经40岁了。估计是常年练瑜伽的缘故，她的身材紧致利落，连一点多余的小肚子都没有，状态好到不像话。这次到了目的地，她先拉素颜的辛芷蕾皮肤状态依旧能打，白皙细腻不说，脸上连个明显的皱纹斑点都找不到，羡煞了一堆天天熬大夜的打工人。平时在娱乐圈轧戏跑活动，连睡个完整的好觉都难，能这么安安静静跟闺蜜坐一下午吹吹风，这种松弛感真的太戳人了"
        elif args.cli.startswith("xhs-"):
            app_caps = apps["xhs"]
            driver = get_driver(app_caps['appPackage'], app_caps['appActivity'])

            if args.cli not in["xhs-details","xhs-comment","xhs-interaction","xhs-comment-list"]:
                # 回到首页再执行
                back_index(driver)
            if args.cli == "xhs-publish":
                xhs_publish.run(args)
            # python openappcli.py xhs-search user --keyword "辛芷蕾" --note --limit 10
            # python openappcli.py xhs-search user --keyword "信息蒸馏研究所" --note --limit 5
            # python openappcli.py xhs-search user --keyword "罗振宇" --limit 5
            # python openappcli.py xhs-search note --keyword "五一假期" --order new --limit 5
            # python openappcli.py xhs-search note --keyword "我拍到了海鸥雨" --order com --limit 5
            # python openappcli.py xhs-search note --keyword "信息蒸馏研究所" --order com --limit 5
            # python openappcli.py xhs-search note --keyword "辛芷蕾" --limit 5
            # python openappcli.py xhs-search note --keyword "普拉提" --limit 50
            # python openappcli.py xhs-search note --keyword "迷人又危险的特工姐姐登场" --order new  --limit 2
            # python openappcli.py xhs-search note --keyword "蜜桃女孩" --order new --limit 5
            # python openappcli.py xhs-search note --keyword "我的运动日常分享 SS潘泥" --limit 5
            elif args.cli == "xhs-search":
                xhs_search.run(args)
            #
            # 禁止下载视频
            # python openappcli.py xhs-details --note_id "6a09983700000000060223e4" --note_type video  --dir "c:\xhs"
            # 超长视频
            # python openappcli.py xhs-details --note_id "69ff656d0000000010001c00" --note_type video  --dir "c:\xhs"
            # python openappcli.py xhs-details --note_id "69f54d4e0000000020038635" --note_type video  --dir "c:\xhs"
            # python openappcli.py xhs-details --note_id "6966e7af000000000b0124e0" --note_type normal  --dir "c:\xhs"
            # python openappcli.py xhs-details --note_id "69f740d50000000037035ce1" --note_type normal  --dir "c:\xhs"
            # python openappcli.py xhs-details --note_id "69c4a99d00000000230100e0" --note_type normal  --dir "c:\xhs"
            # python openappcli.py xhs-details --note_id "69cd0ac0000000002103bc97" --note_type normal --dir "c:\xhs"
            # python openappcli.py xhs-details --note_id "6989aaf100000000090384d9" --note_type normal --dir "c:\xhs"
            # python openappcli.py xhs-details --note_id "69fec1870000000035023f32" --note_type normal --dir "c:\xhs"
            # python openappcli.py xhs-details --note_id "69fec1870000000035023f32" --note_type normal --dir "c:\xhs"
            # python openappcli.py xhs-details --note_id "6a0d7cf5000000003501e132" --note_type normal --dir "c:\xhs"
            elif args.cli == "xhs-details":
                xhs_details.run(args)
            # python openappcli.py xhs-index discover  --limit 5
            elif args.cli == "xhs-index":
                if args.type == "discover":
                    xhs_discover.run(args)
                elif args.type == "followed":
                    xhs_followed.run(args)
                # python openappcli.py xhs-index lbs --limit 5
                elif args.type == "lbs":
                    xhs_lbs.run(args)
            elif args.cli=="xhs-comment":
                xhs_comment.run(args)
            elif args.cli=="xhs-comment-list":
                xhs_comment_list.run(args)
            elif args.cli=="xhs-interaction":
                xhs_interaction.run(args)
        else:
            parser.print_help()
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    main()