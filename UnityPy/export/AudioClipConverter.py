from __future__ import annotations

import wave
from io import BytesIO
from typing import TYPE_CHECKING, Dict

import fmod_toolkit

from ..enums import AudioCompressionFormat
from ..helpers.ResourceReader import get_resource_data

if TYPE_CHECKING:
    from ..classes import AudioClip


def extract_audioclip_samples(audio: AudioClip, convert_pcm_float: bool = True) -> Dict[str, bytes]:
    """extracts all the samples from an AudioClip
    :param audio: AudioClip
    :type audio: AudioClip
    :return: {filename : sample(bytes)}
    :rtype: dict
    """
    audio_data: bytes
    if audio.m_AudioData:
        audio_data = bytes(audio.m_AudioData)
    elif audio.m_Resource:
        assert audio.object_reader is not None, "AudioClip uses an external resource but object_reader is not set"
        resource = audio.m_Resource
        audio_data = get_resource_data(
            resource.m_Source,
            audio.object_reader.assets_file,
            resource.m_Offset,
            resource.m_Size,
        )
    else:
        raise ValueError("AudioClip with neither m_AudioData nor m_Resource")

    magic = memoryview(audio_data)[:8]
    if magic[:4] == b"OggS":
        return {f"{audio.m_Name}.ogg": audio_data}
    elif magic[:4] == b"RIFF":
        return {f"{audio.m_Name}.wav": audio_data}
    elif magic[4:8] == b"ftyp":
        return {f"{audio.m_Name}.m4a": audio_data}

    return fmod_toolkit.raw_to_wav(
        audio_data,
        audio.m_Name,
        audio.m_Channels or 2,
        audio.m_Frequency or 44100,
        convert_pcm_float=convert_pcm_float,
    )


def set_audioclip_samples(audio: AudioClip, samples: Dict[str, bytes]):
    """
    使用提供的样本数据替换AudioClip的音频数据。
    目前仅支持 PCM WAV 格式。

    :param audio: 要修改的AudioClip对象
    :type audio: AudioClip
    :param samples: 包含WAV文件名和数据的字典
    :type samples: Dict[str, bytes]
    """
    if not samples:
        raise ValueError("没有提供任何样本数据")

    # 我们只处理字典中的第一个样本
    filename, sample_data = next(iter(samples.items()))

    if not filename.lower().endswith(".wav"):
        raise NotImplementedError("目前只支持 .wav 格式的音频替换")

    try:
        # 使用 BytesIO 从内存中的字节数据读取 WAV 文件
        with wave.open(BytesIO(sample_data), "rb") as wav_file:
            channels = wav_file.getnchannels()
            frequency = wav_file.getframerate()
            sampwidth = wav_file.getsampwidth()
            nframes = wav_file.getnframes()
            audio_data = wav_file.readframes(nframes)
    except wave.Error as e:
        raise e

    # 更新 AudioClip 的元数据
    audio.m_Channels = channels
    audio.m_Frequency = frequency
    audio.m_BitsPerSample = sampwidth * 8
    audio.m_Length = nframes / float(frequency)
    audio.m_CompressionFormat = AudioCompressionFormat.PCM

    # 清除对外部资源文件的引用（如果存在）
    # 这确保了音频数据会内联存储在 m_AudioData 中
    if audio.m_Resource:
        audio.m_Resource.m_Source = None
        audio.m_Resource.m_Offset = 0
        audio.m_Resource.m_Size = 0

    # 设置新的音频数据
    audio.m_AudioData = list(audio_data)
