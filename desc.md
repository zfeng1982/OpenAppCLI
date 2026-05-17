

# 启动appium参数
1. 只开启 ADB 功能 (安全，推荐):appium --allow-insecure=uiautomator2:adb_shell
2. 开启所有不安全的权限 (全开):appium --relaxed-security(放开所有 Appium 定义的高风险功能，权限完全开放。)
3. adb shell screencap -p /sdcard/screen.png
4. 获取deviceName:adb devices

# adb命令
1. 获取当前应用的 appPackage（应用包名）和 appActivity（当前界面的名称）:adb shell dumpsys window | findstr mCurrentFocus
2. 获取手机输入法列表:adb shell ime list -s

# 环境配置
1. Python 环境：推荐安装 Python 3.8+ 版本
2. 推荐安装 JDK 8或 JDK 11/17 等 LTS 长期支持版
3. Android SDK (或 Command-line Tools)
   - 作用: 提供 adb(Android Debug Bridge) 工具，用于电脑与模拟器/真机通信，还提供元素定位工具 uiautomatorviewer 
   - 轻量级：直接下载 Android SDK Command-line Tools。
     - [command-line-tools-only下载](https://developer.android.google.cn/studio?hl=zh-cn#command-line-tools-only)
   - 完整版：下载并安装 Android Studio，然后在设置中下载对应的 SDK 包
     - [Android Studio下载](https://developer.android.google.cn/studio?hl=zh-cn)
   - 环境变量：
     - 新建系统变量 ANDROID_HOME，值为 SDK 安装路径（例如 C:\Users\YourName\AppData\Local\Android\Sdk）。
     - 在系统变量 Path中添加 %ANDROID_HOME%\platform-tools和 %ANDROID_HOME%\tools
4. Node.js 及 npm
   - Appium 2.x 是基于 Node.js 开发的，需要它通过 npm 来安装和管理
   - Node.js 版本建议 ^14.17.0 || ^16.13.0 || >=18.0.0
   
5. 安装 Appium 2.x 及相关驱动
   - 安装 Appium 服务器:npm install -g appium
   - Appium 2.x 安装驱动:appium driver install uiautomator2
   - Appium 的 Python 客户端库:pip install Appium-Python-Client

6. 开启“开发者选项”和“USB调试”
   - 连续点击“版本号”7次，开启“开发者选项”
   - 进入“开发者选项”，打开 “USB调试”
   - 关闭"监控ADB安装应用"
   - 关闭"通过USB验证应用"

7. pyyaml,request,PIL(pillow)
8. ucdevtools 定位webview元素





