from __future__ import annotations
from PIL import Image
import pygame

class GifExporter:
    def __init__(self) -> None:
        self.frames: list[Image.Image] = []
        self.recording = False

    def start_recording(self) -> None:
        self.frames.clear()
        self.recording = True

    def record_frame(self, surface: pygame.Surface) -> None:
        if not self.recording:
            return
        # Convert pygame surface to RGB string, then to PIL Image
        size = surface.get_size()
        data = pygame.image.tostring(surface, "RGB")
        img = Image.frombytes("RGB", size, data)
        self.frames.append(img)

    def stop_and_save(self, filepath: str, duration_ms: int = 500) -> None:
        self.recording = False
        if not self.frames:
            return
        
        try:
            self.frames[0].save(
                filepath,
                save_all=True,
                append_images=self.frames[1:],
                duration=duration_ms,
                loop=0
            )
        finally:
            self.frames.clear()
