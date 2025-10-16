import wave
from io import BytesIO

from ...enums import AUDIO_TYPE_EXTEMSION, AudioCompressionFormat
from ..generated import AudioClip


def _AudioClip_extension(self: AudioClip) -> str:
    return AUDIO_TYPE_EXTEMSION.get(self.m_CompressionFormat, ".audioclip")


def _AudioClip_samples(self: AudioClip) -> dict:
    from ...export import AudioClipConverter

    return AudioClipConverter.extract_audioclip_samples(self)


def _set_AudioClip_samples(self: AudioClip, samples: dict):
    wav_data = next((data for name, data in samples.items() if name.lower().endswith(".wav")), None)

    if not wav_data:
        raise NotImplementedError("Currently, only writing .wav files is supported.")

    with BytesIO(wav_data) as f:
        with wave.open(f, "rb") as wav_file:
            frames = wav_file.readframes(wav_file.getnframes())

            self.m_Channels = wav_file.getnchannels()
            self.m_Frequency = wav_file.getframerate()
            self.m_BitsPerSample = wav_file.getsampwidth() * 8

            self.m_AudioData = list(frames)

            self.m_Length = wav_file.getnframes() / wav_file.getframerate()
            self.m_CompressionFormat = AudioCompressionFormat.PCM

            if self.m_Resource:
                self.m_Resource.m_Source = ""
                self.m_Resource.m_Offset = 0
                self.m_Resource.m_Size = 0


AudioClip.extension = property(_AudioClip_extension)
AudioClip.samples = property(_AudioClip_samples, _set_AudioClip_samples)

__all__ = ("AudioClip",)
