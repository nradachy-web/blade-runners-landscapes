#!/usr/bin/env python3
"""Batch generate Blade Runners site imagery via Gemini.

Tries Imagen 4 first (paid). Falls back to gemini-3.1-flash-image-preview (free).
Reads GEMINI_API_KEY from env. NEVER hardcode the key.
"""
import os, sys, time, base64
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Installing google-genai...", flush=True)
    os.system(f"{sys.executable} -m pip install -q google-genai pillow")
    from google import genai
    from google.genai import types

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("ERROR: GEMINI_API_KEY not set", file=sys.stderr); sys.exit(1)

OUT = Path(__file__).parent.parent / "assets" / "images"
OUT.mkdir(parents=True, exist_ok=True)

client = genai.Client(api_key=API_KEY)

PROMPTS = {
    "home-hero": (
        "Cinematic ultra-wide aerial shot of a luxury Michigan estate property in late spring at golden hour. "
        "Perfectly manicured emerald-green lawn with crisp diagonal mowing stripes, freshly edged garden beds with dark hardwood mulch, "
        "vibrant blooming hydrangeas and ornamental grasses, a stone paver patio with built-in fire feature in the foreground, "
        "mature shade trees, brick colonial home in soft focus background. "
        "Soft warm sunlight casting long shadows, lens flare, hyper-realistic, 8k, professional landscape photography, "
        "Sony A7R IV, 24mm, shallow depth of field. NO people, NO cars, NO text."
    ),
    "svc-lawn-maintenance": (
        "Professional landscape crew member in clean uniform operating a commercial zero-turn mower across a vast suburban Michigan front lawn. "
        "Razor-sharp diagonal stripe pattern in the lawn, crisp edge along the sidewalk, summer afternoon, lush deep green turf, "
        "white residential home with mature trees in background, cinematic, photorealistic, 8k, magazine quality."
    ),
    "svc-commercial-lawn": (
        "Wide-angle photograph of a large commercial office park property in Michigan with pristine landscaping. "
        "Expansive manicured lawn with perfect stripe pattern, crisp bed lines around the building entrance with seasonal flowers, "
        "modern office building in the background, blue summer sky, professional commercial photography, hyper-realistic, 8k."
    ),
    "svc-hardscaping": (
        "Stunning custom backyard paver patio at dusk in a Michigan luxury home. "
        "Multi-tiered Belgard interlocking pavers in earth tones, built-in stone fire pit with golden flames, "
        "comfortable outdoor lounge furniture, retaining wall with built-in seating, ambient string lighting overhead, "
        "lush landscaping border, warm sunset glow, photorealistic architectural photography, 8k, no people."
    ),
    "svc-landscape-design": (
        "Beautifully designed landscape garden bed in front of a brick Michigan home in late spring. "
        "Layered planting with flowering hydrangeas, boxwood hedges, ornamental grasses, hostas, vibrant perennials in bloom, "
        "fresh dark hardwood mulch, natural stone border, crisp clean edges, mid-morning soft light, photorealistic, magazine quality, 8k."
    ),
    "svc-landscape-cleanup": (
        "Spring landscape refresh in a Michigan suburb. Freshly mulched garden beds with crisp clean edges, "
        "newly trimmed boxwood hedges, blooming early-season perennials, mature trees just leafing out, "
        "manicured green lawn freshly edged, residential home in background, sunny May morning, photorealistic, 8k."
    ),
    "svc-snow-removal": (
        "Pristinely cleared residential driveway and walkway after a fresh Michigan snowfall, early dawn blue hour. "
        "Crisp snow banks lining the edges, salt-treated walkway, plowed concrete driveway, "
        "snow-covered colonial home in background with warm interior lights glowing, peaceful winter scene, photorealistic, 8k, no people, no vehicles."
    ),
    "svc-commercial-snow": (
        "Large commercial parking lot fully plowed and salted at dawn after a Michigan snowstorm. "
        "Crisp clean asphalt strips between snow rows, retail or medical office building in background with lights on, "
        "professional commercial winter operations, photorealistic, 8k, no vehicles, no people."
    ),
    "svc-sod": (
        "Fresh emerald-green sod being installed on a Michigan residential property. Seamless rolls of new turf forming a perfect carpet of grass, "
        "transition line visible between newly laid sod and prepared soil, summer day, brick home in background, "
        "professional landscape photography, hyper-realistic, 8k."
    ),
    "svc-tree-services": (
        "Mature healthy oak and maple trees in a beautifully landscaped Michigan front yard, freshly pruned and shaped. "
        "Manicured lawn beneath, summer afternoon, dappled sunlight, professional tree care result, photorealistic, 8k, no people."
    ),
    "area-livonia": (
        "Aerial drone view of a well-maintained suburban Livonia Michigan residential neighborhood in summer. "
        "Tree-lined streets, manicured lawns, mature landscaping, brick colonial homes, cinematic golden hour, photorealistic, 8k."
    ),
    "area-novi": (
        "Upscale Novi Michigan residential subdivision in summer. Large luxury homes with extensive landscaping, paver driveways, "
        "manicured lawns, mature trees, golden hour, aerial perspective, photorealistic, 8k."
    ),
    "area-northville": (
        "Historic charming Northville Michigan home with classic landscaping in late spring. "
        "Mature trees, blooming gardens, white picket fence, manicured lawn, soft afternoon light, photorealistic, 8k."
    ),
    "area-plymouth": (
        "Beautiful Plymouth Michigan suburban home with professional landscaping in summer. "
        "Brick colonial, hydrangea borders, manicured lawn with stripes, hardscape walkway, photorealistic, 8k."
    ),
    "area-farmington-hills": (
        "Luxury Farmington Hills Michigan estate home with extensive professional landscaping. "
        "Sweeping front lawn, formal garden beds, paver driveway, mature trees, golden hour, aerial photo, photorealistic, 8k."
    ),
    "og-image": (
        "Wide horizontal banner image (16:9) of a stunning Michigan landscape design at golden hour. "
        "Lush manicured lawn with crisp stripes, paver patio with fire feature, blooming garden beds, brick home, "
        "warm sunset, magazine quality, hyper-realistic, 8k, no text, no logos, no people."
    ),
}

def gen_imagen4(name, prompt):
    """Try Imagen 4 (paid)."""
    resp = client.models.generate_images(
        model="imagen-4.0-generate-001",
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio="16:9",
            output_mime_type="image/jpeg",
        ),
    )
    img = resp.generated_images[0].image.image_bytes
    return img

def gen_flash(name, prompt):
    """Fallback to gemini-3.1-flash-image-preview (free tier)."""
    resp = client.models.generate_content(
        model="gemini-3.1-flash-image-preview",
        contents=prompt,
    )
    for part in resp.candidates[0].content.parts:
        if part.inline_data and part.inline_data.data:
            data = part.inline_data.data
            if isinstance(data, str):
                data = base64.b64decode(data)
            return data
    raise RuntimeError(f"No image returned for {name}")

USE_IMAGEN4 = True

def generate(name, prompt):
    global USE_IMAGEN4
    out_path = OUT / f"{name}.jpg"
    if out_path.exists() and out_path.stat().st_size > 10000:
        return f"SKIP {name} (exists)"
    try:
        if USE_IMAGEN4:
            try:
                img = gen_imagen4(name, prompt)
            except Exception as e:
                msg = str(e)
                if "billing" in msg.lower() or "permission" in msg.lower() or "not available" in msg.lower() or "403" in msg or "404" in msg:
                    print(f"  Imagen 4 unavailable ({msg[:80]}), falling back to flash-image", flush=True)
                    USE_IMAGEN4 = False
                    img = gen_flash(name, prompt)
                else:
                    raise
        else:
            img = gen_flash(name, prompt)
        out_path.write_bytes(img)
        return f"OK   {name} ({len(img)//1024} KB)"
    except Exception as e:
        return f"FAIL {name}: {str(e)[:200]}"

print(f"Generating {len(PROMPTS)} images to {OUT}", flush=True)
with ThreadPoolExecutor(max_workers=4) as ex:
    futures = {ex.submit(generate, n, p): n for n, p in PROMPTS.items()}
    for fut in as_completed(futures):
        print(fut.result(), flush=True)
print("DONE", flush=True)
