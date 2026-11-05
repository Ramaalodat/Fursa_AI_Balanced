from pathlib import Path
# pyrefly: ignore[missing-import]
import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
sources = {
    "graduate": "duck_graduate.png",
    "assessment": "duck_assessment.png",
    "detective": "duck_detective_generated.png",
    "coder": "duck_coder_generated.png",
    "success": "duck_success_generated.png",
    "tea": "duck_tea_generated.png",
}
for label, filename in sources.items():
    src = ROOT / "originals" / filename
    if not src.exists():
        print("Missing image:", src)
        continue
    picture = Image.open(src).convert("RGB")
    picture.thumbnail((900, 900), Image.Resampling.LANCZOS)
    rgb = np.asarray(picture).copy()
    lo = rgb.min(axis=2).astype(np.int16)
    hi = rgb.max(axis=2).astype(np.int16)
    light = ((lo >= 236) & ((hi - lo) < 22)).astype(np.uint8)
    _, labels = cv2.connectedComponents(light, connectivity=8)
    border = np.unique(np.concatenate((labels[0,:], labels[-1,:], labels[:,0], labels[:,-1])))
    border = border[border > 0]
    background = np.isin(labels, border)
    alpha = np.where(background, 0, 255).astype(np.uint8)
    alpha = cv2.GaussianBlur(alpha, (3, 3), 0.5)
    rgba = np.dstack((rgb,alpha))
    out = Image.fromarray(rgba, "RGBA")
    dest = ROOT / ("duck_" + label + ".webp")
    out.save(dest, "WEBP", quality=86, method=6)
    print(label, out.size, round(dest.stat().st_size / 1024), "KB")
    if label == "graduate":
        preview = Image.new("RGB", out.size, "#f6f1ff")
        preview.paste(out, mask=out.getchannel("A"))
        preview.save(ROOT / "preview_transparency.png")
