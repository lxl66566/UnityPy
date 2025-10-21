from ...enums import AUDIO_TYPE_EXTEMSION
from ..generated import AudioClip


def _AudioClip_extension(self: AudioClip) -> str:
    return AUDIO_TYPE_EXTEMSION.get(self.m_CompressionFormat, ".audioclip")


def _AudioClip_samples(self: AudioClip) -> dict:
    from ...export import AudioClipConverter

    return AudioClipConverter.extract_audioclip_samples(self)


def _AudioClip_set_samples(self: AudioClip, samples: dict):
    """samples 属性的 setter"""
    from ...export import AudioClipConverter

    AudioClipConverter.set_audioclip_samples(self, samples)


AudioClip.extension = property(_AudioClip_extension)
AudioClip.samples = property(_AudioClip_samples, _AudioClip_set_samples)

__all__ = ("AudioClip",)
