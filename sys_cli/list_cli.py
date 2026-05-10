def run(args):
    """列出所有命令"""
    commands = [
        "   openappcli.py list                     - 列出所有命令",
        "   openappcli.py connected-device         - 显示已连接的设备，并启动 Appium 服务",
        "   openappcli.py check-status             - 检查设备连接、Appium 服务及 driver 状态",
        "   openappcli.py launch wx                - 启动微信",
        "   openappcli.py launch xhs               - 启动小红书",
        "   openappcli.py launch douyin            - 启动抖音",
    ]
    print("\n".join(commands))