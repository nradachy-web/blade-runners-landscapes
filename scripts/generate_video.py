#!/usr/bin/env python3
"""Generate the Blade Runners hero video via Veo 3.

Tries Veo 3 quality first, falls back to fast/lite per memory's free-tier note.
"""
import os, sys, time
from pathlib import Path

try:
    from google import genai
    from google.genai import types
except ImportError:
    os.system(f"{sys.executable} -m pip install -q google-genai")
    from google import genai
    from google.genai import types

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("ERROR: GEMINI_API_KEY not set", file=sys.stderr); sys.exit(1)

OUT = Path(__file__).parent.parent / "assets" / "videos"
OUT.mkdir(parents=True, exist_ok=True)

client = genai.Client(api_key=API_KEY)

PROMPT = (
    "Cinematic 8-second aerial drone shot sweeping low over a luxury Michigan backyard at golden hour. "
    "Camera glides forward over freshly cut emerald-green lawn with crisp diagonal stripes, "
    "passes a custom paver patio with a built-in stone fire pit emitting warm flames, "
    "rises to reveal a beautifully landscaped backyard with blooming hydrangeas, manicured boxwoods, mature shade trees, "
    "and a brick colonial home softly lit by sunset. Warm golden lighting, gentle wind in the trees, "
    "professional cinematography, photorealistic, 4K. NO people, NO cars, NO text."
)

MODELS = ["veo-3.0-generate-001", "veo-3.1-fast-generate-preview", "veo-3.1-generate-preview"]

for model in MODELS:
    try:
        print(f"Trying {model}...", flush=True)
        op = client.models.generate_videos(
            model=model,
            prompt=PROMPT,
            config=types.GenerateVideosConfig(
                aspect_ratio="16:9",
                negative_prompt="text, watermark, logo, people, cars, blurry",
            ),
        )
        # Poll
        start = time.time()
        while not op.done:
            if time.time() - start > 600:
                print("  timeout", flush=True); break
            time.sleep(10)
            op = client.operations.get(op)
            print(f"  ...polling ({int(time.time()-start)}s)", flush=True)
        if op.done and op.response and op.response.generated_videos:
            video = op.response.generated_videos[0].video
            out = OUT / "hero.mp4"
            client.files.download(file=video)
            video.save(str(out))
            print(f"OK saved {out}", flush=True)
            sys.exit(0)
    except Exception as e:
        print(f"  {model} failed: {str(e)[:200]}", flush=True)
        continue

print("All Veo models failed — site will use static hero image", flush=True)
sys.exit(1)
