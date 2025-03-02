# game/managers/soundmanager.py
import pygame
import os

class SoundManager:
    def __init__(self, sound_dir):
        self.sound_dir = sound_dir
        self.sounds = {}
        self.channels = {}
        self.sound_on = True
        #print(f"[DEBUG] SoundManager initialized with sound directory: {self.sound_dir}")

    def load_sound(self, name, filename):
        path = os.path.join(self.sound_dir, filename)
        try:
            sound = pygame.mixer.Sound(path)
            self.sounds[name] = sound
        except pygame.error as e:
            pass
            #print(f"[DEBUG] Failed to load sound '{name}' from '{path}': {e}")

    def play(self, name):
        if not self.sound_on:
            return  # サウンドがオフの場合は再生しない
        sound = self.sounds.get(name)
        if sound:
            channel = pygame.mixer.find_channel()
            if channel:
                channel.play(sound)
            else:
                sound.play()
        else:
            pass

    def set_volume(self, name, volume):
        sound = self.sounds.get(name)
        if sound:
            sound.set_volume(volume)
        else:
            pass
            #print(f"[DEBUG] Sound '{name}' not found!")

    def toggle_sound(self):
        self.sound_on = not self.sound_on

    def play_music(self, file_name, loops=-1):
        if not self.sound_on:
            return 
        path = os.path.join(self.sound_dir, file_name)
        if os.path.exists(path):
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.play(loops=loops)
            except pygame.error as e:
                pass
                #print(f"Error loading music '{file_name}' from '{path}': {e}")
        else:
            pass            #print(f"Music file '{path}' not found!")

    def stop_music(self):
        pygame.mixer.music.stop()
        #print("Music stopped.")

    def pause_music(self):
        pygame.mixer.music.pause()

    def unpause_music(self):
        pygame.mixer.music.unpause()
