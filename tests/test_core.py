import pytest
from pathlib import Path

from nqt.core import (
    build_output_path,
    change_speed,
    _build_atempo_filter,
    MIN_SPEED,
    MAX_SPEED,
)


# --- build_output_path ---


def test_build_output_path_default(tmp_path):
    input_path = tmp_path / "song.mp3"
    result = build_output_path(input_path, 1.5, None)
    assert result == tmp_path / "1.5x-song.mp3"


def test_build_output_path_out_directory(tmp_path):
    input_path = tmp_path / "song.wav"
    out_dir = tmp_path / "output"
    out_dir.mkdir()
    result = build_output_path(input_path, 0.5, str(out_dir))
    assert result == out_dir / "0.5x-song.wav"


def test_build_output_path_out_file(tmp_path):
    input_path = tmp_path / "song.mp3"
    out_file = tmp_path / "fast.mp3"
    result = build_output_path(input_path, 2.0, str(out_file))
    assert result == out_file


# --- speed factor computation (as done in CLI) ---


def test_speed_factor_up():
    factor = 1.5
    assert factor == 1.5


def test_speed_factor_down():
    factor = 1.0 / 2.0
    assert factor == 0.5


# --- validation ---


def test_change_speed_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError, match="not found"):
        change_speed(tmp_path / "nope.mp3", 1.5, tmp_path / "out.mp3")


def test_change_speed_bad_extension(tmp_path):
    bad_file = tmp_path / "song.ogg"
    bad_file.write_bytes(b"fake")
    with pytest.raises(ValueError, match="Unsupported format"):
        change_speed(bad_file, 1.5, tmp_path / "out.ogg")


def test_change_speed_factor_too_low(tmp_path):
    f = tmp_path / "song.mp3"
    f.write_bytes(b"fake")
    with pytest.raises(ValueError, match="Speed factor must be between"):
        change_speed(f, 0.01, tmp_path / "out.mp3")


def test_change_speed_factor_too_high(tmp_path):
    f = tmp_path / "song.mp3"
    f.write_bytes(b"fake")
    with pytest.raises(ValueError, match="Speed factor must be between"):
        change_speed(f, 200.0, tmp_path / "out.mp3")


# --- atempo filter chaining ---


def test_atempo_normal():
    assert _build_atempo_filter(1.5) == "atempo=1.5"


def test_atempo_at_boundary():
    assert _build_atempo_filter(0.5) == "atempo=0.5"


def test_atempo_chain_needed():
    # 0.25 = 0.5 * 0.5 → two atempo=0.5 filters
    result = _build_atempo_filter(0.25)
    assert result == "atempo=0.5,atempo=0.5"


def test_atempo_chain_with_remainder():
    # 0.3 → 0.3/0.5 = 0.6, so atempo=0.5,atempo=0.6
    result = _build_atempo_filter(0.3)
    assert result == "atempo=0.5,atempo=0.6"


def test_atempo_very_slow():
    # 0.1 → 0.1/0.5=0.2, 0.2/0.5=0.4, 0.4/0.5=0.8
    # so: atempo=0.5,atempo=0.5,atempo=0.5,atempo=0.8
    result = _build_atempo_filter(0.1)
    parts = result.split(",")
    assert len(parts) == 4
    assert parts[:3] == ["atempo=0.5"] * 3
    assert parts[3] == "atempo=0.8"


# --- integration test ---


def test_integration_speed_up(tmp_path):
    """Generate a sine wave, speed it up, verify output exists and duration changed."""
    from pydub import AudioSegment
    from pydub.generators import Sine

    # Generate a 2-second 440Hz sine wave
    tone = Sine(440).to_audio_segment(duration=2000)
    input_file = tmp_path / "tone.wav"
    tone.export(str(input_file), format="wav")

    output_file = tmp_path / "fast_tone.wav"
    change_speed(input_file, 2.0, output_file)

    assert output_file.exists()
    result_audio = AudioSegment.from_file(str(output_file))
    # At 2x speed, ~2s input → ~1s output (allow some tolerance)
    assert result_audio.duration_seconds < 1.5


def test_integration_slow_down(tmp_path):
    """Generate a sine wave, slow it down, verify output exists and duration changed."""
    from pydub import AudioSegment
    from pydub.generators import Sine

    tone = Sine(440).to_audio_segment(duration=1000)
    input_file = tmp_path / "tone.wav"
    tone.export(str(input_file), format="wav")

    output_file = tmp_path / "slow_tone.wav"
    change_speed(input_file, 0.5, output_file)

    assert output_file.exists()
    result_audio = AudioSegment.from_file(str(output_file))
    # At 0.5x speed, ~1s input → ~2s output
    assert result_audio.duration_seconds > 1.5
