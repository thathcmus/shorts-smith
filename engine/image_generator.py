"""
Module sinh ảnh AI đám mây miễn phí chất lượng cao (Free AI Cloud Image Generator).
Kết nối trực tiếp tới API Pollinations.ai FLUX (100% miễn phí, không cần token/key),
tải song song 6 cảnh bằng asyncio, xác thực ảnh hợp lệ bằng Pillow và tự động retry khi gặp lỗi mạng.
"""
import asyncio
import os
import random
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

async def fetch_image(
    prompt: str,
    output_path: str,
    width: int = 1080,
    height: int = 1920,
    max_retries: int = 3,
    session: aiohttp.ClientSession = None
) -> str:
    """
    Tải 1 ảnh từ Pollinations.ai FLUX với kích thước 1080x1920 (9:16 dọc).
    Xác thực ảnh hợp lệ và thử lại nếu gặp sự cố kết nối.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # URL Encode prompt để an toàn với ký tự đặc biệt
    clean_prompt = prompt.strip()
    encoded_prompt = urllib.parse.quote(clean_prompt)
    seed = random.randint(1000, 999999)
    url = f"{POLLINATIONS_BASE_URL}/{encoded_prompt}?width={width}&height={height}&model=flux&nologo=true&seed={seed}"

    close_session = False
    if session is None:
        session = aiohttp.ClientSession()
        close_session = True

    try:
        last_error = None
        for attempt in range(max_retries):
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=45)) as resp:
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
                    else:
                        last_error = RuntimeError(f"HTTP {resp.status} từ máy chủ sinh ảnh")
            except Exception as e:
                last_error = e

            if attempt < max_retries - 1:
                await asyncio.sleep(1.5 * (attempt + 1))

        raise RuntimeError(f"Failed to download valid image after retries: {last_error}")
    finally:
        if close_session:
            await session.close()

async def generate_images_parallel(
    scenes: list,
    target_dir: str,
    prefix: str = "scene",
    width: int = 1080,
    height: int = 1920
) -> list[str]:
    """
    Kích hoạt tải song song tất cả các ảnh cho các cảnh kịch bản chưa có ảnh bằng asyncio.gather.
    Cập nhật trực tiếp đường dẫn ảnh vào scene['image'].
    """
    os.makedirs(target_dir, exist_ok=True)
    async with aiohttp.ClientSession() as session:
        tasks = []
        for idx, scene in enumerate(scenes):
            existing_img = scene.get("image")
            out_file = os.path.join(target_dir, f"{prefix}_{idx+1}.jpg")
            
            # Nếu đã có file ảnh tồn tại và hợp lệ thì bỏ qua không cần tải lại
            if existing_img and os.path.exists(existing_img) and validate_image_file(existing_img):
                continue

            prompt = scene.get("prompt")
            if not prompt:
                # Fallback prompt nếu thiếu
                prompt = f"Cinematic dramatic 8k vertical shot representing: {scene.get('text', 'mysterious discovery')}"

            # Gán đường dẫn trước
            scene["image"] = out_file
            tasks.append(fetch_image(prompt, out_file, width=width, height=height, session=session))

        if tasks:
            await asyncio.gather(*tasks)

    return [s.get("image") for s in scenes if s.get("image")]
