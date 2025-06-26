# utils/video_effects.py
from moviepy.editor import ColorClip, CompositeVideoClip

def add_flash_effect(clip, flash_duration=0.08):
    """
    在影片片頭閃白一瞬間（0.08秒）
    """
    w, h = clip.size
    flash = ColorClip(size=(w, h), color=(255, 255, 255), duration=flash_duration)
    flash = flash.set_opacity(0.4)

    composite = CompositeVideoClip([clip.set_start(flash_duration), flash])
    return composite.set_duration(clip.duration)

from moviepy.editor import CompositeVideoClip
import numpy as np

def add_ghost_effect(clip, ghost_count=3, interval=0.1, opacity_decay=0.5):
    """
    給 clip 加上拖影（殘影）效果
    - ghost_count: 拖影數量
    - interval: 每幀拖影相隔幾秒
    - opacity_decay: 每層的透明度遞減
    """
    w, h = clip.size
    layers = [clip]
    
    for i in range(1, ghost_count + 1):
        offset = i * interval
        opacity = max(0, 1.0 - opacity_decay * i)
        ghost = clip.set_start(offset).set_opacity(opacity)
        layers.append(ghost)

    composite = CompositeVideoClip(layers)
    return composite.set_duration(clip.duration)
