# Design Spec: Fix Video 007 Generation Issues (Image Concurrency, Voice Consistency, Script Quality)

## 1. Problem Statement & Root Cause Analysis

Video 007 ("Nền văn minh Maya") was generated but suffered from three major quality and pipeline defects:

1. **Visual Defect (Critical - 5/6 Blank Scenes):**
   - Scenes 2, 3, 4, 5, and 6 in `output/007_video_nen_van_minh_maya.mp4` render dark blue placeholder canvas boxes with generic text ("KHÁM PHÁ BÍ ẨN") instead of real AI images.
   - **Root Cause:** `engine/image_generator.py::generate_images_parallel` uses unbounded `asyncio.gather(*tasks)`, dispatching all 6 requests simultaneously. Free-tier `image.pollinations.ai` has a strict concurrency throttle, immediately returning HTTP 402/429/503. In `fetch_image`, receiving 402/429/503 executed `break` out of the retry loop. Wikimedia fallback search terms were overly specific (e.g. "towering Maya stone slab") returning 0 matches, silently triggering `generate_cinematic_canvas`.

2. **Audio Voice Inconsistency (Critical - Mid-video Gender Swap):**
   - Narration starts with `vi-VN-NamMinhNeural` (male) for Scenes 1-4, but abruptly switches to `vi-VN-HoaiMyNeural` (female) in Scenes 5-6.
   - **Root Cause:** `engine/tts.py::synthesize_speech_with_words` changed voice on retry attempts 2+: `cur_voice = voice if attempt < 2 else alt_voice`. This destroyed audio coherence for the video.

3. **Script Quality & Hallucination (Major - Nonsense Vietnamese):**
   - Scenes 2-5 contain hallucinated or ungrammatical pseudo-Vietnamese (e.g. "Thật cấu?", "vô vẩn, chữ tứ quẩn mênh mông", "bộ trạm chiếu quanh trục hoàng đạo", "băng kẽ lạnh à").
   - **Root Cause:** `text.pollinations.ai` free endpoint hallucinated terms when prompted for mystery shorts. The schema validator only checked for the existence of 6 scenes with non-empty text, allowing corrupted vocabulary to pass.

---

## 2. Architecture & Solution Strategy

### 2.1 AI Image Generation: Sequential Throttling & Resilient Fallback
- **Sequential / Semaphore Throttling:** In `engine/image_generator.py`, throttle downloads using an `asyncio.Semaphore(1)` with an asynchronous delay of 1.5s - 2.0s between requests.
- **Exponential Backoff on 402/429/503:** Do not `break` on 402/429/503; sleep with exponential backoff (`2.0s * (attempt + 1)`) and retry.
- **Broad Wikimedia Fallback:** Strip stylistic adjectives and use core entity nouns (e.g. `Maya pyramid ruins`, `ancient Maya civilization`) so Wikimedia Commons returns real historical documentary photographs.

### 2.2 Edge-TTS: Strict Voice Identity & SentenceBoundary Fallback
- **Voice Identity Invariance:** A video MUST maintain a single, consistent voice across all scenes. Remove mid-scene `alt_voice` switching.
- **WordBoundary Fallback Mechanism:** Microsoft Azure Edge-TTS drops connections with `NoAudioReceived` primarily when `boundary="WordBoundary"` is used on long sentences. The retry mechanism will:
  - Attempt 0: Primary voice with `boundary="WordBoundary"`.
  - Attempt 1+: Primary voice with standard `boundary="SentenceBoundary"` (no word boundary) and interpolate word timings evenly across duration.
  - Sleep 1.5s - 2.5s between retry attempts.

### 2.3 Script Generation: Quality Filtering & Mayan Civilization Script
- Improve `engine/script_generator.py` prompt and add sanity validation for unnatural characters or gibberish.
- Update `examples/007_script_nen_van_minh_maya.json` with an authentic, compelling viral Vietnamese script detailing real Mayan mysteries (Chichen Itza, calendar, astronomical accuracy, sudden collapse).

### 2.4 End-to-End Verification & Re-rendering
- Run automated unit and integration tests (`tests/`).
- Regenerate high-resolution AI images for all 6 scenes of Video 007.
- Re-render `007_video_nen_van_minh_maya.mp4`, generate cover thumbnail, TikTok caption, and update the publish package.
- Verify frame pixels and audio waveform integrity.
