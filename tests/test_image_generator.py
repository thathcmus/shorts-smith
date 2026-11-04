import os
import io
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from PIL import Image

from engine.image_generator import (
    fetch_image,
    generate_images_parallel,
    validate_image_file,
    POLLINATIONS_BASE_URL
)

@pytest.mark.asyncio
async def test_validate_image_file(temp_test_dir, mock_image_bytes):
    valid_path = os.path.join(temp_test_dir, "valid.jpg")
    with open(valid_path, "wb") as f:
        f.write(mock_image_bytes)
    assert validate_image_file(valid_path) is True

    # Truncated or small non-image payload (e.g. 5KB)
    small_path = os.path.join(temp_test_dir, "small_5kb.jpg")
    with open(small_path, "wb") as f:
        f.write(b"X" * 5000)
    assert validate_image_file(small_path) is False

    corrupt_path = os.path.join(temp_test_dir, "corrupt.jpg")
    with open(corrupt_path, "wb") as f:
        f.write(b"NOT_AN_IMAGE_DATA_TOO_SMALL")
    assert validate_image_file(corrupt_path) is False

    empty_path = os.path.join(temp_test_dir, "empty.jpg")
    with open(empty_path, "wb") as f:
        f.write(b"")
    assert validate_image_file(empty_path) is False

@pytest.mark.asyncio
async def test_fetch_image_success(temp_test_dir, mock_image_bytes):
    output_file = os.path.join(temp_test_dir, "test_scene_1.jpg")
    prompt = "Cinematic shot of ancient temple in jungle, 8k"

    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.read = AsyncMock(return_value=mock_image_bytes)

    mock_session = MagicMock()
    mock_session.get.return_value.__aenter__.return_value = mock_response

    result_path = await fetch_image(prompt, output_file, session=mock_session)

    assert result_path == output_file
    assert os.path.exists(output_file)
    assert os.path.getsize(output_file) >= 10240
    with Image.open(output_file) as img:
        assert img.size == (1080, 1920)

@pytest.mark.asyncio
async def test_fetch_image_retry_on_http_error(temp_test_dir, mock_image_bytes):
    output_file = os.path.join(temp_test_dir, "test_retry.jpg")
    prompt = "Futuristic neon city, dramatic lighting"

    fail_resp = AsyncMock()
    fail_resp.status = 500

    success_resp = AsyncMock()
    success_resp.status = 200
    success_resp.read = AsyncMock(return_value=mock_image_bytes)

    mock_session = MagicMock()
    mock_session.get.return_value.__aenter__.side_effect = [fail_resp, success_resp]

    with patch("asyncio.sleep", new_callable=AsyncMock):
        result_path = await fetch_image(prompt, output_file, max_retries=3, session=mock_session)

    assert result_path == output_file
    assert os.path.exists(output_file)
    assert mock_session.get.call_count == 2

@pytest.mark.asyncio
async def test_fetch_image_rejects_corrupted_image(temp_test_dir):
    output_file = os.path.join(temp_test_dir, "test_corrupt.jpg")
    prompt = "Corrupted test prompt"

    bad_resp = AsyncMock()
    bad_resp.status = 200
    bad_resp.read = AsyncMock(return_value=b"INVALID_HEADER_AND_CORRUPT")

    mock_session = MagicMock()
    mock_session.get.return_value.__aenter__.return_value = bad_resp

    with patch("asyncio.sleep", new_callable=AsyncMock):
        with pytest.raises(RuntimeError, match="Failed to download valid image after retries"):
            await fetch_image(prompt, output_file, max_retries=2, session=mock_session)

@pytest.mark.asyncio
async def test_generate_images_parallel(temp_test_dir, sample_scene_payload, mock_image_bytes):
    # Mock fetch_image to simulate parallel resolution without calling network
    async def mock_fetch(prompt, out_path, **kwargs):
        with open(out_path, "wb") as f:
            f.write(mock_image_bytes)
        return out_path

    with patch("engine.image_generator.fetch_image", side_effect=mock_fetch):
        downloaded = await generate_images_parallel(
            scenes=sample_scene_payload,
            target_dir=temp_test_dir,
            prefix="001_dead_internet"
        )

    assert len(downloaded) == len(sample_scene_payload)
    for idx, scene in enumerate(sample_scene_payload):
        assert "image" in scene
        assert os.path.exists(scene["image"])
        assert f"001_dead_internet_{idx+1}.jpg" in scene["image"]
