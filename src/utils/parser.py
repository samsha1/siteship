import re
import zipfile
from pathlib import Path
from src.common.logger import get_logger


logger = get_logger(__name__)

async def extract_and_zip_code(model_response: str, user_id: str) -> str:
    """
    Parses Gemini response, writes HTML, CSS, JS to files,
    zips them, and returns local zip path.
    """

    base_dir = Path(f"./tmp/{user_id}")
    base_dir.mkdir(parents=True, exist_ok=True)

    # Regex for ````html ... ````
    html_match = re.search(r"```html(.*?)```css", model_response, re.DOTALL | re.IGNORECASE)
    css_match = re.search(r"```css(.*?)```javascript", model_response, re.DOTALL | re.IGNORECASE)
    js_match = re.search(r"```javascript(.*?)```", model_response, re.DOTALL | re.IGNORECASE)

    if not html_match or not css_match or not js_match:
        logger.error("One or more code blocks missing in Gemini response")

    html_code = html_match.group(1).strip().encode("utf-8")
    css_code = css_match.group(1).strip()
    js_code = js_match.group(1).strip()

    if isinstance(html_code, bytes):
        html_code = html_code.decode("utf-8")

    if isinstance(css_code, bytes):
        css_code = css_code.decode("utf-8")

    if isinstance(js_code, bytes):
        js_code = js_code.decode("utf-8")
    # Write files
    html_file = base_dir / "index.html"
    css_file = base_dir / "style.css"
    js_file = base_dir / "script.js"
    zip_file = base_dir / "site.zip"

    html_file.write_text(html_code)
    css_file.write_text(css_code)
    js_file.write_text(js_code)

    # Zip them
    with zipfile.ZipFile(zip_file, "w") as zipf:
        zipf.write(html_file, arcname="index.html")
        zipf.write(css_file, arcname="style.css")
        zipf.write(js_file, arcname="script.js")

    return str(zip_file)
