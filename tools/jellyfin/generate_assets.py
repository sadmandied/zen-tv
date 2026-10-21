import os, sys, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.stdout.reconfigure(encoding="utf-8")

out_dir = r"C:\Users\Sadman\.gemini\antigravity\scratch\cleanyourtv\jellyfin_showcase"
os.makedirs(out_dir, exist_ok=True)

movies = [
    {
        "id": "4fa984fc91c397562bb711c003e6d9e7",
        "name": "12 Angry Men",
        "year": "1957",
        "rating": "9.0",
        "poster": r"C:\ProgramData\Jellyfin\Server\metadata\library\4f\4fa984fc91c397562bb711c003e6d9e7\poster.jpg",
        "backdrop": r"C:\ProgramData\Jellyfin\Server\metadata\library\4f\4fa984fc91c397562bb711c003e6d9e7\backdrop.jpg"
    },
    {
        "id": "49c14b2b31e5997f56eac60f59f54acf",
        "name": "Avengers: Endgame",
        "year": "2019",
        "rating": "8.4",
        "poster": r"C:\ProgramData\Jellyfin\Server\metadata\library\49\49c14b2b31e5997f56eac60f59f54acf\poster.jpg",
        "backdrop": r"C:\ProgramData\Jellyfin\Server\metadata\library\49\49c14b2b31e5997f56eac60f59f54acf\backdrop.jpg"
    },
    {
        "id": "fd6e89af2b641c3fa6d85f2523dc8c7c",
        "name": "Project Hail Mary",
        "year": "2026",
        "rating": "8.3",
        "poster": r"C:\ProgramData\Jellyfin\Server\metadata\library\fd\fd6e89af2b641c3fa6d85f2523dc8c7c\poster.jpg",
        "backdrop": r"C:\ProgramData\Jellyfin\Server\metadata\library\fd\fd6e89af2b641c3fa6d85f2523dc8c7c\backdrop.jpg"
    },
    {
        "id": "2f614859b2f59629971ea36f228cff87",
        "name": "Bonolota Express",
        "year": "2026",
        "rating": "8.3",
        "poster": r"C:\ProgramData\Jellyfin\Server\metadata\library\2f\2f614859b2f59629971ea36f228cff87\poster.jpg",
        "backdrop": r"C:\ProgramData\Jellyfin\Server\metadata\library\2f\2f614859b2f59629971ea36f228cff87\backdrop.jpg"
    },
    {
        "id": "7482c17eea182c153d8b65442559ef96",
        "name": "Uri: The Surgical Strike",
        "year": "2019",
        "rating": "8.2",
        "poster": r"C:\ProgramData\Jellyfin\Server\metadata\library\74\7482c17eea182c153d8b65442559ef96\poster.jpg",
        "backdrop": r"C:\ProgramData\Jellyfin\Server\metadata\library\74\7482c17eea182c153d8b65442559ef96\backdrop.jpg"
    },
    {
        "id": "17f967bf228f447d537ee9d2608669b8",
        "name": "Spider-Man: Brand New Day",
        "year": "2026",
        "rating": "8.0",
        "poster": r"C:\ProgramData\Jellyfin\Server\metadata\library\17\17f967bf228f447d537ee9d2608669b8\poster.jpg",
        "backdrop": r"C:\ProgramData\Jellyfin\Server\metadata\library\17\17f967bf228f447d537ee9d2608669b8\backdrop.jpg"
    }
]

movie_metadata = []

for idx, m in enumerate(movies):
    print(f"Processing #{idx+1}: {m['name']}...")
    
    # 1. Process Backdrop: 1920x1080 with bottom 45% darkened to OLED black
    bd_raw = Image.open(m["backdrop"]).convert("RGB")
    bd_scaled = bd_raw.resize((1920, 1080), Image.Resampling.LANCZOS)
    
    # Create black gradient mask for bottom 45% (from y=500 to y=850 fade to 0)
    bd_final = bd_scaled.copy()
    overlay = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Gradient fade from y=480 to 800, solid black from 800 down
    for y in range(480, 1080):
        if y < 820:
            alpha = int(255 * ((y - 480) / (820 - 480)))
        else:
            alpha = 255
        draw.line([(0, y), (1920, y)], fill=(0, 0, 0, alpha))
        
    bd_final.paste(overlay, (0, 0), overlay)
    bd_out_path = os.path.join(out_dir, f"backdrop_{idx}.jpg")
    bd_final.save(bd_out_path, "JPEG", quality=85, optimize=True)
    
    # 2. Process Tile Banner: 360x202 (16:9 banner)
    # Backdrop as background, center-cropped 16:9
    tb = bd_scaled.resize((360, 202), Image.Resampling.LANCZOS)
    # Add subtle dark vignette
    tb_dark = Image.new("RGBA", (360, 202), (0, 0, 0, 0))
    tb_draw = ImageDraw.Draw(tb_dark)
    # Subtle gradient at bottom for text
    for ty in range(120, 202):
        a = int(180 * ((ty - 120) / (202 - 120)))
        tb_draw.line([(0, ty), (360, ty)], fill=(0, 0, 0, a))
    tb.paste(tb_dark, (0, 0), tb_dark)
    
    # Add small poster on left side with rounded corners
    post_raw = Image.open(m["poster"]).convert("RGBA")
    # Scale poster to height 170 (width ~115)
    pw = int(170 * post_raw.width / post_raw.height)
    post_scaled = post_raw.resize((pw, 170), Image.Resampling.LANCZOS)
    
    # Create composite banner:
    # Blur the backdrop slightly on the tile so the poster and title pop!
    tb_blur = tb.filter(ImageFilter.GaussianBlur(radius=3))
    
    banner_canvas = Image.new("RGBA", (360, 202), (10, 12, 18, 255))
    banner_canvas.paste(tb_blur, (0, 0))
    
    # Paste poster at (16, 16)
    banner_canvas.paste(post_scaled, (16, 16), post_scaled)
    
    # Save tile banner
    tile_out_path = os.path.join(out_dir, f"tile_{idx}.jpg")
    banner_canvas.convert("RGB").save(tile_out_path, "JPEG", quality=90, optimize=True)
    
    movie_metadata.append({
        "id": m["id"],
        "name": m["name"],
        "year": m["year"],
        "rating": m["rating"],
        "title": f"★ {m['rating']}  {m['name']} ({m['year']})",
        "tile": f"tile_{idx}.jpg",
        "backdrop": f"backdrop_{idx}.jpg"
    })

meta_path = os.path.join(out_dir, "movies.json")
with open(meta_path, "w", encoding="utf-8") as f:
    json.dump(movie_metadata, f, indent=2)

print(f"Generated assets for {len(movies)} movies in {out_dir}")
for m in movie_metadata:
    print(f" - {m['title']}")
