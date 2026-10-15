"""Build a labelled pitch around an uncut, real-time desktop recording.

Optional media tooling: Pillow, FFmpeg/ffprobe, Windows System.Speech.
The desktop footage is never accelerated or spliced. Speech is synthetic.
"""
from pathlib import Path
import json
import re
import shutil
import subprocess
import textwrap
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "runs" / "pitch"
OUT.mkdir(parents=True, exist_ok=True)
DIST = ROOT / "dist"
DIST.mkdir(exist_ok=True)
FFMPEG = shutil.which("ffmpeg")
FFPROBE = shutil.which("ffprobe")
if not FFMPEG or not FFPROBE:
    raise SystemExit("Install FFmpeg and ffprobe before building the optional pitch.")
SOURCE = ROOT / "runs/demo/office-twin-desktop-20261015-171812.mp4"
BG, PANEL, INK, MUTED, TEAL = "#0B1220", "#152236", "#F3F7FE", "#B7C7DB", "#58DEC5"
FONT_DIR = Path("C:/Windows/Fonts")


def run(args):
    subprocess.run(args, check=True, cwd=OUT,
                   creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))


def duration(path):
    return float(subprocess.check_output([FFPROBE, "-v", "error", "-show_entries", "format=duration",
                                         "-of", "default=nw=1:nk=1", str(path)], text=True))


def font(size, bold=False):
    return ImageFont.truetype(str(FONT_DIR / ("segoeuib.ttf" if bold else "segoeui.ttf")), size)


def card(path, kind, size=(1920, 1200)):
    w, h = size
    scale = w / 1920
    image = Image.new("RGB", size, BG)
    d = ImageDraw.Draw(image)
    def t(x, y, value, fs=40, color=INK, bold=False):
        d.text((x*scale, y*scale), value, font=font(round(fs*scale), bold), fill=color)
    def box(x, y, x2, y2, color=PANEL):
        d.rounded_rectangle(tuple(round(v*scale) for v in (x,y,x2,y2)), radius=round(22*scale), fill=color)
    t(100, 80, "NTU x ST ENGINEERING HACKATHON  /  2026", 28, TEAL, True)
    t(100, 185, "Office Twin", 116, bold=True)
    t(105, 335, "Office activity. Checked outputs. Inspectable evidence.", 43, MUTED)
    for x, name, sub in [(100,"CHROME","Review supplier quotes"),(680,"GOOGLE SHEETS","Calculate cost + eligibility"),(1260,"NOTEPAD","Save the recommendation")]:
        box(x, 475, x+540, 675)
        t(x+35, 510, name, 30, TEAL, True)
        t(x+35, 580, sub, 30)
    if kind == "closing":
        t(105, 750, "SEPARATE ALTERNATE RUN", 28, TEAL, True)
        t(105, 805, "Changed price → Crest Industrial selected at SGD 525", 45, bold=True)
        t(105, 890, "6 formulas independently checked • 11/11 steps completed", 34, MUTED)
        t(105, 1035, "github.com/ajayasai/office-twin-ntu-st-2026", 37)
    elif kind == "cover":
        t(105, 765, "11 STEPS     /     3 LATEST RUNS COMPLETED     /     41 TESTS", 34, TEAL, True)
        t(105, 860, "Scenario-driven Windows desktop workflow", 43, bold=True)
        t(105, 960, "Synthetic business data • Contextual timing • Saved-content checks", 30, MUTED)
    else:
        t(105, 775, "RECORDED DESKTOP EXECUTION  •  1x PLAYBACK", 37, TEAL, True)
        t(105, 865, "Continuous original run, with introductory and result cards", 35, MUTED)
        t(105, 1025, "Synthetic narration added • No human-similarity claim", 31, MUTED)
    image.save(path)


card(OUT / "intro.png", "opening")
card(OUT / "outro.png", "closing")
media = ROOT / "docs" / "media"
media.mkdir(exist_ok=True)
card(media / "office-twin-cover.png", "cover", (1500, 1000))
source_duration = duration(SOURCE)
end = 8 + source_duration + 10
script = (ROOT / "docs" / "PITCH.md").read_text(encoding="utf-8")
spoken = re.findall(r"\*\*Narration:\*\*\s*\n\n([^\n]+)", script)
assert len(spoken) == 8, "Expected eight narration sections in PITCH.md"
starts = [0, 8, 32, 58, 86, 114, 150, 8 + source_duration]
segments = [{"start": start, "end": (starts+[end])[i+1], "text": text,
             "file": f"voice-{i}.wav"} for i,(start,text) in enumerate(zip(starts, spoken))]
(OUT / "narration.json").write_text(json.dumps(segments, ensure_ascii=False), encoding="utf-8")
ps = '''Add-Type -AssemblyName System.Speech
$pitchNarrator = New-Object System.Speech.Synthesis.SpeechSynthesizer
$pitchNarrator.SelectVoice('Microsoft Zira Desktop')
$pitchNarrator.Rate = 0
$pitchSegments = Get-Content -LiteralPath 'narration.json' -Raw -Encoding UTF8 | ConvertFrom-Json
foreach ($pitchSegment in $pitchSegments) {
    $pitchNarrator.SetOutputToWaveFile((Join-Path (Get-Location) $pitchSegment.file))
    $pitchNarrator.Speak($pitchSegment.text)
}
$pitchNarrator.Dispose()
'''
(OUT / "narrate.ps1").write_text(ps, encoding="utf-8-sig")
run(["powershell", "-NoProfile", "-File", str(OUT / "narrate.ps1")])

# Normalize speech to its allotted slot only when necessary. Video speed is unchanged.
audio_inputs, audio_filters, labels = [], [], []
for i, segment in enumerate(segments):
    wav = OUT / segment["file"]
    measured = duration(wav)
    slot = segment["end"] - segment["start"]
    tempo = max(1.0, measured / (slot - .2))
    if tempo > 1.35:
        raise RuntimeError(f"Narration {i} too long for natural pacing: shorten the script")
    segment.update({"speech_duration": measured, "audio_tempo": tempo})
    audio_inputs += ["-i", str(wav)]
    audio_filters.append(f"[{i}:a]atempo={tempo:.6f},apad,atrim=0:{slot:.6f},asetpts=PTS-STARTPTS[a{i}]")
    labels.append(f"[a{i}]")
audio_filters.append(''.join(labels)+f"concat=n={len(segments)}:v=0:a=1[a]")
run([FFMPEG,"-y","-hide_banner","-loglevel","error",*audio_inputs,"-filter_complex",
     ';'.join(audio_filters),"-map","[a]","-c:a","pcm_s16le",str(OUT / "narration.wav")])

captions = [
    (8,32,"DEFAULT SCENARIO  |  Five sensor kits. Seven-day deadline."),
    (32,58,"CONTEXTUAL TIMING  |  Seeded engineering defaults; not human-calibrated."),
    (58,86,"VISIBLE DESKTOP INPUT  |  Dedicated Quotes worksheet. Escape stops input."),
    (86,114,"SAVED-CONTENT CHECKS  |  Reload the sheet and check calculated results."),
    (114,150,"DEFAULT RESULT  |  Atlas: SGD 600. Latest 3 runs: 11/11 steps. 41 tests pass."),
    (150,8+source_duration,"EVIDENCE LIMITS  |  No human baseline or independent Sysmon trace collected."),
]
video_filter = ["[0:v]fps=15,format=yuv420p,setsar=1[i]",
                "[1:v]fps=15,format=yuv420p,setsar=1[r]",
                "[2:v]fps=15,format=yuv420p,setsar=1[o]",
                "[i][r][o]concat=n=3:v=1:a=0[v0]"]
last="v0"
for i,(start,stop,caption) in enumerate(captions):
    (OUT/f"caption-{i}.txt").write_text(caption,encoding="utf-8")
    nxt=f"v{i+1}"
    video_filter.append(f"[{last}]drawbox=x=0:y=ih-50:w=iw:h=50:color=0x101b2d:t=fill:enable='between(t,{start},{stop})',drawtext=textfile=caption-{i}.txt:fontfile='C\\:/Windows/Fonts/segoeui.ttf':fontcolor=white:fontsize=24:x=24:y=h-39:enable='between(t,{start},{stop})'[{nxt}]")
    last=nxt
output=DIST/"office-twin-submission.mp4"
run([FFMPEG,"-y","-hide_banner","-loglevel","warning",
     "-loop","1","-framerate","15","-t","8","-i",str(OUT/"intro.png"),
     "-i",str(SOURCE),"-loop","1","-framerate","15","-t","10","-i",str(OUT/"outro.png"),
     "-i",str(OUT/"narration.wav"),"-filter_complex",';'.join(video_filter),"-map",f"[{last}]","-map","3:a",
     "-t",str(end),"-c:v","libx264","-crf","22","-preset","fast","-pix_fmt","yuv420p",
     "-c:a","aac","-b:a","160k","-movflags","+faststart",str(output)])
(OUT/"build.json").write_text(json.dumps({"source_video":str(SOURCE),"source_seconds":source_duration,
    "source_playback":"unchanged 1x continuous", "opening_seconds":8,"closing_seconds":10,
    "speech":"Microsoft Zira Desktop, synthetic narration", "segments":segments,
    "output":str(output),"output_seconds":duration(output)},indent=2),encoding="utf-8")
print(output)
