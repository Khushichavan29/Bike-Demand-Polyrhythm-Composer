from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

from .rhythm_engine import Composition, NoteEvent


TICKS_PER_BEAT = 480

LAYER_SOUND_DESIGN = {
    "demand_triplet": {"pan": 0.15, "gain": 0.28, "waveform": "triangle"},
    "time_grid": {"pan": 0.78, "gain": 0.2, "waveform": "square"},
    "weather_layer": {"pan": 0.55, "gain": 0.15, "waveform": "sine"},
    "bass_anchor": {"pan": 0.4, "gain": 0.3, "waveform": "saw"},
    "season_pad": {"pan": 0.62, "gain": 0.16, "waveform": "triangle"},
}


def export_midi(composition: Composition, output_path: str | Path) -> Path:
    output = Path(output_path)
    track = bytearray()

    microseconds_per_beat = int(60_000_000 / composition.tempo_bpm)
    track.extend(_var_len(0))
    track.extend(b"\xff\x51\x03")
    track.extend(struct.pack(">I", microseconds_per_beat)[1:])

    for channel, instrument in _channel_programs(composition.notes).items():
        track.extend(_var_len(0))
        track.extend(bytes([0xC0 | channel, instrument]))

    events: list[tuple[int, bytes]] = []
    for note in composition.notes:
        start_tick = int(note.start / composition.seconds_per_step * TICKS_PER_BEAT)
        end_tick = max(start_tick + 1, int(note.end / composition.seconds_per_step * TICKS_PER_BEAT))
        events.append((start_tick, bytes([0x90 | note.channel, note.pitch, note.velocity])))
        events.append((end_tick, bytes([0x80 | note.channel, note.pitch, 0])))

    last_tick = 0
    for tick, event in sorted(events, key=lambda item: (item[0], item[1][0] & 0xF0 == 0x80)):
        delta = tick - last_tick
        track.extend(_var_len(delta))
        track.extend(event)
        last_tick = tick

    track.extend(_var_len(0))
    track.extend(b"\xff\x2f\x00")

    header = struct.pack(">4sLHHH", b"MThd", 6, 0, 1, TICKS_PER_BEAT)
    track_chunk = struct.pack(">4sL", b"MTrk", len(track)) + track
    output.write_bytes(header + track_chunk)
    return output


def export_wav(composition: Composition, output_path: str | Path, sample_rate: int = 44_100) -> Path:
    output = Path(output_path)
    total_samples = int((composition.total_duration + 0.5) * sample_rate)
    left = [0.0] * total_samples
    right = [0.0] * total_samples

    for note in composition.notes:
        design = LAYER_SOUND_DESIGN.get(note.layer, {"pan": 0.5, "gain": 0.18, "waveform": "sine"})
        frequency = _midi_to_freq(note.pitch)
        start_index = int(note.start * sample_rate)
        end_index = min(total_samples, int(note.end * sample_rate))
        amplitude = (note.velocity / 127.0) * design["gain"]
        left_gain = math.sqrt(1.0 - design["pan"])
        right_gain = math.sqrt(design["pan"])

        for index in range(start_index, end_index):
            note_progress = (index - start_index) / max(1, end_index - start_index)
            envelope = _adsr(note_progress, note.layer)
            shimmer = 1.0 + 0.08 * math.sin(2 * math.pi * 5 * index / sample_rate)
            sample = _oscillator(design["waveform"], frequency, index, sample_rate)
            value = sample * amplitude * envelope * shimmer
            left[index] += value * left_gain
            right[index] += value * right_gain

    _apply_echo(left, right, sample_rate)
    peak = _peak(left, right)
    scale = 32767 / peak if peak else 1.0

    with wave.open(str(output), "wb") as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        frames = bytearray()
        for left_sample, right_sample in zip(left, right):
            frames.extend(struct.pack("<h", int(left_sample * scale)))
            frames.extend(struct.pack("<h", int(right_sample * scale)))
        wav_file.writeframes(frames)
    return output


def _channel_programs(notes: list[NoteEvent]) -> dict[int, int]:
    programs: dict[int, int] = {}
    for note in notes:
        programs.setdefault(note.channel, note.instrument)
    return programs


def _var_len(value: int) -> bytes:
    buffer = value & 0x7F
    chunks = bytearray([buffer])
    while value > 0x7F:
        value >>= 7
        buffer = (value & 0x7F) | 0x80
        chunks.insert(0, buffer)
    return bytes(chunks)


def _midi_to_freq(pitch: int) -> float:
    return 440.0 * (2 ** ((pitch - 69) / 12))


def _oscillator(waveform: str, frequency: float, index: int, sample_rate: int) -> float:
    phase = 2 * math.pi * frequency * index / sample_rate
    sine = math.sin(phase)
    if waveform == "square":
        return 1.0 if sine >= 0 else -1.0
    if waveform == "triangle":
        return (2 / math.pi) * math.asin(sine)
    if waveform == "saw":
        fraction = (frequency * index / sample_rate) % 1.0
        return 2.0 * fraction - 1.0
    return sine


def _adsr(progress: float, layer: str) -> float:
    if progress < 0.08:
        return progress / 0.08
    if progress < 0.25:
        return 1.0 - (progress - 0.08) * 1.1
    sustain = 0.42 if layer == "season_pad" else 0.28
    if progress < 0.8:
        return sustain
    return sustain * max(0.0, 1.0 - (progress - 0.8) / 0.2)


def _apply_echo(left: list[float], right: list[float], sample_rate: int) -> None:
    delay = int(sample_rate * 0.18)
    feedback = 0.22
    for index in range(delay, len(left)):
        left[index] += left[index - delay] * feedback
        right[index] += right[index - delay] * feedback * 0.92


def _peak(left: list[float], right: list[float]) -> float:
    return max(
        max((abs(sample) for sample in left), default=1.0),
        max((abs(sample) for sample in right), default=1.0),
    )
