import pygame
import os

class SoundManager:
    def __init__(self, sound_dir):
        self.sound_dir = sound_dir
        self.sounds = {}
        self.channels = {}
        self.sound_on = True
        # ブラウザ環境チェック
        try:
            import sys
            self.is_browser = (getattr(sys, 'platform', None) == 'emscripten')
        except Exception as e:
            print(f"Could not determine platform: {e}")
            self.is_browser = False  # or True, depending on your preference

    def load_sound(self, name, filename):
        try:
            # ブラウザ環境に対応したファイルパス生成
            if self.is_browser:
                path = f"{self.sound_dir}/{filename}"
            else:
                path = os.path.join(self.sound_dir, filename)
                
            sound = pygame.mixer.Sound(path)
            self.sounds[name] = sound
        except pygame.error as e:
            print(f"Failed to load sound {filename}: {e}")
            # エラーハンドリング - ブラウザでは一部のファイル操作でエラーが出るため静かに失敗

    def play(self, name):
        if not self.sound_on:
            return  # サウンドがオフの場合は再生しない
        sound = self.sounds.get(name)
        if sound:
            try:
                channel = pygame.mixer.find_channel()
                if channel:
                    channel.play(sound)
                else:
                    sound.play()
            except Exception as e:
                print(f"Unexpected error in SoundManager: {e}")
                pass
        else:
            pass

    def set_volume(self, name, volume):
        sound = self.sounds.get(name)
        if sound:
            try:
                sound.set_volume(volume)
            except Exception:
                # ブラウザでボリューム設定に失敗しても続行
                pass
        else:
            pass

    def toggle_sound(self):
        self.sound_on = not self.sound_on

    def play_music(self, file_name, loops=-1):
        if not self.sound_on:
            return
            
        try:
            # ブラウザ環境に対応したファイルパス生成
            if self.is_browser:
                path = f"{self.sound_dir}/{file_name}"
            else:
                path = os.path.join(self.sound_dir, file_name)
                
            # ファイル存在チェックはブラウザでは動作しない可能性があるため条件分岐
            if self.is_browser or os.path.exists(path):
                try:
                    pygame.mixer.music.load(path)
                    pygame.mixer.music.play(loops=loops)
                except pygame.error:
                    # ブラウザでの音楽読み込みエラーを静かに処理
                    pass
        except Exception:
            # 予期せぬエラーも静かに処理
            pass

    def stop_music(self):
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

    def pause_music(self):
        try:
            pygame.mixer.music.pause()
        except Exception:
            pass

    def unpause_music(self):
        try:
            pygame.mixer.music.unpause()
        except Exception:
            pass