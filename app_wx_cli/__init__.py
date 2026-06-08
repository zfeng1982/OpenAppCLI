# 初始化全局变量
# 加载配置
# 检查运行环境
# 预加载资源
import os
import easyocr
_WX_INDEX_TAB_KEYWORD_=['微信', '通讯录', '发现', '我']
_WX_BASE_DIR_ = os.path.dirname(os.path.abspath(__file__))
_WX_CONF_PATH_ = os.path.join(_WX_BASE_DIR_, "wx_pos_conf.yaml")
# 微信消息/昵称和系统日期字体的差值
_WX_FONT_SIZE_DIFF=0.39
# 初始化（首次会自动下载模型，约 100MB）
_EA_READER_ = easyocr.Reader(['ch_sim', 'en'], gpu=True)