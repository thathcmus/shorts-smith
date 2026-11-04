import os
import subprocess
import pytest
from unittest.mock import patch, MagicMock

from engine.render import (
    sanitize_ffmpeg_path,
    clean_temp_files,
    assemble_final_video
)

def test_sanitize_ffmpeg_path_windows_colons_and_spaces():
    raw_path = r"C:\Users\User Name\7_Media\sub.ass"
    safe = sanitize_ffmpeg_path(raw_path)
    assert safe == "C\\:/Users/User Name/7_Media/sub.ass"

    # Forward slash path with drive letter
    raw_path_fwd = "E:/7_Media/temp_build/job_123/tiktok_karaoke.ass"
    safe_fwd = sanitize_ffmpeg_path(raw_path_fwd)
    assert safe_fwd == "E\\:/7_Media/temp_build/job_123/tiktok_karaoke.ass"

    # Single quote escaping
    raw_quote = r"C:\Users\John's Media\sub.ass"
    safe_quote = sanitize_ffmpeg_path(raw_quote)
    assert safe_quote == r"C\:/Users/John\'s Media/sub.ass"

def test_assemble_final_video_captures_stderr_on_error(temp_test_dir):
    clip_paths = [os.path.join(temp_test_dir, "clip1.mp4")]
    out_video = os.path.join(temp_test_dir, "out.mp4")

    # Mock subprocess.run to simulate FFmpeg failure with stderr output
    def mock_run(cmd, *args, **kwargs):
        raise subprocess.CalledProcessError(
            returncode=1,
            cmd=cmd,
            stderr="[ffmpeg error] Invalid filter syntax: subtitles filter failed"
        )

    with patch("subprocess.run", side_effect=mock_run):
        with pytest.raises(RuntimeError, match=r"(?s)FFmpeg assembly failed.*Invalid filter syntax"):
            assemble_final_video(
                clip_paths=clip_paths,
                output_video_path=out_video,
                temp_dir=temp_test_dir
            )

def test_clean_temp_files_removes_root_orphans_and_job_dir(temp_test_dir):
    # Create fake job directory
    job_dir = os.path.join(temp_test_dir, "job_test_123")
    os.makedirs(job_dir, exist_ok=True)
    with open(os.path.join(job_dir, "test.tmp"), "w") as f:
        f.write("tmp data")

    # Create orphan test files in root mock
    orphan1 = os.path.join(temp_test_dir, "temp_test_0.mp3")
    orphan2 = os.path.join(temp_test_dir, "tmp_scene.mp3")
    keeper = os.path.join(temp_test_dir, "keep_me.txt")
    with open(orphan1, "w") as f:
        f.write("junk")
    with open(orphan2, "w") as f:
        f.write("junk")
    with open(keeper, "w") as f:
        f.write("keep")

    # Clean
    clean_temp_files(job_dir=job_dir, root_dir=temp_test_dir)

    assert not os.path.exists(job_dir)
    assert not os.path.exists(orphan1)
    assert not os.path.exists(orphan2)
    assert os.path.exists(keeper)
