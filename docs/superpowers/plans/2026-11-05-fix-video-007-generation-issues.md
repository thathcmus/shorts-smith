# Fix Video 007 Generation Issues Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the root causes that caused defective output in Video 007 (dark blue placeholder canvases on 5/6 scenes, mid-video voice gender swap, and garbled script vocabulary), add regression unit tests, and re-produce Video 007 to high cinematic quality.

**Architecture:** Implement concurrency throttling (`asyncio.Semaphore(1)` + inter-request cooldown) and retry backoff on free-tier Pollinations AI image generation with broadened Wikimedia search fallback. Enforce strict single-voice identity across all scenes in `engine/tts.py` while gracefully degrading to `SentenceBoundary` with word interpolation on server errors. Update `examples/007_script_nen_van_minh_maya.json` with authentic, compelling Vietnamese narration, and re-run full pipeline rendering.

**Tech Stack:** Python 3.14, asyncio, aiohttp, edge-tts, FFmpeg (`imageio-ffmpeg`), Pillow, pytest, pytest-asyncio.

**Spec:** `docs/superpowers/specs/2026-11-05-fix-video-007-generation-issues-design.md`

## Global Constraints
- Zero-cost (F2P 100%): Never introduce paid APIs or require credit card keys.
- Preserve 9:16 vertical resolution (1080x1920), 1.5x pacing, TikTok dynamic subtitles, and BGM ducking.
- Windows file:// clickable path links for all generated media files in chat response.
- All test files under `tests/` must pass (`pytest -v`).

## Review Focus
- Free-tier HTTP 402/429/503 rate limits on concurrent Pollinations image requests triggering placeholder canvas fallback.
- Voice identity swapping mid-video between male and female narration.
- Edge-TTS `NoAudioReceived` on Vietnamese phrases with `boundary="WordBoundary"`.
- Hallucinated pseudo-Vietnamese text from text generation endpoints.
- Image center-crop and aspect ratio preservation to exactly 1080x1920 (9:16).

---

### Task 1: AI Image Generator Throttling & Resilient Retry

**Files:**
- Modify: `engine/image_generator.py:40-220`
- Test: `tests/test_image_generator.py`

**Interfaces:**
- Consumes: `extract_search_terms(prompt: str) -> str`, `fetch_image(prompt, output_path, width, height, ...)`
- Produces: `generate_images_parallel(scenes: list, target_dir: str, prefix: str, width: int, height: int, concurrency: int = 1, delay: float = 1.5) -> list[str]`

- [ ] **Step 1: Write the failing test for sequential throttling and retry backoff on HTTP 402/429**

In `tests/test_image_generator.py`:
```python
@pytest.mark.asyncio
async def test_generate_images_throttled_sequential(tmp_path, monkeypatch):
    from engine.image_generator import generate_images_parallel
    calls = []
    async def mock_fetch(prompt, out_path, **kwargs):
        calls.append(out_path)
        with open(out_path, "wb") as f:
            f.write(b"\xff\xd8\xff\xe0" + b"\x00" * 11000)
        return out_path
    monkeypatch.setattr("engine.image_generator.fetch_image", mock_fetch)
    scenes = [{"prompt": f"test prompt {i}"} for i in range(3)]
    res = await generate_images_parallel(scenes, str(tmp_path), prefix="throttle_test", delay=0.05)
    assert len(res) == 3
    assert len(calls) == 3
```

- [ ] **Step 2: Run test to verify it fails or needs parameter updates**

Run: `python -m pytest tests/test_image_generator.py::test_generate_images_throttled_sequential -v`
Expected: FAIL if `delay` parameter is not supported or behavior differs.

- [ ] **Step 3: Implement sequential throttling, backoff retry, and broadened search query**

In `engine/image_generator.py`:
1. In `extract_search_terms(prompt: str)`: Extract 2-3 essential subject keywords (e.g. nouns), stripping adjectives, camera terms, and styles. If query is empty or too long, default to subject root.
2. In `fetch_image`: On `resp.status in (402, 429, 503)`: do NOT immediately `break`; instead wait with exponential backoff (`await asyncio.sleep(2.0 * (attempt + 1))`) and retry up to `max_retries`.
3. In `generate_images_parallel`: Add `semaphore = asyncio.Semaphore(1)` and an inter-request delay (`await asyncio.sleep(delay)`) between scenes so the free endpoint is not overwhelmed.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_image_generator.py -v`
Expected: PASS (all image generator tests passing).

- [ ] **Step 5: Commit**

```bash
git add engine/image_generator.py tests/test_image_generator.py
git commit -m "fix(image_gen): throttle concurrent image downloads and improve retry backoff"
```

---

### Task 2: Strict Voice Identity Invariance & Edge-TTS Fallback

**Files:**
- Modify: `engine/tts.py:20-95`
- Test: `tests/test_tts_resilience.py` (Create)

**Interfaces:**
- Consumes: `DEFAULT_VOICE`, `DEFAULT_SPEECH_RATE`, `DEFAULT_PITCH` from `engine.config`
- Produces: `synthesize_speech_with_words(text: str, output_audio: str, voice: str, rate: str, volume: str, pitch: str, max_retries: int) -> tuple[float, list]`

- [ ] **Step 1: Write unit test verifying voice identity invariance across retries**

Create `tests/test_tts_resilience.py`:
```python
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from engine.tts import synthesize_speech_with_words

@pytest.mark.asyncio
async def test_voice_identity_remains_strictly_consistent_on_retry(tmp_path):
    out_audio = str(tmp_path / "scene_voice.mp3")
    communicator_instances = []

    def mock_communicate_init(self, text, voice="en-US-EmmaMultilingualNeural", **kwargs):
        self._voice = voice
        communicator_instances.append(voice)
        self.stream = AsyncMock()

    with patch("edge_tts.Communicate", side_effect=mock_communicate_init):
        # We simulate the first call failing and second succeeding
        try:
            await synthesize_speech_with_words("Chào bạn", out_audio, voice="vi-VN-NamMinhNeural", max_retries=2)
        except Exception:
            pass
        # All initiated instances must strictly use vi-VN-NamMinhNeural
        for v in communicator_instances:
            assert v == "vi-VN-NamMinhNeural"
```

- [ ] **Step 2: Run test to verify it fails if voice changes**

Run: `python -m pytest tests/test_tts_resilience.py -v`
Expected: FAIL if `cur_voice` switches to `alt_voice` on attempt 2+.

- [ ] **Step 3: Update `engine/tts.py` to maintain voice invariance and use `SentenceBoundary` interpolation on retry**

In `engine/tts.py`:
1. Remove `alt_voice` switching in `synthesize_speech_with_words`. Retain `voice` for all retry attempts to prevent mid-video gender changes.
2. In retry loop:
   - Attempt 0: `use_wb = True` (try `WordBoundary`).
   - Attempt 1+: `use_wb = False` (omit `boundary` argument, fallback to standard synthesis, and interpolate word timings evenly across `dur`).
   - Backoff wait: `await asyncio.sleep(1.5 * (attempt + 1))` before retrying.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_tts_resilience.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add engine/tts.py tests/test_tts_resilience.py
git commit -m "fix(tts): ensure single-voice identity invariance across all scene retries"
```

---

### Task 3: Script Quality Validation & Authentic Mayan Civilization Script

**Files:**
- Modify: `engine/script_generator.py:75-125`
- Modify: `examples/007_script_nen_van_minh_maya.json`
- Test: `tests/test_script_generator.py`

**Interfaces:**
- Consumes: `topic: str`, `style: str`
- Produces: `generate_script_from_topic(topic: str, style: str) -> dict`, `is_script_vietnamese_fluent(scenes: list) -> bool`

- [ ] **Step 1: Write failing test for script fluency validation**

In `tests/test_script_generator.py`:
```python
def test_is_script_vietnamese_fluent_rejects_garbled_vocabulary():
    from engine.script_generator import is_script_vietnamese_fluent
    garbled_scenes = [
        {"text": "Bản đồ đều vô vẩn, chữ tứ quẩn mênh mông!"},
        {"text": "Họ khắc hòm sao trên đá trong toàn Thiên Dương"},
    ]
    assert is_script_vietnamese_fluent(garbled_scenes) is False

    fluent_scenes = [
        {"text": "Bạn có biết người Maya đã xây dựng những kim tự tháp kỳ vĩ sâu trong rừng thẳm?"},
        {"text": "Hệ thống lịch thiên văn của họ chính xác đến từng chu kỳ mặt trời và các vì sao!"},
    ]
    assert is_script_vietnamese_fluent(fluent_scenes) is True
```

- [ ] **Step 2: Run test to verify failure**

Run: `python -m pytest tests/test_script_generator.py::test_is_script_vietnamese_fluent_rejects_garbled_vocabulary -v`
Expected: FAIL with `ImportError: cannot import name 'is_script_vietnamese_fluent'`.

- [ ] **Step 3: Implement `is_script_vietnamese_fluent` and update Mayan script**

1. In `engine/script_generator.py`:
   - Implement `is_script_vietnamese_fluent(scenes: list) -> bool`: check for garbled terms (`vô vẩn`, `tứ quẩn`, `thổi chiều`, `khai hình`, `hòm sao`, etc.) and ensure average word length and diacritic ratios match natural Vietnamese.
   - If AI generation produces garbled output, fall back to `get_fallback_script`.
2. In `examples/007_script_nen_van_minh_maya.json`:
   - Write an authentic, accurate, viral 6-scene script on Mayan Civilization:
     - Hook: Thành phố cổ Chichen Itza và sự biến mất bí ẩn của hàng triệu người Maya.
     - Fact 1: Kim tự tháp Kukulkan tạo hình bóng rắn trườn trong ngày xuân phân.
     - Anomaly: Không dùng bánh xe hay kim loại nhưng xây công trình vĩ đại.
     - Theory: Giả thuyết về nguồn gốc kiến thức thiên văn vượt thời đại.
     - Coincidence: Độ chuẩn xác đến kinh ngạc của bộ lịch Maya 260 ngày và 365 ngày.
     - CTA: Đặt câu hỏi kích thích người xem bình luận.
   - Pair with detailed, clean English prompts for 9:16 vertical AI image generation.

- [ ] **Step 4: Run tests to verify all pass**

Run: `python -m pytest tests/test_script_generator.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add engine/script_generator.py examples/007_script_nen_van_minh_maya.json tests/test_script_generator.py
git commit -m "fix(script): add linguistic sanity filter and write authentic Mayan civilization script"
```

---

### Task 4: Re-generate Video 007 Assets & End-to-End Re-render Verification

**Files:**
- Asset Directory: `sample_assets/007_nen_van_minh_maya/`
- Output Video: `output/007_video_nen_van_minh_maya.mp4`
- Cover: `output/covers/007_cover_nen_van_minh_maya.jpg`
- Caption: `output/cap/007_cap_nen_van_minh_maya.txt`
- Package: `output/publish_packages/007_nen_van_minh_maya/`

**Interfaces:**
- Consumes: `examples/007_script_nen_van_minh_maya.json`
- Produces: 6 real high-res AI images (1080x1920), 1080x1920 MP4 video, ASS subtitles, cover image, caption file.

- [ ] **Step 1: Clear old defective assets for 007**

Run: Remove old sample assets in `sample_assets/007_nen_van_minh_maya/` to allow full re-generation with the throttled pipeline.

- [ ] **Step 2: Download 6 AI images using throttled generator**

Run: `python generate_video.py -s 007 --generate-images`
Verify: All 6 images are real photographs/renders (> 25KB each, non-canvas).

- [ ] **Step 3: Render complete video 007**

Run: `python generate_video.py -s 007`
Verify:
1. Video renders to `output/007_video_nen_van_minh_maya.mp4`.
2. Audio uses a single consistent voice (`vi-VN-NamMinhNeural` or `vi-VN-HoaiMyNeural`) throughout all 6 scenes.
3. Every scene shows an authentic AI image with Ken Burns cinematic animation (no blue placeholder screens).
4. Subtitles synchronize with karaoke highlighting.
5. Cover thumbnail and TikTok caption package created.

- [ ] **Step 4: Run full test suite regression**

Run: `python -m pytest -v`
Expected: PASS (100% of tests passing).

- [ ] **Step 5: Verify output with FFmpeg probe**

Run verification command to confirm video duration (~30s), stream codecs (h264, aac), and resolution (1080x1920).

- [ ] **Step 6: Commit**

```bash
git add output/007_video_nen_van_minh_maya.mp4 output/covers/007_cover_nen_van_minh_maya.jpg output/cap/007_cap_nen_van_minh_maya.txt output/publish_packages/007_nen_van_minh_maya/
git commit -m "feat(video007): produce verified, high-quality Mayan civilization video"
```
