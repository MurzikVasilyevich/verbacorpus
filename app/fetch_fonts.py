import re, os, urllib.request

css = open("/tmp/spectral.css").read()
blocks = re.findall(r"/\*\s*([\w-]+)\s*\*/\s*@font-face\s*\{(.*?)\}", css, re.S)
want = {"cyrillic", "cyrillic-ext", "latin"}
os.makedirs("public/fonts", exist_ok=True)
faces = []
ua = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
seen = set()
for subset, body in blocks:
    if subset not in want:
        continue
    wght = re.search(r"font-weight:\s*(\d+)", body)
    ital = "italic" in body
    url = re.search(r"url\((https://[^)]+\.woff2)\)", body)
    rng = re.search(r"unicode-range:\s*([^;]+);", body)
    if not (wght and url):
        continue
    w = wght.group(1)
    style = "italic" if ital else "normal"
    name = f"spectral-{w}-{style}-{subset}.woff2"
    path = f"public/fonts/{name}"
    key = (w, style, subset)
    if key in seen:
        continue
    seen.add(key)
    req = urllib.request.Request(url.group(1), headers={"User-Agent": ua})
    data = urllib.request.urlopen(req).read()
    open(path, "wb").write(data)
    faces.append((w, style, subset, name, rng.group(1).strip() if rng else "", len(data)))

faces.sort()
total = sum(f[5] for f in faces)
print(f"downloaded {len(faces)} woff2, total {total//1024} KB")
# emit @font-face CSS
out = []
for w, style, subset, name, rng, sz in faces:
    out.append(
        "@font-face{font-family:'Spectral';font-style:%s;font-weight:%s;font-display:swap;"
        "src:url('/fonts/%s') format('woff2');unicode-range:%s}" % (style, w, name, rng)
    )
open("public/fonts/spectral.css", "w").write("\n".join(out) + "\n")
for f in faces:
    print(f"  {f[3]}  {f[5]//1024}KB")
print("wrote public/fonts/spectral.css")
