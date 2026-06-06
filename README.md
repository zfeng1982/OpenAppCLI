# OpenAppCLI
## 简介
- 核心功能：通过计算机的命令行界面（CLI）操控移动端应用程序。
- 项目愿景：旨在赋能 AI 代理（Agent），使其具备自主操作手机应用程序的能力。
![pic](OpenAppCLI.png)
## 实现清单
### 手机系统 CLI
- launch-app: 启动指定的应用程序
- sps: 保存当前应用页面的 UI 层级结构/源码。
- push-file:向移动设备推送文件（支持图片、文本等）。

### Xiaohongshu (XHS) CLI
- xhs-publish: 发布内容（支持类型：album相册选取 / text图文或长文笔记）。
- xhs-search: 搜索用户及笔记内容。
- xhs-details: 根据笔记 ID 获取详情（提取文案、下载视频及图片）。
- xhs-index: 获取首页信息流（包含“发现”、“关注”及 LBS 地理位置列表）。

### 微信 (WX) CLI
微信需要通过截图和OCR来进行定位操作，建议在有GPU的计算机中进行
- wx-init: 初始化程序，主要用于生成定位锚点，后继操作都是通过这些锚点来计算位置