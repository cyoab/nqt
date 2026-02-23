# 🥁 nqt — "Not Quite my Tempo"

> *"Were you rushing or were you dragging?"*
> — Terence Fletcher, **Whiplash** (2014)

Your audio file not quite at the right tempo? **nqt** fixes that.

A dead-simple CLI tool that speeds up or slows down audio files — **with pitch preservation** — so your tracks don't sound like chipmunks or demons. Just pure tempo adjustment, the way Fletcher would demand it. 🎬🎶

`mp3` · `wav` · powered by `ffmpeg`

---

## ✨ Features

- 🔺 **Speed up** — crank that tempo with `--up`
- 🔻 **Slow down** — take it easy with `--down`
- 🎵 **Pitch preserved** — no squeaky voices, no deep rumbles
- 📁 **Flexible output** — custom path, directory, or auto-named
- ⚡ **Fast** — thin wrapper around ffmpeg's `atempo` filter

---

## 📦 Installation

### Prerequisites

You need **ffmpeg** installed on your system:

```bash
# Ubuntu / Debian / WSL
sudo apt install ffmpeg
```

### Install with uv

```bash
# Install from the repo
uv tool install git+https://github.com/cyoab/nqt.git
```

That's it — `nqt` is now available globally! 🎉

### Development setup

```bash
git clone https://github.com/cyoab/nqt.git
cd nqt
uv sync
uv run nqt --help
```

---

## 🚀 Usage

```
nqt <file> (--up <factor> | --down <factor>) [--out <path>]
```

### Examples

```bash
# 🔺 Speed up a song by 1.5x
nqt song.mp3 --up 1.5              # → 1.5x-song.mp3

# 🔻 Slow down to half speed
nqt song.wav --down 2              # → 0.5x-song.wav

# 📁 Output to a specific directory
nqt song.mp3 --up 1.1 --out ./out/ # → ./out/1.1x-song.mp3

# 📝 Output with a custom filename
nqt song.mp3 --up 2 --out fast.mp3 # → fast.mp3
```

### Speed factors

| Flag | Value | Effective speed |
|------|-------|----------------|
| `--up 1.5` | 1.5x | 50% faster |
| `--up 2` | 2.0x | Double speed |
| `--down 2` | 0.5x | Half speed |
| `--down 4` | 0.25x | Quarter speed |

---

## 🛠️ How it works

Under the hood, `nqt` uses ffmpeg's [`atempo`](https://ffmpeg.org/ffmpeg-filters.html#atempo) audio filter for pitch-preserving time stretching. For extreme slow-downs (below 0.5x), it automatically chains multiple `atempo` filters together — because ffmpeg's single filter range is `0.5–100.0`.

No intermediate processing, no bloated dependencies. Just ffmpeg doing what it does best. 💪

---

## 📄 License

MIT
