import shutil
import subprocess
from pathlib import Path

SUPPORTED_EXTENSIONS = {".wav", ".mp3"}
MIN_SPEED = 0.1
MAX_SPEED = 100.0


def check_ffmpeg() -> None:
    """Verify ffmpeg is available, raise if not."""
    if shutil.which("ffmpeg") is None:
        raise RuntimeError(
            "ffmpeg not found. Install with: sudo apt install ffmpeg"
        )


def build_output_path(
    input_path: Path, speed_factor: float, out: str | None
) -> Path:
    """Build the output file path based on input path, speed factor, and --out flag."""
    auto_name = f"{speed_factor}x-{input_path.name}"

    if out is None:
        return input_path.parent / auto_name

    out_path = Path(out)
    if out_path.is_dir():
        return out_path / auto_name

    return out_path


def _build_atempo_filter(speed_factor: float) -> str:
    """Build an ffmpeg atempo filter chain for the given speed factor.

    atempo accepts values in [0.5, 100.0]. For factors below 0.5,
    chain multiple atempo=0.5 filters with a final remainder.
    """
    if speed_factor >= 0.5:
        return f"atempo={speed_factor}"

    filters = []
    remaining = speed_factor
    while remaining < 0.5:
        filters.append("atempo=0.5")
        remaining /= 0.5
    filters.append(f"atempo={remaining}")
    return ",".join(filters)


def change_speed(
    input_path: Path, speed_factor: float, output_path: Path
) -> Path:
    """Change audio speed with pitch preservation using ffmpeg atempo filter."""
    if not input_path.exists():
        raise FileNotFoundError(f"File '{input_path}' not found")

    ext = input_path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported format '{ext}'. Supported: .wav, .mp3"
        )

    if not (MIN_SPEED <= speed_factor <= MAX_SPEED):
        raise ValueError(
            f"Speed factor must be between {MIN_SPEED} and {MAX_SPEED}"
        )

    check_ffmpeg()

    out_ext = output_path.suffix.lower()
    if out_ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported output format '{out_ext}'. Supported: .wav, .mp3"
        )

    atempo_filter = _build_atempo_filter(speed_factor)

    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(input_path),
        "-filter:a", atempo_filter,
        str(output_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr}")

    return output_path
