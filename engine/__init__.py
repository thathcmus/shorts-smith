"""
AI Video Producer Engine Package.
"""
from engine.config import FFMPEG_EXE, RESOLUTIONS, VOICES
from engine.tts import synthesize_speech, generate_ass_subtitles
from engine.effects import get_ken_burns_filter
from engine.render import render_scene_clip, create_tension_bgm, assemble_final_video
from engine.script_generator import load_script_from_file, save_script_to_file

__all__ = [
    "FFMPEG_EXE",
    "RESOLUTIONS",
    "VOICES",
    "synthesize_speech",
    "generate_ass_subtitles",
    "get_ken_burns_filter",
    "render_scene_clip",
    "create_tension_bgm",
    "assemble_final_video",
    "load_script_from_file",
    "save_script_to_file",
]
