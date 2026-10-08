"""Continuous utterance detection and a simple playback-reference echo filter.

The echo filter is not a full acoustic echo canceller. Headphones are preferable
for dependable barge-in; timing/device acoustics need validation on the real Mac.
"""
from collections import deque
import io
import threading
import time
import wave


class VoiceActivity:
    def __init__(self, threshold=900, silence_seconds=0.8, sample_rate=16000, chunk=1024):
        if threshold <= 0 or silence_seconds < 0.2:
            raise ValueError("O limite do microfone deve ser positivo; pausa mínima de 0,2 segundo.")
        self.threshold = threshold
        self.silence_frames = max(1, round(silence_seconds * sample_rate / chunk))
        self.max_frames = round(30 * sample_rate / chunk)
        self.pre_roll = deque(maxlen=6)
        self.frames = []
        self.onset = self.silence = self.voiced = 0
        self.active = False

    def reset(self):
        self.pre_roll.clear()
        self.frames = []
        self.onset = self.silence = self.voiced = 0
        self.active = False

    def feed(self, raw, amplitude):
        """Return (speech_started, completed_frames). Three frames reject spikes."""
        if not self.active:
            self.pre_roll.append(raw)
            self.onset = self.onset + 1 if amplitude > self.threshold else 0
            if self.onset < 3:
                return False, None
            self.active = True
            self.frames = list(self.pre_roll)
            self.pre_roll.clear()
            self.voiced = 3
            self.silence = 0
            return True, None
        self.frames.append(raw)
        if amplitude > self.threshold:
            self.voiced += 1
            self.silence = 0
        else:
            self.silence += 1
        if self.silence < self.silence_frames and len(self.frames) < self.max_frames:
            return False, None
        frames = self.frames if self.voiced >= 3 else None
        self.active = False
        self.frames = []
        self.onset = self.voiced = self.silence = 0
        return False, frames


def wav_bytes(frames):
    target = io.BytesIO()
    with wave.open(target, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(16000)
        wav.writeframes(b"".join(frames))
    return target.getvalue()


class EchoReference:
    """Remove a correlated, delayed component of our own rendered waveform."""
    def __init__(self):
        self.lock = threading.Lock()
        self.blocks = deque(maxlen=24)
        self.last_output = 0.0

    def push(self, samples):
        with self.lock:
            self.blocks.append(samples.copy())
            self.last_output = time.monotonic()

    def amplitude(self, raw):
        return self.filter(raw)[1]

    def filter(self, raw):
        import numpy as np
        samples = np.frombuffer(raw, dtype="<i2").astype(np.float32)
        original = float(np.sqrt(np.mean(samples * samples)))
        with self.lock:
            if not self.blocks or time.monotonic() - self.last_output > 0.4:
                return raw, original
            reference = np.concatenate(list(self.blocks))[-14000:] * 32768
        if len(reference) < len(samples):
            return raw, original
        samples_centered = samples - samples.mean()
        reference = reference - reference.mean()
        size = 1 << (len(reference) + len(samples) - 1).bit_length()
        convolution = np.fft.irfft(np.fft.rfft(reference, size) * np.fft.rfft(samples_centered[::-1], size), size)
        dots = convolution[len(samples) - 1:len(reference)]
        squares = np.concatenate(([0.0], np.cumsum(reference.astype(np.float64) ** 2)))
        energy = squares[len(samples):] - squares[:-len(samples)]
        norm = np.sqrt(np.maximum(energy * float(np.dot(samples_centered, samples_centered)), 1.0))
        correlations = np.abs(dots) / norm
        index = int(np.argmax(correlations))
        if correlations[index] < 0.6:
            return raw, original
        matched = reference[index:index + len(samples)]
        gain = float(dots[index] / max(energy[index], 1.0))
        residual = samples_centered - gain * matched
        return np.clip(residual, -32768, 32767).astype("<i2").tobytes(), float(np.sqrt(np.mean(residual * residual)))
