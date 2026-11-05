"""
Module sinh ảnh AI đám mây miễn phí chất lượng cao (Free AI Cloud Image Generator).
Kết nối trực tiếp tới API Pollinations.ai (100% miễn phí, không cần token/key),
hỗ trợ fallback sang kho tư liệu độ phân giải cao Wikimedia Commons khi máy chủ AI bị giới hạn,
tải song song 6 cảnh bằng asyncio, xác thực ảnh hợp lệ bằng Pillow và tự động retry khi gặp lỗi mạng.
"""
import asyncio
import io
import os
import random
import re
import urllib.parse
import aiohttp
from PIL import Image

POLLINATIONS_BASE_URL = "https://image.pollinations.ai/prompt"

def validate_image_file(image_path: str) -> bool:
    """
    Kiểm tra tệp ảnh có hợp lệ, không bị lỗi hỏng (corrupted) và có kích thước tối thiểu.
    """
    if not os.path.exists(image_path):
        return False
    # Kích thước phải lớn hơn ít nhất 10KB
    if os.path.getsize(image_path) < 10240:
        return False
    try:
        with Image.open(image_path) as img:
            img.verify()
        return True
    except Exception:
        return False

def extract_search_terms(prompt: str) -> str:
    """Loại bỏ các từ khóa phong cách chung để lấy thực thể chính phục vụ tìm kiếm ảnh tư liệu."""
    p = prompt.lower()
    for drop in [
        "cinematic", "8k", "dramatic lighting", "vertical composition",
        "dramatic light flicker", "hyper-detailed", "atmospheric", "volumetric light",
        "close-up", "establishing shot", "concept art", "photorealistic", "ultra realistic"
    ]:
        p = p.replace(drop, "")
    words = [w for w in re.split(r"[^a-zA-Z0-9]+", p) if len(w) > 3]
    return " ".join(words[:4]) or "history discovery"

async def fetch_wikimedia_fallback(
    prompt: str,
    output_path: str,
    width: int = 1080,
    height: int = 1920,
    session: aiohttp.ClientSession = None
) -> str:
    """Tìm kiếm ảnh chất lượng cao trên Wikimedia Commons khi máy chủ AI bị giới hạn."""
    query = extract_search_terms(prompt)
    encoded_q = urllib.parse.quote(query)
    api_url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrnamespace=6&gsrsearch={encoded_q}&gsrlimit=3&prop=imageinfo&iiprop=url&format=json"

    close_session = False
    if session is None:
        session = aiohttp.ClientSession()
        close_session = True

    try:
        headers = {"User-Agent": "MediaProducerAI/2.0 (Wikimedia Integration)"}
        async with session.get(api_url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            if resp.status == 200:
                data = await resp.json()
                pages = data.get("query", {}).get("pages", {})
                for page in pages.values():
                    img_info = page.get("imageinfo", [])
                    if img_info and "url" in img_info[0]:
                        img_url = img_info[0]["url"]
                        if img_url.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                            async with session.get(img_url, headers=headers, timeout=aiohttp.ClientTimeout(total=20)) as img_resp:
                                if img_resp.status == 200:
                                    raw_bytes = await img_resp.read()
                                    raw_buf = io.BytesIO(raw_bytes)
                                    with Image.open(raw_buf) as img:
                                        img = img.convert("RGB")
                                        w, h = img.size
                                        target_ratio = width / height
                                        if w / h > target_ratio:
                                            new_w = int(h * target_ratio)
                                            left = (w - new_w) // 2
                                            img = img.crop((left, 0, left + new_w, h))
                                        else:
                                            new_h = int(w / target_ratio)
                                            top = (h - new_h) // 2
                                            img = img.crop((0, top, w, top + new_h))
                                        img = img.resize((width, height), Image.Resampling.LANCZOS)
                                        img.save(output_path, format="JPEG", quality=90)
                                    if validate_image_file(output_path):
                                        return output_path
    except Exception:
        pass
    finally:
        if close_session:
            await session.close()
    return None

def generate_cinematic_canvas(prompt: str, output_path: str, width: int = 1080, height: int = 1920) -> str:
    """Tạo ảnh canvas điện ảnh dự phòng tuyệt đối khi mọi dịch vụ mạng đều bất khả dụng."""
    from PIL import ImageDraw
    img = Image.new("RGB", (width, height), color=(18, 24, 38))
    draw = ImageDraw.Draw(img)
    draw.rectangle([40, 40, width - 40, height - 40], outline=(0, 229, 255), width=4)
    draw.text((width // 2, 700), "KHÁM PHÁ BÍ ẨN", fill=(255, 230, 0), anchor="mm")
    
    clean_p = prompt if len(prompt) < 100 else prompt[:100] + "..."
    draw.text((width // 2, 850), clean_p, fill=(255, 255, 255), anchor="mm")
    img.save(output_path, format="JPEG", quality=90)
    return output_path

async def fetch_image(
    prompt: str,
    output_path: str,
    width: int = 1080,
    height: int = 1920,
    max_retries: int = 3,
    session: aiohttp.ClientSession = None,
    allow_fallback: bool = True
) -> str:
    """
    Tải 1 ảnh AI từ Pollinations.ai (model=turbo).
    Nếu gặp sự cố giới hạn lượt tải (402/503), tự động kích hoạt fallback tư liệu Wikimedia Commons.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # URL Encode prompt để an toàn với ký tự đặc biệt
    clean_prompt = prompt.strip()
    encoded_prompt = urllib.parse.quote(clean_prompt)
    seed = random.randint(1000, 999999)
    
    # Kiểm tra xem có API key trong môi trường hay không
    pollen_key = os.environ.get("POLLEN_KEY") or os.environ.get("POLLINATIONS_API_KEY")
    key_param = f"&key={pollen_key}" if pollen_key else ""
    url = f"{POLLINATIONS_BASE_URL}/{encoded_prompt}?width={width}&height={height}&model=turbo&nologo=true&seed={seed}{key_param}"

    close_session = False
    if session is None:
        session = aiohttp.ClientSession()
        close_session = True

    try:
        last_error = None
        for attempt in range(max_retries):
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=35)) as resp:
                    if resp.status == 200:
                        content = await resp.read()
                        with open(output_path, "wb") as f:
                            f.write(content)
                        
                        if validate_image_file(output_path):
                            return output_path
                        else:
                            if os.path.exists(output_path):
                                try:
                                    os.remove(output_path)
                                except Exception:
                                    pass
                            last_error = ValueError("Tệp ảnh tải về bị hỏng hoặc định dạng không hợp lệ")
                    elif resp.status in (402, 429, 503):
                        last_error = RuntimeError(f"HTTP {resp.status} (Rate limited / Quota reached)")
                        # Nếu còn lượt retry, không thoát vội mà đợi backoff rồi thử lại
                        if attempt < max_retries - 1:
                            await asyncio.sleep(2.0 * (attempt + 1))
                            continue
                        break
                    else:
                        last_error = RuntimeError(f"HTTP {resp.status} từ máy chủ sinh ảnh")
            except Exception as e:
                last_error = e

            if attempt < max_retries - 1:
                await asyncio.sleep(1.0 * (attempt + 1))

        if allow_fallback:
            print(f"   ⚠️ Máy chủ AI thông báo ({last_error}). Đang tự động chuyển sang kho tư liệu độ nét cao...")
            wiki_res = await fetch_wikimedia_fallback(prompt, output_path, width=width, height=height, session=session)
            if wiki_res and os.path.exists(wiki_res):
                return wiki_res

            # Fallback canvas
            return generate_cinematic_canvas(prompt, output_path, width=width, height=height)

        raise RuntimeError(f"Failed to download valid image after retries: {last_error}")
    finally:
        if close_session:
            await session.close()

async def generate_images_parallel(
    scenes: list,
    target_dir: str,
    prefix: str = "scene",
    width: int = 1080,
    height: int = 1920,
    concurrency: int = 1,
    delay: float = 1.5
) -> list[str]:
    """
    Kích hoạt tải các ảnh cho các cảnh kịch bản chưa có ảnh với điều tiết nhịp độ (throttling),
    tránh chạm trần rate-limit IP của các dịch vụ AI miễn phí.
    Cập nhật trực tiếp đường dẫn ảnh vào scene['image'].
    """
    os.makedirs(target_dir, exist_ok=True)
    sem = asyncio.Semaphore(concurrency)

    async with aiohttp.ClientSession() as session:
        for idx, scene in enumerate(scenes):
            existing_img = scene.get("image")
            out_file = os.path.join(target_dir, f"{prefix}_{idx+1}.jpg")
            
            if existing_img and os.path.exists(existing_img) and validate_image_file(existing_img):
                continue

            prompt = scene.get("prompt")
            if not prompt:
                prompt = f"Cinematic dramatic 8k vertical shot representing: {scene.get('text', 'mysterious discovery')}"

            scene["image"] = out_file
            async with sem:
                await fetch_image(prompt, out_file, width=width, height=height, session=session)
                if delay > 0 and idx < len(scenes) - 1:
                    await asyncio.sleep(delay)

    return [s.get("image") for s in scenes if s.get("image")]
