import sys
import os
import base64

def run(driver,args):
    try:
        filepath = args.filepath
        # 检查本地文件是否存在
        if not os.path.isfile(filepath):
            print(f"错误：文件不存在 - {filepath}")
            sys.exit(1)

        # 读取文件并转为 base64
        with open(filepath, 'rb') as f:
            file_data = base64.b64encode(f.read()).decode('utf-8')

        # 提取文件名，构造手机上的目标路径（可写的外部存储）
        filename = os.path.basename(filepath)
        # 使用 /sdcard/DCIM/ 或 /storage/emulated/0/DCIM/（两者通常等效）
        # 这个目录是写死的目前还不支持修改
        dest_path = f"/sdcard/DCIM/{filename}"
        driver.push_file(dest_path, file_data)
        print(f"文件已成功推送到手机: {dest_path}")

    except Exception as e:
        print(f"发生未知错误: {e}")