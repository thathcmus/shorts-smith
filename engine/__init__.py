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
from engine.script_generator import (
    load_script_from_file,
    save_script_to_file,
    find_script_by_index_or_path,
    derive_default_output_name,
)
from engine.qa_inspector import inspect_video_output, run_qa_audit
from engine.publisher import (
    create_publish_workspace,
    generate_tiktok_caption,
    get_next_sequence_prefix,
    parse_sequence_and_slug,
    COVERS_DIR,
)
from engine.cover_designer import (
    create_tiktok_cover,
    design_cover_for_video_id,
)

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
    "find_script_by_index_or_path",
    "derive_default_output_name",
    "inspect_video_output",
    "run_qa_audit",
    "create_publish_workspace",
    "generate_tiktok_caption",
    "get_next_sequence_prefix",
    "parse_sequence_and_slug",
    "COVERS_DIR",
    "create_tiktok_cover",
    "design_cover_for_video_id",
]
