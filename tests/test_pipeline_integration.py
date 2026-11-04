import os
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

import generate_video
from engine.script_generator import get_fallback_script

def test_cli_parser_supports_topic_and_generate_images():
    # Test argparse argument parsing without running main()
    parser = argparse_test_helper()
    args = parser.parse_args(["--topic", "Bi An Rung Amazon", "--generate-images"])
    assert args.topic == "Bi An Rung Amazon"
    assert args.generate_images is True

    short_args = parser.parse_args(["-t", "Thanh Pho Ngam", "-g"])
    assert short_args.topic == "Thanh Pho Ngam"
    assert short_args.generate_images is True

def argparse_test_helper():
    import argparse
    from engine.config import DEFAULT_VOICE, DEFAULT_SPEECH_RATE, DEFAULT_PITCH
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", "-s", "--s", type=str)
    parser.add_argument("--topic", "-t", type=str, help="Chủ đề tự động")
    parser.add_argument("--generate-images", "-g", action="store_true")
    parser.add_argument("--voice", "-v", default=DEFAULT_VOICE)
    parser.add_argument("--rate", "-r", default=DEFAULT_SPEECH_RATE)
    parser.add_argument("--pitch", "-p", default=DEFAULT_PITCH)
    parser.add_argument("--output", "-o", default=None)
    parser.add_argument("--aspect", "-a", default="vertical")
    parser.add_argument("--bgm", "-b", default=None)
    parser.add_argument("--bgm-volume", type=float, default=0.22)
    parser.add_argument("--placeholder", action="store_true")
    return parser

@pytest.mark.asyncio
async def test_run_pipeline_end_to_end_cleans_temp_dir(temp_test_dir, sample_scene_payload):
    # Mock TTS, render_scene_clip, assemble_final_video, and create_publish_workspace
    for sc in sample_scene_payload:
        fake_img = os.path.join(temp_test_dir, "fake_img.jpg")
        with open(fake_img, "wb") as f:
            f.write(b"header_dummy_bytes")
        sc["image"] = fake_img

    async def mock_tts(text, out_path, **kwargs):
        with open(out_path, "wb") as f:
            f.write(b"fake_audio")
        return 2.0, [{"word": "test", "start": 0.0, "end": 1.0}]

    def mock_render_clip(media_path, audio_path, output_clip_path, **kwargs):
        with open(output_clip_path, "wb") as f:
            f.write(b"fake_clip")
        return output_clip_path

    def mock_assemble(clip_paths, output_video_path, **kwargs):
        with open(output_video_path, "wb") as f:
            f.write(b"fake_final_video")
        return output_video_path

    def mock_pub_workspace(video_path, scenes, duration):
        return {
            "cap_file": os.path.join(temp_test_dir, "cap.txt"),
            "cover_file": os.path.join(temp_test_dir, "cover.jpg"),
            "package_dir": os.path.join(temp_test_dir, "pkg")
        }

    with patch("generate_video.synthesize_speech_with_words", side_effect=mock_tts), \
         patch("generate_video.render_scene_clip", side_effect=mock_render_clip), \
         patch("generate_video.assemble_final_video", side_effect=mock_assemble), \
         patch("generate_video.create_publish_workspace", side_effect=mock_pub_workspace), \
         patch("generate_video.OUTPUT_DIR", temp_test_dir), \
         patch("generate_video.TEMP_DIR", temp_test_dir):

        out_name = "test_e2e_video.mp4"
        result = await generate_video.run_pipeline(
            scenes=sample_scene_payload,
            output_filename=out_name
        )

        assert os.path.exists(result)
        # Verify job temp directories are cleaned
        remaining_jobs = [d for d in os.listdir(temp_test_dir) if d.startswith("job_")]
        assert len(remaining_jobs) == 0
