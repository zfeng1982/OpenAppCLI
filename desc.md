

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

## 用法
```bash
 android.widget.LinearLayout[
            @index=0
            and count(child::*) = 2
            and child::*[1][self::android.widget.ImageView and @index=0]
            and child::*[2][self::android.widget.TextView and @index=1 and not(@text='说点什么...') and not(@text='公开可见')]
            and parent::android.widget.LinearLayout[@index=1]
        ]
        android.widget.TextView[contains( @ text, '保存') or contains( @ text, '作者')]"
         element_on_clickable(10, (AppiumBy.ACCESSIBILITY_ID, '评论框'))
```
# 微信需要的安装包
pip install easyocr
安装 VC++ 运行库
下载并安装：Microsoft Visual C++ Redistributable https://aka.ms/vs/17/release/vc_redist.x64.exe
C:\Users\Administrator\.EasyOCR\model
可以把 Microsoft Visual C++ Redistributable（简称 VC++ 运行库）理解为：
Windows 系统的一个“公共能力补给包”。
很多软件（包括你正在用的 Python 库）在开发时，为了追求极致的运行速度，会使用 C++ 来写底层核心代码。这些软件在编写时依赖了微软提供的一些“基础零件”，而 VC++ 运行库就是把这些“基础零件”打包在一起的集合。


先卸载 CPU 版
pip uninstall torch torchvision torchaudio
装 CUDA 11.8 版（兼容性好）
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
或 CUDA 12.1 版（较新）
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121






