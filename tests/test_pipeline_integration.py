import os
import sys
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

import generate_video
from engine.script_generator import get_fallback_script

def test_cli_parser_supports_topic_and_generate_images():
    """Kiểm tra trực tiếp ArgumentParser của production trong generate_video.py."""
    parser = generate_video.build_arg_parser()
    args = parser.parse_args(["--topic", "Bi An Rung Amazon", "--generate-images"])
    assert args.topic == "Bi An Rung Amazon"
    assert args.generate_images is True

    short_args = parser.parse_args(["-t", "Thanh Pho Ngam", "-g"])
    assert short_args.topic == "Thanh Pho Ngam"
    assert short_args.generate_images is True

def test_pipeline_with_topic_triggers_script_and_image_generation(temp_test_dir):
    """Kiểm tra luồng --topic kích hoạt đầy đủ sinh kịch bản, sinh ảnh và nạp vào pipeline."""
    sample_topic = "Bí Ẩn Kim Tự Tháp Rừng Amazon"
    mock_script = get_fallback_script(sample_topic)

    mock_run_pipeline = AsyncMock(return_value=os.path.join(temp_test_dir, "001_video_test.mp4"))
    mock_gen_images = AsyncMock(return_value=[f"img_{i}.jpg" for i in range(6)])

    with patch.object(sys, "argv", ["generate_video.py", "--topic", sample_topic]), \
         patch("generate_video.generate_script_from_topic", return_value=mock_script) as mock_script_fn, \
         patch("generate_video.generate_images_parallel", mock_gen_images), \
         patch("generate_video.run_pipeline", mock_run_pipeline), \
         patch("generate_video.BASE_DIR", temp_test_dir), \
         patch("generate_video.OUTPUT_DIR", temp_test_dir):

        generate_video.main()

        mock_script_fn.assert_called_once_with(sample_topic)
        assert mock_gen_images.called
        assert mock_run_pipeline.called

def test_pipeline_with_existing_script_respects_existing_assets(temp_test_dir, sample_scene_payload):
    """Kiểm tra kịch bản có sẵn đầy đủ ảnh thì không tải lại nếu không có cờ -g."""
    fake_script = os.path.join(temp_test_dir, "001_script_test.json")
    with open(fake_script, "w", encoding="utf-8") as f:
        f.write("{}")

    # Tạo các tệp ảnh giả lập hợp lệ (> 10KB)
    for sc in sample_scene_payload:
        fake_img = os.path.join(temp_test_dir, "existing_valid.jpg")
        with open(fake_img, "wb") as f:
            f.write(b"X" * 12000)
        sc["image"] = fake_img

    mock_run_pipeline = AsyncMock(return_value="done.mp4")
    mock_gen_images = AsyncMock()

    with patch.object(sys, "argv", ["generate_video.py", "-s", "001"]), \
         patch("generate_video.find_script_by_index_or_path", return_value=fake_script), \
         patch("generate_video.load_script_from_file", return_value=sample_scene_payload), \
         patch("generate_video.validate_image_file", return_value=True), \
         patch("generate_video.generate_images_parallel", mock_gen_images), \
         patch("generate_video.run_pipeline", mock_run_pipeline):

        generate_video.main()

        # Không được gọi tải lại ảnh vì ảnh đã có sẵn và hợp lệ
        mock_gen_images.assert_not_called()
        assert mock_run_pipeline.called

@pytest.mark.asyncio
async def test_run_pipeline_end_to_end_cleans_temp_dir(temp_test_dir, sample_scene_payload):
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
