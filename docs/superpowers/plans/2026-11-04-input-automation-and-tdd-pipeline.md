# Input Automation & TDD Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a fully automated end-to-end media pipeline that takes a single topic string, generates a structured 6-scene viral script, downloads 6 AI 9:16 images in parallel for free, and renders the video with subtitles, audio, and packaging, verified by automated TDD tests.

**Architecture:** Modular pipeline where `engine/image_generator.py` handles parallel async image fetching with Pillow validation, `engine/script_generator.py` converts topics to structured 6-scene scripts with offline fallback, and `generate_video.py` orchestrates the pipeline with safe temp directory lifecycles and sanitized FFmpeg invocations.

**Tech Stack:** Python 3.10+, `aiohttp`, `requests`, `edge-tts`, `imageio-ffmpeg`, `pillow`, `pytest`, `pytest-asyncio`.

**Spec:** `docs/superpowers/specs/2026-11-04-input-automation-and-tdd-pipeline-design.md`

## Global Constraints

- Must run on Windows 10/11 using PowerShell and standard Python 3.10+.
- Zero paid API keys (F2P 100%): All generation must use free cloud endpoints (Pollinations.ai / Edge-TTS) or local fallback.
- No heavy local ML frameworks (no PyTorch/CUDA/ComfyUI required).
- All image downloads for a 6-scene video must execute asynchronously in parallel (`asyncio.gather`), not sequentially.
- Backward compatibility: Existing JSON scripts (`examples/001_*.json` to `006_*.json`) and CLI options (`-s 003`) must continue working.
- FFmpeg subprocess invocations must never redirect stderr to `DEVNULL` when errors occur, and all file paths must be sanitized for Windows.
- All temporary files must stay isolated in `temp_build/job_{timestamp}/` and be cleaned up.

## Review Focus

1. **Network drop or HTTP 500/429 during image fetch:** System retries 3 times with backoff, fails with informative error instead of silent crash. Tested in Task 2.
2. **Corrupted or truncated image returned by API:** Pillow validation detects invalid image header or file size < 10KB and triggers retry. Tested in Task 2.
3. **Special characters or spaces in Windows paths for FFmpeg filters:** Paths containing spaces, colons, and non-ASCII characters correctly escaped for `subtitles` filter and `concat` demuxer. Tested in Task 4.
4. **Offline/network failure during topic script generation:** Script generator invokes offline fallback template preserving 6-scene viral structure without failing. Tested in Task 3.
5. **Orphaned temporary audio/video files lingering in root directory:** Pipeline safely registers cleanup handlers so no `temp_*.mp3` or dangling files escape `temp_build/`. Tested in Task 4.

---

### Task 1: Setup Testing Infrastructure & Pytest Environment

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`
- Create: `pytest.ini`

**Interfaces:**
- Produces: Test runner configuration and shared fixtures for mocking HTTP requests (`aiohttp` and `requests`) and sample scene payloads.

- [ ] **Step 1: Install pytest and pytest-asyncio**

Command:
```powershell
pip install pytest pytest-asyncio
```

- [ ] **Step 2: Create `pytest.ini`**

Configure test discovery and asyncio mode:
```ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
```

- [ ] **Step 3: Create `tests/__init__.py` and `tests/conftest.py` with mock fixtures**

In `tests/conftest.py`, define fixtures:
- `sample_scene_payload`: Returns a list of 6 mock scene dictionaries with `text`, `effect`, and `prompt`.
- `mock_image_bytes`: Returns valid 1080x1920 JPEG binary bytes generated using Pillow in-memory.
- `temp_test_dir`: Yields a temporary directory cleaned up after test run.

- [ ] **Step 4: Verify test runner works**

Run: `pytest`
Expected: `no tests ran in ...` with exit code 5 (or 0 with no errors).

- [ ] **Step 5: Commit testing setup**

```powershell
git add pytest.ini tests/
git commit -m "chore: setup pytest and testing infrastructure with conftest fixtures"
```

---

### Task 2: AI Cloud Image Generator (`engine/image_generator.py`)

**Files:**
- Create: `engine/image_generator.py`
- Create: `tests/test_image_generator.py`

**Interfaces:**
- Produces:
  - `async def fetch_image(prompt: str, output_path: str, width: int = 1080, height: int = 1920, max_retries: int = 3, session: aiohttp.ClientSession = None) -> str`
  - `async def generate_images_parallel(scenes: list, target_dir: str, width: int = 1080, height: int = 1920) -> list[str]`
- Consumes: `aiohttp`, `PIL.Image`, `urllib.parse.quote`.

- [ ] **Step 1: Write the failing tests in `tests/test_image_generator.py`**

Cover:
- `test_fetch_image_success`: Successfully writes valid image file when API returns 200 with valid JPEG.
- `test_fetch_image_retry_on_http_error`: Retries on 500 error and succeeds on subsequent 200 response.
- `test_fetch_image_rejects_corrupted_image`: Rejects data < 10KB or invalid image headers, raising RuntimeError when retries exhausted.
- `test_generate_images_parallel`: Downloads multiple scenes in parallel using `asyncio.gather` and saves to `target_dir/scene_{idx}.jpg`.

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_image_generator.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'engine.image_generator'`.

- [ ] **Step 3: Implement `engine/image_generator.py`**

Implement:
- `POLLINATIONS_BASE_URL = "https://image.pollinations.ai/prompt"`
- `fetch_image`: URL-encodes prompt, calls Pollinations endpoint with query params `width`, `height`, `model=flux`, `nologo=true`, verifies image integrity using `PIL.Image.open()`, retries up to `max_retries` with exponential backoff (`asyncio.sleep(1.5 * attempt)`).
- `generate_images_parallel`: Identifies scenes without valid existing `image` files, prepares output paths (`target_dir/{seq}_{slug}_{idx+1}.jpg`), and executes downloads concurrently with `asyncio.gather(*tasks)`. Updates `scene["image"]` in-place.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_image_generator.py -v`
Expected: All 4 tests PASS.

- [ ] **Step 5: Commit**

```powershell
git add engine/image_generator.py tests/test_image_generator.py
git commit -m "feat: implement parallel cloud AI image generator with Pillow validation"
```

---

### Task 3: Intelligent Script Generation & Fallback (`engine/script_generator.py`)

**Files:**
- Modify: `engine/script_generator.py`
- Create: `tests/test_script_generator.py`

**Interfaces:**
- Produces:
  - `def generate_script_from_topic(topic: str, style: str = "mystery") -> dict`
  - `def get_fallback_script(topic: str, style: str = "mystery") -> dict`
- Consumes: `json`, `requests`, `engine.script_generator.TEMPLATES`.

- [ ] **Step 1: Write the failing tests in `tests/test_script_generator.py`**

Cover:
- `test_generate_script_schema`: Output dictionary contains `"scenes"` with exactly 6 items, each containing non-empty `"text"`, `"effect"`, and `"prompt"`.
- `test_generate_script_prompts_are_english_cinematic`: Every scene prompt contains cinematic keywords (`cinematic`, `8k`, `lighting` or `dramatic`).
- `test_fallback_script_on_network_failure`: When HTTP connection fails or times out, `generate_script_from_topic` falls back to `get_fallback_script` cleanly without raising an unhandled exception.
- `test_backward_compatibility_find_script`: Existing `find_script_by_index_or_path("001")` still works as expected.

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_script_generator.py -v`
Expected: FAIL with `ImportError: cannot import name 'generate_script_from_topic' from 'engine.script_generator'`.

- [ ] **Step 3: Implement `generate_script_from_topic` in `engine/script_generator.py`**

Implement:
- `SYSTEM_PROMPT` tailored for 6 viral short scenes (`hook`, `fact1`, `anomaly`, `theory`, `coincidence`, `cta`).
- Free text LLM endpoint call (Pollinations text API / HuggingFace public router) with a 10-second timeout.
- JSON response parser that extracts the structured scene array.
- `get_fallback_script(topic: str, style: str)` which creates a dynamic 6-scene script using templated sentence structures and English visual prompts based on the topic keywords if the remote API is unreachable.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_script_generator.py -v`
Expected: All tests in `tests/test_script_generator.py` PASS.

- [ ] **Step 5: Commit**

```powershell
git add engine/script_generator.py tests/test_script_generator.py
git commit -m "feat: add topic-based 6-scene viral script generation with offline fallback"
```

---

### Task 4: FFmpeg Path Sanitization, Error Logging & Resource Cleanup

**Files:**
- Modify: `engine/render.py`
- Modify: `engine/config.py`
- Create: `tests/test_render_safety.py`

**Interfaces:**
- Produces:
  - `def sanitize_ffmpeg_path(path: str) -> str`
  - `def clean_temp_files(job_dir: str = None)`
  - Enhanced `assemble_final_video` raising `RuntimeError` with full stderr on failure.
- Consumes: `os`, `re`, `subprocess`, `shutil`.

- [ ] **Step 1: Write the failing tests in `tests/test_render_safety.py`**

Cover:
- `test_sanitize_ffmpeg_path_windows_colons_and_spaces`: Converts `C:\path with spaces\sub.ass` to `C\:/path with spaces/sub.ass` safe for FFmpeg filter syntax.
- `test_assemble_final_video_captures_stderr_on_error`: When FFmpeg fails, raises `RuntimeError` containing the captured stderr rather than hiding it.
- `test_clean_temp_files_removes_root_orphans_and_job_dir`: Removes job directory and any orphaned `temp_test_*.mp3` files in project root.

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_render_safety.py -v`
Expected: FAIL with `ImportError: cannot import name 'sanitize_ffmpeg_path' from 'engine.render'`.

- [ ] **Step 3: Implement path sanitization and error logging in `engine/render.py`**

Implement:
- `sanitize_ffmpeg_path(path: str) -> str`: Normalizes path with forward slashes and escapes colons (`:` -> `\:`).
- In `assemble_final_video`:
  - Use `subprocess.PIPE` for `stderr` instead of `subprocess.DEVNULL`.
  - Wrap in `try ... except subprocess.CalledProcessError as e:` and raise `RuntimeError(f"FFmpeg assembly failed:\n{e.stderr}")`.
- Implement `clean_temp_files(job_dir: str)`: Cleans `job_dir` and purges any orphaned `temp_*.mp3` / `tmp_*.mp3` files from the project root.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_render_safety.py -v`
Expected: All tests in `tests/test_render_safety.py` PASS.

- [ ] **Step 5: Commit**

```powershell
git add engine/render.py engine/config.py tests/test_render_safety.py
git commit -m "fix: sanitize FFmpeg filter paths, surface stderr on failure, and clean temp files"
```

---

### Task 5: End-to-End CLI Pipeline Integration (`generate_video.py`)

**Files:**
- Modify: `generate_video.py`
- Create: `tests/test_pipeline_integration.py`

**Interfaces:**
- Produces:
  - CLI arguments `--topic` / `-t`, `--generate-images` / `-g`.
  - Seamless lifecycle: Topic -> Script -> Parallel AI Images -> Audio & Subtitles -> Ken Burns & Mix -> Thumbnail & Caption Package -> Safe Cleanup.
- Consumes: `engine.image_generator`, `engine.script_generator`, `engine.render`, `engine.publisher`.

- [ ] **Step 1: Write the failing tests in `tests/test_pipeline_integration.py`**

Cover:
- `test_pipeline_with_topic_triggers_script_and_image_generation`: Mocking external networks (TTS and Image API), verify that providing `--topic "Bi An Kim Tu Thap"` triggers script generation, downloads images, produces packaging, and cleans temp directory.
- `test_pipeline_with_existing_script_respects_existing_assets`: Verifies that specifying `-s 001` without `-g` uses existing assets without redundant downloads.

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_pipeline_integration.py -v`
Expected: FAIL due to missing `--topic` CLI parsing in `generate_video.py`.

- [ ] **Step 3: Update `generate_video.py`**

Implement:
- Add argparse arguments:
  - `-t`, `--topic`: Text topic to automatically generate a video.
  - `-g`, `--generate-images`: Force generating new AI images even if local files exist.
- In `run_pipeline`:
  - If `topic` is provided: call `generate_script_from_topic(topic)`, determine next sequence prefix (`00X`), derive slug, save script to `examples/{seq}_script_{slug}.json`.
  - Check missing scene images or if `generate_images` flag is set: invoke `await generate_images_parallel(scenes, asset_dir)`.
  - Wrap pipeline execution in a `try ... finally:` block to ensure `clean_temp_files(job_temp_dir)` is always invoked.
  - Update `engine/publisher.py` to package the generated metadata.

- [ ] **Step 4: Run the full test suite**

Run: `pytest`
Expected: 100% of test suite PASSES with pristine output.

- [ ] **Step 5: Commit**

```powershell
git add generate_video.py tests/test_pipeline_integration.py
git commit -m "feat: complete end-to-end topic-to-video CLI pipeline integration"
```
