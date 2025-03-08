import sys, os
import pygame

# ブラウザ環境かどうかを検出する関数
def is_browser_environment():
    try:
        # PyInstallerの属性があるかチェック（デスクトップのみの特徴）
        return not hasattr(sys, '_MEIPASS') and not os.path.exists('/bin')
    except:
        # エラーが発生したらブラウザとみなす
        return True

# 最適なスクリーンサイズを取得する関数
def get_optimal_screen_size():
    if is_browser_environment():
        return 1024, 768
    else:
        # デスクトップ環境では固定サイズ
        return 1078, 768  # 元の解像度

# スクリーンサイズを設定
SCREEN_WIDTH, SCREEN_HEIGHT = get_optimal_screen_size()

# フレームレート設定
FPS = 60

# アイテムサイズ計算
KEY_SIZE = int(SCREEN_WIDTH * 0.043)

# ステージクリア表示時間（ミリ秒）
STAGE_CLEAR_DISPLAY_TIME = 2000

# リソースパスの解決
def resource_path(relative_path):
    try:
        # PyInstaller 用
        if hasattr(sys, "_MEIPASS"):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
    except:
        # ブラウザ(pyodide)環境など
        return relative_path

# フォントパス
FONT_PATH = "assets/fonts/DotGothic16-Regular.ttf"