---
name: xhs-mobile-app-controller
displayName: 小红书手机APP控制器
author: sardinesInQianhai
description: 让你的Agent能操作小红书手机APP,包括自动化发布长文，想法，相册，下载相册笔记和视频笔记等
metadata: 
  openclaw: 
    emoji: "🔍︎"
    requires: 
      bins: ["python","adb","appium"]
    triggers:
      - "小红书"
      - "自动化"
      - "发布笔记"
      - "手机"
      - "xhs"
    homepage: "https://github.com/zfeng1982/OpenAppCLI"
---
# 小红书手机APP控制器
让你的AI Agent能操作小红书手机APP
  - 发布笔记
    - 图文(支持相片同步手机相册)
    - 想法
    - 长文(支持模板)
  - 笔记互动
    - 发布评论
    - 点赞
    - 收藏
  - 笔记列表
    - 首页发现笔记列表
    - 首页关注笔记列表
    - 首页同城笔记列表
    - 个人主页帐户信息
    - 个人主页笔记列表
  - 笔记详情
    - 正文,LBS,作者,发布时间等信息
    - 下载视频笔记
    - 下载图片笔记
    - 评论列表
  - 搜索
    - 搜索博主
    - 搜索笔记
----
## 技术支持
> 环境配置有一定的技术门槛,如果需要提供帮助或者更多功能,可直接联系SKILL开发者  
> 邮箱:zfengyy@qq.com  
> QQ:81261686  
----
## 环境准备
1. 准备手机
   - 出于安装考虑不建议使用自己日常的手机给Agent进行操作
   - 本技能只支持Android系统的手机
   - 建议使用真机进行自动化操作,理论上可以使用模拟器和云手机
   - 如果使用真机连接电脑,建议使用原厂的USB线,或者质量较好的数据线(选最粗的一条线).
   
2. 手机设置
   - 开启“开发者选项”,连续点击“版本号”7次可开启,不同手机可能开启方式不一样,请自行搜索开启
   - 启动“USB调试”:进入“开发者选项”，打开 “USB调试”
   - 关闭"监控ADB安装应用"
   - 关闭"通过USB验证应用"

3. 应用及Java Android安装
   - 安装并登录小红书APP
   - 安装Java JDK 8或 JDK 11/17
   - Android SDK:提供 adb(Android Debug Bridge) 工具，用于电脑与模拟器/真机通信，还提供元素定位工具 uiautomatorviewer.以下安装包根据情况二选一即可(一般用户推荐轻量级安装)
     - 轻量级：直接下载 Android SDK Command-line Tools。
       - [command-line-tools-only下载](https://developer.android.google.cn/studio?hl=zh-cn#command-line-tools-only)
     - 完整版：下载并安装 Android Studio，然后在设置中下载对应的 SDK 包
       - [Android Studio下载](https://developer.android.google.cn/studio?hl=zh-cn)
       
4. Node.js
   - Appium 2.x 是基于 Node.js 开发的，需要它通过 npm 来安装和管理
   - Node.js 版本建议 ^14.17.0 || ^16.13.0 || >=18.0.0

5. 安装 Appium 2.x 及相关驱动
   - 安装 Appium 服务器:npm install -g appium
   - Appium 2.x 安装驱动:appium driver install uiautomator2
   - Appium 的 Python 客户端库:pip install Appium-Python-Client

6. 命令行启动Appium服务
   - appium --allow-insecure=uiautomator2:adb_shell 


## 环境确认
1. adb安装确认,如下执行adb devices命令,返回手机设备信息,请记住这个设备ID,config.yaml配置文件需要.命令执行失败请检查adb是否安装成功,特别是环境变量  
```bash
PS C:\Users\pan> adb devices
List of devices attached
[你手机的设备ID]        device  
```
2. 获取系统默认输入法,如下执行adb shell ime list -s命令,返回手机上的输入法,请忽略UnicodeIME和AppiumIME,我的手机是com.baidu.input_huawei/.ImeService,记下你手机上安装的输入法config.yaml配置文件需要.
```bash

PS C:\Users\pan> adb shell ime list -s
com.baidu.input_huawei/.ImeService
io.appium.settings/.UnicodeIME
io.appium.settings/.AppiumIME
```
3. 修改scripts/config.yaml文件中的两个值
   - deviceName: "你的设备序列号"
   - IME: 你通过上面命令获取的输入法,例如我的是:com.baidu.input_huawei/.ImeService

4. 确认环境是否成功
    执行 python scripts/openappcli.py connected-device 命令,如果成功会返回如下信息:  
    **✓ 设备已成功连接！**
----
## 手机系统CLI
### 1.检查手机状态(connected-device)
查看手机是否成功链接
用法:
```bash
python scripts/openappcli.py connected-device
```
参数:无  
示例:
```bash
(.venv) PS D:\python\OpenAppCLI> python openappcli.py connected-device
已连接设备: TWGDU16719003567 (Appium server: http://192.168.2.81:4723)
=== Appium 配置信息 ===
Appium server: http://192.168.2.81:4723
配置的设备名: [你的设备ID]
当前为远程 Appium server，请确保服务已手动启动且设备已连接
✓ Appium server 可访问
正在尝试连接设备并获取屏幕信息...
✓ 设备已成功连接！屏幕尺寸: 宽度=1440, 高度=2560
```
### 2.push文件到手机(push-file)
从电脑上push文件到手机,包括图片和视频等.文件保存在手机/sdcard/DCIM/目录下.
用法:
```bash
python scripts/openappcli.py push-file  <文件在本地的完整路径>
```
参数:文件在本地电脑的完整路径 
示例:
```bash
python openappcli.py push-file "C:\Users\Administrator\Videos\Cities Skylines\1.png"
```
### 3.保存手机UI XML源码(sps)
保存当前app页面的UI XML源码,可用于通过xpath的方式控制手机
用法:
```bash
python openappcli.py sps <文件在本地的完整路径和文件名>
```
参数:文件在本地的完整路径 
示例:
```bash
python openappcli.py sps search.xml
```
----
## 小红书APP CLI
### 1.发布相册内容(xhs-publish alum)
发布相册笔记,相片使用push-file命令推送到手机  
用法:
```bash
python scripts/openappcli.py xhs-publish alum  [--count <相片数量>] [--title <笔记标题>] [--content <笔记内容>] [--topics <话题1|话题2|话题3>]
```
参数:
- `--count`：打开相册时选择发布相片的数量(使用相册的默认排序进行选择)
- `--title`：笔记标题
- `--content`：笔记标题内容
- `--topics`：可选，笔记相关的话题,多个话题之间用|分隔
示例:
```bash
python scripts/openappcli.py xhs-publish album --count 2  --title "英国法院裁定三星向中兴赔偿" --content "从公开消息看，中兴通讯在德国、UPC和巴西等法院判决获得了支持。" --topics "三星|中兴"
```
### 2.发布文本内容(xhs-publish text)
发布文字内容,包括想法和长文  
用法:
```bash
python scripts/openappcli.py xhs-publish text --txttype {thinking,longtxt} [--title <笔记标题>] [--content <笔记内容>] [--topics <话题1|话题2|话题3>]
```
参数:
- `--txttype`：文本类型二选一thinking为想法,longtxt为长文
- `--title`：笔记标题
- `--content`：笔记标题内容
- `--topics`：可选，笔记相关的话题,多个话题之间用|分隔
示例:
```bash
python scripts/openappcli.py xhs-publish text --txttype thinking --itxt "我有一个想法" --title "测试想法的标题" --content "测试想法的内容" --topics "测试话题1|测试话题2"
```
### 3.发布评论笔记(xhs-comment)
根据笔记ID发布评论  
用法:
```bash
python scripts/openappcli.py xhs-comment [--note_id <笔记ID>] [--text <内容>] [--note_type {normal,video}]
```
参数:
- `--note_id`：笔记的ID,可通过列表接口获取
- `--text`：评论内容
- `--note_type`：笔记类型normal为图文,video为视频,可能过列表接口获取
示例:
```bash
python openappcli.py xhs-comment --note_id "6a01920f0000000036033ce7" --text "不错找个时间去看下!!" --note_type video
```
### 4.点赞和收藏(xhs-interaction)
点赞/取消点赞,收藏/取消收藏
用法:
```bash
python scripts/openappcli.py xhs-interaction [--note_id <笔记ID>] [--note_type {normal,video}] [--action {favorites,like}]
```
参数:
- `--note_id`：笔记的ID,可通过列表接口获取
- `--note_type`：笔记类型normal为图文,video为视频,可能过列表接口获取
- `--action`：favorites 收藏,like 点赞
示例:
```bash
#收藏视频笔记(重复执行即为消取收藏)
python scripts/openappcli.py xhs-interaction --note_id "69435de2000000001e039058" --note_type video --action favorites
#点赞图文笔记(重复执行即为消取点赞)
python scripts/openappcli.py xhs-interaction --note_id "69f13c090000000023017c85" --note_type normal --action like

```
### 5.获取首页笔记列表(xhs-index)
从上到下滑动获取首页笔记列表,包括discover(发现), followed(关注),lbs(同城LBS)  
用法:
```bash
python scripts/openappcli.py xhs-index {discover,followed,lbs} [--limit <返回数量>]
```
参数:
- `{discover,followed,lbs}`：三选一discover(发现), followed(关注),lbs(同城LBS)
- `--limit`：选填默认值为10,返回笔记的数量,请根据自己手机的性能适当填写,不建议超过50条
示例:
```bash
python scripts/openappcli.py xhs-index discover  --limit 5
```
输出:
```json
 {
      "title": "深圳⋆🍈礼拜五咖啡馆",
      "note_id": "6a06c1ae0000000008002bba",
      "author": "卷卷",
      "date": "05-16",
      "like_num": "43",
      "comment_num": " 8",
      "favorites_num": " 14",
      "location": "礼拜五咖啡馆",
      "distance": "2.1km",
      "note_type": "normal",
      "share_link": "http://xhslink.com/o/AE0rRLjU2DG",
      "_field_comments": {
        "note_type": "只有两个值normal(图文)和video(视频),暂不支持直播"
      }
    }
```
### 6.搜索博主(xhs-search user)
搜索博主信息,可选择同时返回博主的笔记
用法:
```bash
python scripts/openappcli.py xhs-search user [--keyword <博主昵称>] [--note] [--limit <返回笔记数量>]
```
参数:
- `--keyword`：博主昵称
- `--note`：选填,填这个参数说明需要返回博主的笔记列表,为空则只返回博主信息
- `--limit`：选填,返回笔记的数量,前面的参数为--note时才生效,请根据自己手机的性能适当填写,不建议超过50条
示例:
```bash
#搜索辛芷蕾的个人主页,并返回10条她的笔记
python scripts/openappcli.py xhs-search user --keyword "辛芷蕾" --note --limit 10
#只搜索辛芷蕾的个人主页信息,不返回笔记
python scripts/openappcli.py xhs-search user --keyword "辛芷蕾"
```
输出:
```json
{
  "user": {
    "user_name": "辛芷蕾",
    "xhs_id": "",
    "ip_location": "IP：辽宁",
    "job": "演员",
    "follow_count": "0",
    "fans_count": "44.8万",
    "likes_collect": "97.6万",
    "signature": "是我…",
    "share_link": "https://www.xiaohongshu.com/user/profile/5ad5a69511be1041b8e7152e",
    "other_info": "40岁|中国"
  },
  "notes": [
    {
      "title": "让心情提前进入夏日模式～",
      "note_id": "69ecb5450000000035028812",
      "author": "辛芷蕾",
      "date": "04-25",
      "like_num": "5759",
      "comment_num": " 834",
      "favorites_num": " 322",
      "location": "",
      "distance": "",
      "note_type": "normal",
      "share_link": "http://xhslink.com/o/11hnKpaKBPn"
    }
  ],
  "_field_comments": {
    "notes": "这个字段在参数选择--note时才会有数据,否则为[]"
  }
}

```
### 7.搜索日记(xhs-search note)
搜索博主信息,可选择同时返回博主的笔记
用法:
```bash
python scripts/openappcli.py xhs-search note [--keyword <搜索笔记关键字>] [--order {com,new}] [--limit <返回笔记数量>]
```
参数:
- `--keyword`：搜索笔记关键字
- `--order`：排序方式,com综合排序,new按时间排序,默认为综合排,注意不是所有搜索结果都支持按时间排序
- `--limit`：选填,返回笔记的数量,请根据自己手机的性能适当填写,不建议超过50条
示例:
```bash
python scripts/openappcli.py xhs-search note --keyword "我拍到了海鸥雨" --order com --limit 1
```
输出:
```json
{
  "hot_keyword_desc": "薯薯拍到了漫天飞舞的“海鸥雨”，当它们从海面与蓝天间蜂拥而至，翅膀掠过指尖，每一帧都是自由与浪漫的碰撞。",
  "notes": [
    {
      "title": "进来感受4k全屏海鸥雨的震撼 #海鸥与日落  #海鸥不再眷恋大海  #带你看海鸥  #你啊借那风越海峡  #总有一只海鸥为你停留  #昆明  #我拍到",
      "note_id": "6989aaf100000000090384d9",
      "author": "Donhox 📸",
      "date": "02-23",
      "like_num": "10万+",
      "comment_num": " 9179",
      "favorites_num": " 36315",
      "note_type": "normal",
      "share_link": "http://xhslink.com/o/1tfpCg2ZMct"
    }
  ],
  "_field_comments": {
    "hot_keyword_desc": "热词介绍,当搜索关键字命中热词是才会有值"
  }
}
```
### 8.获取和下载笔记详情内容(xhs-details)
根据笔记ID获取详情包括文本,图片和视频.
用法:
```bash
python scripts/openappcli.py xhs-details [--note_id <笔记ID>] [--note_type {normal,video}]  [--dir <保存资源的本地目录>]
```
参数:
- `--note_id`：笔记ID,可从笔记列表中获取
- `--note_type`：笔记类型,normal(图文)和video(视频)二选一,可从笔记列表中获取
- `--dir`：下载资源的保存目录,包括图片和视频.技能只能获取手机上保存目录为/sdcard/DCIM/Camera/的资源,一般手机默认都是这个设置
示例:
```bash
python openappcli.py xhs-details --note_id "69f54d4e0000000020038635" --note_type video  --dir "c:\xhs"
```
输出:
```json
{
   "note_text": {
    "title": "和我一起开启「满级XIN状态」",
    "content": "和 ID. ERA 9X 同行，每一段旅程都自在从容🚗 @大众汽车 @上汽大众大众品牌\n#大众9X #德系满级旗舰SUV #大众汽车全新以赴 ",
    "note_id": "69ec2741000000003502aae8",
    "author": "",
    "date": "04-25",
    "like_num": "2121",
    "comment_num": "302",
    "favorites_num": "133",
    "location": "",
    "distance": "",
    "note_type": "video",
    "share_link": "http://xhslink.com/o/8k5Aa5sPbyt"
  },
  "video_save_path": [
    "c:\\xhs\\69ec2741000000003502aae8\\video.mp4"
  ],
  "images_save_path": [],
  "_field_comments": {
    "video_save_path": "note_type=video 时才会有值",
    "images_save_path": "note_type=normal 时才会有值"
  }
}
```
### 9.获取评论列表(xhs-comment-list)
根据笔记ID获取评论列表,只返回一级的评论内容,不包括回复
用法:
```bash
python scripts/openappcli.py openappcli.py xhs-comment-list [--note_id <笔记ID>] [--note_type {normal,video}]  [--limit <返回评论数量>]
```
参数:
- `--note_id`：笔记ID,可从笔记列表中获取
- `--note_type`：笔记类型,normal(图文)和video(视频)二选一,可从笔记列表中获取
- `--limit`：返回评论数量
示例:
```bash
python openappcli.py xhs-comment-list --note_id "6a0a94d4000000003601ec7a" --note_type normal --limit 2
```
输出:
```json
{
  "note_id": "6a0a94d4000000003601ec7a",
  "comment_sum": "共 239 条评论",
  "comment_list": [
    {
      "nick_name": "珺仔",
      "content": "他是累坏的，又不是跑坏的[失望R]  ",
      "date_and_lbs": "3天前 广西 ",
      "like_num": "141"
    },
    {
      "nick_name": "未央",
      "content": "最主要的不是跑步猝死[失望R]而是睡眠不足[失望R]，睡眠不足耗心阳的啊[失望R]说白了就是提前透支你的阳气，肺气，没看熬夜之后第二天早起，就会感觉气短胸闷[失望R]  ",
      "date_and_lbs": "3天前 黑龙江 ",
      "like_num": "1"
    }
  ],
  "_field_comments": {
    "comment_sum": "评论总数为评论数+回复数"
  }
}

```