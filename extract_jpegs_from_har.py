"""
extract_jpegs_from_har.py

Extracts JPEG images embedded in a browser HAR (HTTP Archive) capture.

Why HAR extraction instead of simple scraping: many auction sites lazy-load
lot images via JavaScript, so a static request to the page URL won't return
the image bytes. Capturing network traffic in a HAR file (via browser dev
tools) and parsing it directly is a reliable workaround.

Usage:
    python extract_jpegs_from_har.py --har capture.har --out ./images
"""

import argparse
import json
import base64
import os


def extract_jpegs(har_path: str, output_dir: str) -> int:
    os.makedirs(output_dir, exist_ok=True)

    with open(har_path, "r", encoding="utf-8") as f:
        har = json.load(f)

    entries = har.get("log", {}).get("entries", [])
    print(f"Found {len(entries)} network entries in HAR")

    saved_count = 0

    for entry in entries:
        response = entry.get("response", {})
        content = response.get("content", {})
        mime_type = (content.get("mimeType") or "").lower()
        url = entry.get("request", {}).get("url", "")

        is_jpeg = mime_type == "image/jpeg" or url.lower().endswith((".jpg", ".jpeg"))
        if not is_jpeg:
            continue

        body_text = content.get("text")
        if not body_text:
            continue

        filename = url.split("/")[-1]
        if not filename.lower().endswith((".jpg", ".jpeg")):
            filename = f"image_{saved_count + 1}.jpg"

        output_path = os.path.join(output_dir, filename)

        try:
            encoding = content.get("encoding")
            image_bytes = (
                base64.b64decode(body_text)
                if encoding == "base64"
                else body_text.encode("utf-8")
            )
        except Exception as exc:
            print(f"Skipping {url}: decode error ({exc})")
            continue

        with open(output_path, "wb") as img_file:
            img_file.write(image_bytes)

        saved_count += 1

    print(f"Done. Saved {saved_count} JPEG images to {output_dir}")
    return saved_count


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract JPEG images from a HAR capture.")
    parser.add_argument("--har", required=True, help="Path to the .har file")
    parser.add_argument("--out", required=True, help="Output directory for extracted images")
    args = parser.parse_args()

    extract_jpegs(args.har, args.out)
