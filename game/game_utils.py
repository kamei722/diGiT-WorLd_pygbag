import sys, os

# SCREEN_WIDTH = 800
# SCREEN_HEIGHT = 600

# テスト用に異なるサイズを設定
SCREEN_WIDTH = 1078
SCREEN_HEIGHT = 768

# SCREEN_WIDTH = 1280
# SCREEN_HEIGHT = 720

FPS = 60

KEY_SIZE = int(SCREEN_WIDTH * 0.043)

# ステージクリア表示時間（ミリ秒）
STAGE_CLEAR_DISPLAY_TIME = 2000


def resource_path(relative_path):
    """ 
    PyInstaller での実行時に合わせた、リソースファイルへの絶対パスを返す関数 
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

FONT_PATH = resource_path("assets/fonts/DotGothic16-Regular.ttf")