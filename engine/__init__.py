"""
AI Video Producer Engine Package (V2 Enhanced).
"""
from engine.config import FFMPEG_EXE, RESOLUTIONS, VOICES
from engine.tts import synthesize_speech_with_words, generate_tiktok_style_subtitles
from engine.effects import (
    get_cinematic_image_filter,
    get_cinematic_video_filter,
    is_video_file,
)
from engine.render import render_scene_clip, assemble_final_video, get_best_bgm_track
from engine.script_generator import load_script_from_file, save_script_to_file
from engine.qa_inspector import inspect_video_output, run_qa_audit

__all__ = [
    "FFMPEG_EXE",
    "RESOLUTIONS",
    "VOICES",
    "synthesize_speech_with_words",
    "generate_tiktok_style_subtitles",
    "get_cinematic_image_filter",
    "get_cinematic_video_filter",
    "is_video_file",
    "render_scene_clip",
    "assemble_final_video",
    "get_best_bgm_track",
    "load_script_from_file",
    "save_script_to_file",
    "inspect_video_output",
    "run_qa_audit",
]
