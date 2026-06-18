import os
import re


DEMOS_DIR = os.path.dirname(os.path.abspath(__file__))


FALLBACK_MAP = {
    "cafe": "../shared/cafe-hero.jpg",
    "coffee": "../shared/coffee-hero.jpg",
    "restaurant": "../shared/restaurant-hero.jpg",
    "seafood": "../shared/seafood-hero.jpg",
    "bakery": "../shared/bakery-hero.jpg",
    "cake": "../shared/bakery-hero.jpg",
    "bar": "../shared/bar-hero.jpg",
    "bistro": "../shared/bar-hero.jpg",
    "cocktail": "../shared/bar-hero.jpg",
    "goan": "../shared/restaurant-hero.jpg",
    "default": "../shared/restaurant-hero.jpg",
}


def detect_fallback(html):
    """Detect the best local fallback image for this site."""
    low = html.lower()
    for key in ["seafood", "goan", "bakery", "cake", "coffee", "bistro", "cocktail", "bar", "cafe", "restaurant"]:
        if key in low:
            return FALLBACK_MAP[key]
    return FALLBACK_MAP["default"]


def add_fallbacks_to_file(filepath):
    with open(filepath, "r", encoding="utf-8") as file_handle:
        content = file_handle.read()

    original = content
    fallback = detect_fallback(content)

    def patch_img_tag(match):
        tag = match.group(0)
        if "onerror" in tag:
            return tag
        return tag.rstrip(">") + f' onerror="this.onerror=null;this.src=\'{fallback}\'">'

    content = re.sub(
        r'<img\b[^>]*src="https://images\.unsplash\.com[^"]*"[^>]*>',
        patch_img_tag,
        content,
        flags=re.IGNORECASE,
    )

    if "Hero image fallback" not in content:
        js_block = rf"""
    <script>
    /* Hero image fallback - if Unsplash CDN is unreachable, show local image */
    (function () {{
        var heroBg = document.querySelector('.hero-bg');
        if (!heroBg) return;
        var styleVal = heroBg.style.backgroundImage || '';
        var match = styleVal.match(/url\(['\"]?(.*?)['\"]?\)/);
        if (!match || !match[1]) return;
        var testImg = new Image();
        testImg.onerror = function () {{
            heroBg.style.backgroundImage = "url('{fallback}')";
        }};
        testImg.src = match[1];
    }})();
    </script>
"""
        content = content.replace("</body>", js_block + "</body>", 1)

    if content != original:
        with open(filepath, "w", encoding="utf-8") as file_handle:
            file_handle.write(content)
        return True
    return False


def main():
    html_files = []
    for root, dirs, files in os.walk(DEMOS_DIR):
        dirs[:] = [directory for directory in dirs if directory not in ("shared", ".git")]
        for filename in files:
            if filename == "index.html":
                html_files.append(os.path.join(root, filename))

    print(f"Processing {len(html_files)} HTML files...")
    updated = 0
    for index, filepath in enumerate(html_files):
        try:
            if add_fallbacks_to_file(filepath):
                updated += 1
        except Exception as error:
            print(f"  ERROR {filepath}: {error}")
        if (index + 1) % 100 == 0:
            print(f"  {index + 1}/{len(html_files)} done...")

    print(f"\nDone. Updated {updated} / {len(html_files)} files with fallback images.")


if __name__ == "__main__":
    main()