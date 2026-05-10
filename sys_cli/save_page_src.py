def run(driver,args):
    try:
        file_name = args.file_name  # 字符串或 None
        page_source = driver.page_source
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(page_source)
        print(f"保存Page Source成功!({file_name})")

        # timestamp = time.strftime("%Y%m%d_%H%M%S")
        # driver.save_screenshot(os.path.join(".", f"page_source_{timestamp}.png"))

    except Exception as e:
        print(f"发生未知错误: {e}")