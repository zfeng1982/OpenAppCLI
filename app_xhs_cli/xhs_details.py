import time
import json
import re
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from core import scroll_small_step,swipe_right,swipe_left,save_full_screenshot,swipe_left_at_bottom
import os
from PIL import Image
import io
import base64

def get_video_duration(driver):
    """
    通过 XPath 定位视频进度条所在的 FrameLayout，从其 content-desc 中提取总时长。
    返回格式如 "0分50秒"
    """
    try:
        # 定位包含 VideoSeekBar 的 FrameLayout（或者直接定位 VideoSeekBar 的父级）
        # 根据 XML 结构，VideoSeekBar 的父级 FrameLayout 的 content-desc 包含时长信息
        elem = driver.find_element(AppiumBy.XPATH, "//com.xingin.redview.seekbar.VideoSeekBar/..")
        desc = elem.get_attribute("content-desc")
        if desc:
            match = re.search(r"共(\d+)分(\d+)秒", desc)
            if match:
                minutes, seconds = match.groups()
                return int(minutes), int(seconds)
    except Exception as e:
        print(f"获取时长失败: {e}")
        pass

    # 备选：直接定位 content-desc 包含 "已播放到" 和 "共" 的 FrameLayout
    try:
        elem = driver.find_element(AppiumBy.XPATH,
                                   "//android.widget.FrameLayout[contains(@content-desc, '已播放到') and contains(@content-desc, '共')]")
        desc = elem.get_attribute("content-desc")
        match = re.search(r"共(\d+)分(\d+)秒", desc)
        if match:
            minutes, seconds = match.groups()
            return int(minutes),int(seconds)
    except Exception as e:
        print(f"备选获取时长失败: {e}")
    return 0,0

def count_xhs_mp4_files_bak(driver,directory="/sdcard/DCIM/Camera"):
    fileCount=0
    try:
        result = driver.execute_script('mobile: shell', {
            'command': 'ls',
            'args': ['-t', directory]
        })
        lines = result.strip().split('\n')
        for line in lines:
            filename = line.strip()
            # 条件：以 xhs_ 开头，且以 .mp4 结尾
            if filename.startswith('xhs_') and filename.endswith('.mp4'):
                fileCount=fileCount+1
    except Exception as e:
        print(f"统计文件数量失败: {e}")

    return fileCount
def count_xhs_mp4_files(driver,directory="/sdcard/DCIM/Camera"):
    try:
        result = driver.execute_script('mobile: shell', {
            'command': 'ls',
            'args': ['-1', '/sdcard/DCIM/Camera/xhs_*.mp4']
        })
        if result and isinstance(result, str):
            lines = [line for line in result.strip().split('\n') if line.strip()]
            return len(lines)
        return 0
    except Exception as e:
        # 如果错误信息指明没有找到文件，返回 0
        if "No such file or directory" in str(e):
            return 0
        # 其他异常则打印并返回 0
        print(f"统计文件数量失败: {e}")
        return -1

def get_latest_video_path(driver, directory="/sdcard/DCIM/Camera"):
    """
    通过 Appium 在设备上执行 ls -t 命令，获取指定目录下最新的、文件名以 'xhs_' 开头的 .mp4 文件路径。

    Args:
        driver: Appium WebDriver 实例
        directory: 视频文件所在目录（默认为相机目录）

    Returns:
        最新视频的完整路径（如 "/sdcard/DCIM/Camera/xhs_123.mp4"），若未找到则返回 None
    """
    try:
        result = driver.execute_script('mobile: shell', {
            'command': 'ls',
            'args': ['-t', directory]
        })
        lines = result.strip().split('\n')
        for line in lines:
            filename = line.strip()
            # 条件：以 xhs_ 开头，且以 .mp4 结尾
            if filename.startswith('xhs_') and filename.endswith('.mp4'):
                return f"{directory}/{filename}"
    except Exception as e:
        print(f"获取最新视频失败: {e}")
    return None
def click_image(driver,min_width=350, min_height=350):
    # 直接获取截图数据并转为 Image 对象
    png_data = driver.get_screenshot_as_png()
    full_img = Image.open(io.BytesIO(png_data))
    width, height = full_img.size
    image_views = driver.find_elements(AppiumBy.XPATH, "//android.widget.ImageView")
    if not image_views:
        # print("未找到任何 ImageView")
        return False
    for idx, iv in enumerate(image_views):
        bounds = iv.get_attribute("bounds")
        if not bounds:
            continue
        coords = re.findall(r"\d+", bounds)
        if len(coords) != 4:
            continue
        x1, y1, x2, y2 = map(int, coords)
        # 边界保护
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(width, x2), min(height, y2)
        if x2 <= x1 or y2 <= y1:
            continue

        img_w = x2 - x1
        img_h = y2 - y1
        # 判断图片大小是否满足阈值
        if img_w < min_width or img_h < min_height:
            # print(f"跳过较小图片 {idx + 1}: {img_w}x{img_h}")
            continue
        # print(f"找到可点击的大图 {idx + 1}: {img_w}x{img_h}")
        iv.click()
        return True
    # 找不到可以点击的大图
    return False

def get_image_progress(driver):
    """
    从页面中提取当前图片是第几张和总共多少张。
    返回 (current, total) 如果未找到则返回 (None, None)
    """
    try:
        # 查找包含 "图片,第" 和 "共" 的 FrameLayout
        elem = driver.find_element(AppiumBy.XPATH, "//android.widget.FrameLayout[contains(@content-desc, '图片,第')]")
        desc = elem.get_attribute("content-desc")
        # 正则提取
        match = re.search(r"第(\d+)张,共(\d+)张", desc)
        if match:
            return int(match.group(1)), int(match.group(2))
    except:
        pass
    return None, None


def delete_xhs_video(driver, remote_path):
    """
    删除设备上的指定文件，但要求文件名以 'xhs_' 开头且以 '.mp4' 结尾。

    Args:
        driver: Appium driver 实例
        remote_path: 设备上的完整文件路径，例如 '/sdcard/DCIM/Camera/xhs_123.mp4'
    """
    # 提取文件名
    filename = os.path.basename(remote_path)
    # 检查命名规范
    if not (filename.startswith("xhs_") and filename.endswith(".mp4")):
        raise ValueError(f"文件名不符合 xhs_*.mp4 规范: {filename}")

    try:
        # 执行删除命令（使用 -f 避免文件不存在时报错）
        driver.execute_script('mobile: shell', {
            'command': 'rm',
            'args': ['-f', remote_path]
        })
        print(f"已删除文件: {remote_path}")
    except Exception as e:
        print(f"删除失败: {e}")

def run(driver,args):

    try:
        deep_link_url = f"xhsdiscover://item/{args.note_id}?type={args.note_type}"
        driver.execute_script('mobile: deepLink', { 'url': f'{deep_link_url}',})
        text_views = []
        video_save_path = []
        image_sava_path = []
        note = {}
        save_resource_dir=args.dir+"\\"+args.note_id
        if not os.path.exists(save_resource_dir):
            os.makedirs(save_resource_dir)

        # 需要开启 ADB 功能 (安全，推荐)	appium --allow-insecure=uiautomator2:adb_shell
        if args.note_type=="video":
            time.sleep(1)
            all_textviews = driver.find_elements(AppiumBy.XPATH, "//android.widget.TextView")
            # 遍历查找文本为 "关注" 的 TextView
            for i, tv in enumerate(all_textviews):
                text = tv.text.strip()
                if len(text) > 10:
                    text_views.append(text)
            note["text_views"] = text_views
            minutes,seconds=get_video_duration(driver)
            try:
                share_btn = driver.find_element(AppiumBy.XPATH, ".//*[@content-desc='分享']")
            except:
                share_btn = driver.find_element(AppiumBy.ID, "com.xingin.xhs:id/moreOperateIV")

            if share_btn:
                before_mobile_video_count=count_xhs_mp4_files(driver)
                share_btn.click()
                time.sleep(1)
                swipe_left_at_bottom(driver)
                save_option = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((AppiumBy.XPATH, "//*[contains(@text, '保存')]"))
                )
                save_option.click()
                # 下载视频的等待时间
                # 根据视频长度计算sleep时间
                save_wait_time=30
                if minutes>0 or seconds>0:
                    # 等待时间为视频长度的1/2,如一段一分钟的视频,等待30s
                    save_wait_time=round((minutes * 60 + seconds) / 2.0, 1)
                print(f"视频时长:{minutes}分{seconds}秒,等待视频操作:{save_wait_time}秒")
                time.sleep(save_wait_time)
                # 下载前和下载后文件数量一样则表示,下载失败
                after_mobile_video_count = count_xhs_mp4_files(driver)
                # print(f"before_mobile_video_count:{before_mobile_video_count},after_mobile_video_count:{after_mobile_video_count}")
                if 0 <= before_mobile_video_count < after_mobile_video_count and after_mobile_video_count>=0:
                    latest_video_path=get_latest_video_path(driver)
                    # print(f"latest_video_path:{latest_video_path}")
                    save_dir = save_resource_dir
                    if latest_video_path:
                        # 从手机拉取文件（返回 Base64 字符串）
                        file_data_base64 = driver.pull_file(latest_video_path)
                        # 解码为字节
                        file_data = base64.b64decode(file_data_base64)
                        # 写入本地文件
                        local_dir=os.path.join(save_dir, 'video.mp4')
                        with open(local_dir, 'wb') as f:
                            f.write(file_data)
                        print(f"视频已保存至: {local_dir}")
                        delete_xhs_video(driver,latest_video_path)
                        video_save_path.append(local_dir)
                    else:
                        print(f"未找到下载的视频文件:{latest_video_path}")
                else:
                    print(f"文件下载失败,确认作者是否充许保存")

                note["video_save_path"]=video_save_path

        else:

            scroll_small_step(driver)
            time.sleep(0.5)
            all_textviews = driver.find_elements(AppiumBy.XPATH, "//android.widget.TextView")
            # 遍历查找文本为 "关注" 的 TextView
            for i, tv in enumerate(all_textviews):
                text = tv.text.strip()
                if len(text) > 10:
                    text_views.append(text)
            c,m=get_image_progress(driver)
            if c and m:
                # 点击放大图片
                if click_image(driver):
                   for i in range(int(m)):
                       time.sleep(4)
                       filePath=save_full_screenshot(driver,save_resource_dir,str(i+1))
                       image_sava_path.append(filePath)
                       swipe_left(driver)
            note["text_views"]=text_views
            note["images_save_path"]=image_sava_path
            note["video_save_path"] = video_save_path
        print(json.dumps(note, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"发生未知错误: {e}")


