"""https://github.com/wiseman/py-webrtcvad/blob/master/example.py"""

import collections
import contextlib
import sys
import wave
import glob

import pandas as pd

import webrtcvad


def read_wave(path):
    """Reads a .wav file.
    Takes the path, and returns (PCM audio data, sample rate).
    """
    with contextlib.closing(wave.open(path, 'rb')) as wf:
        num_channels = wf.getnchannels()
        assert num_channels == 1
        sample_width = wf.getsampwidth()
        assert sample_width == 2
        sample_rate = wf.getframerate()
        assert sample_rate in (8000, 16000, 32000, 48000)
        pcm_data = wf.readframes(wf.getnframes())
        return pcm_data, sample_rate


def write_wave(path, audio, sample_rate):
    """Writes a .wav file.
    Takes path, PCM audio data, and sample rate.
    """
    with contextlib.closing(wave.open(path, 'wb')) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio)


class Frame(object):
    """Represents a "frame" of audio data."""
    def __init__(self, bytes, timestamp, duration):
        self.bytes = bytes
        self.timestamp = timestamp
        self.duration = duration


def frame_generator(frame_duration_ms, audio, sample_rate):
    """Generates audio frames from PCM audio data.
    Takes the desired frame duration in milliseconds, the PCM data, and
    the sample rate.
    Yields Frames of the requested duration.
    """
    n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
    offset = 0
    timestamp = 0.0
    duration = (float(n) / sample_rate) / 2.0
    while offset + n < len(audio):
        yield Frame(audio[offset:offset + n], timestamp, duration)
        timestamp += duration
        offset += n


def vad_collector(sample_rate, frame_duration_ms,
                  padding_duration_ms, vad, frames):
    """Filters out non-voiced audio frames.
    Given a webrtcvad.Vad and a source of audio frames, yields only
    the voiced audio.
    Uses a padded, sliding window algorithm over the audio frames.
    When more than 90% of the frames in the window are voiced (as
    reported by the VAD), the collector triggers and begins yielding
    audio frames. Then the collector waits until 90% of the frames in
    the window are unvoiced to detrigger.
    The window is padded at the front and back to provide a small
    amount of silence or the beginnings/endings of speech around the
    voiced frames.
    Arguments:
    sample_rate - The audio sample rate, in Hz.
    frame_duration_ms - The frame duration in milliseconds.
    padding_duration_ms - The amount to pad the window, in milliseconds.
    vad - An instance of webrtcvad.Vad.
    frames - a source of audio frames (sequence or generator).
    Returns: A generator that yields PCM audio data.
    """
    num_padding_frames = int(padding_duration_ms / frame_duration_ms)
    # We use a deque for our sliding window/ring buffer.
    ring_buffer = collections.deque(maxlen=num_padding_frames)
    # We have two states: TRIGGERED and NOTTRIGGERED. We start in the
    # NOTTRIGGERED state.
    triggered = False

    voiced_frames = []
    for i, frame in enumerate(frames):
        is_speech = vad.is_speech(frame.bytes, sample_rate)
        
        ring_buffer.append((frame, is_speech))
        num_voiced = len([f for f, speech in ring_buffer if speech])
        # If we're NOTTRIGGERED and more than 90% of the frames in
        # the ring buffer are voiced frames, then enter the
        # TRIGGERED state.
        if num_voiced > 0.9 * ring_buffer.maxlen:
            triggered = True
            sys.stdout.write('+(%s)' % (ring_buffer[0][0].timestamp,))
            # We want to yield all the audio we see from now until
            # we are NOTTRIGGERED, but we have to start with the
            # audio that's already in the ring buffer.
            num_empty_frames = i + 1
            for f, s in ring_buffer:
                num_empty_frames -= 1
            return num_empty_frames * frame_duration_ms
    return -1


def get_silence_duration_ms(path_to_wav, aggressiveness=0):
    audio, sample_rate = read_wave(path_to_wav)
    vad = webrtcvad.Vad(int(aggressiveness))
    frames = frame_generator(30, audio, sample_rate)
    frames = list(frames)
    silence_duration_ms = vad_collector(sample_rate, 30, 300, vad, frames)
    return silence_duration_ms


if __name__ == '__main__':
    wav_files = glob.glob("resampled_wavs/*.wav")
    df = pd.DataFrame(wav_files)
    df[1] = df[0].apply(get_silence_duration_ms)
    df.to_csv("silence_duration_ms.csv")
    
    

