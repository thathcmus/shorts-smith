import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from engine.tts import synthesize_speech_with_words

@pytest.mark.asyncio
async def test_voice_identity_remains_strictly_consistent_on_retry(tmp_path):
    out_audio = str(tmp_path / "scene_voice.mp3")
    communicator_instances = []

    class MockCommunicate:
        def __init__(self, text, voice="en-US-EmmaMultilingualNeural", **kwargs):
            self._voice = voice
            communicator_instances.append(voice)
            self.stream = AsyncMock(side_effect=RuntimeError("Simulated TTS Stream Failure"))

    with patch("edge_tts.Communicate", side_effect=MockCommunicate):
        with patch("asyncio.sleep", new_callable=AsyncMock):
            try:
                await synthesize_speech_with_words("Chào bạn", out_audio, voice="vi-VN-NamMinhNeural", max_retries=4)
            except Exception:
                pass
        
        # Must have attempted multiple times
        assert len(communicator_instances) >= 3
        # ALL initiated instances must strictly use vi-VN-NamMinhNeural, NEVER switching to another voice
        for v in communicator_instances:
            assert v == "vi-VN-NamMinhNeural"
