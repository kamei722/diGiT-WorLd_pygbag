import sys, os

# 元のサイズ
# SCREEN_WIDTH = 800
# SCREEN_HEIGHT = 600

# テスト用に異なるサイズを設定
SCREEN_WIDTH = 1078
SCREEN_HEIGHT = 768


# SCREEN_WIDTH = 1280
# SCREEN_HEIGHT = 720

FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

KEY_SIZE = int(SCREEN_WIDTH * 0.043)

# 正しい絶対パスで環境設定
FONT_PATH = "/Users/kameishohei/Game_project/clock_action/digitworld/assets/fonts/DotGothic16-Regular.ttf"

# ステージクリア表示時間（ミリ秒）
STAGE_CLEAR_DISPLAY_TIME = 2000  # 2秒


def resource_path(relative_path):
    """ 
    開発環境および PyInstaller での実行時に合わせた、リソースファイルへの絶対パスを返す関数 
    """
    try:
        # PyInstaller でビルドされた場合
        base_path = sys._MEIPASS
    except Exception:
        # 開発中の場合は現在のディレクトリを基準にする
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)