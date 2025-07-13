# core/dj_controller.py
import pygame
import time

class DJController:
    def __init__(self, track_path):
        pygame.mixer.init()
        self.track_path = track_path
        self.is_playing = False

    def load_track(self):
        pygame.mixer.music.load(self.track_path)

    def play(self):
        pygame.mixer.music.play()
        self.is_playing = True

    def pause(self):
        pygame.mixer.music.pause()
        self.is_playing = False

    def unpause(self):
        pygame.mixer.music.unpause()
        self.is_playing = True

    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False