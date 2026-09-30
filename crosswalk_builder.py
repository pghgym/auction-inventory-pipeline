"""
crosswalk_builder.py

Parses saved HTML purchase-history pages and builds a structured crosswalk
(lot number -> title, hammer price, image filename) as a CSV.

Usage:
    python crosswalk_builder.py --html "Purchase History 1.html" "Purchase History 2.html" \\
        --auctioneer "Silver City Auctions" --date "July 7th, 2026" --out crosswalk.csv
"""

import argparse
import os
import re

import pandas as pd
from bs4 import BeautifulSoup

LOT_NUMBER_RE = re.compile(r"Lot\s+(\d+):")
PRICE_RE = re.compile(r"\$(\d+(?:\.\d+)?)\s+paid")


def parse_purchase_history(html_paths, auctioneer: str, date_filter: str) -> pd.DataFrame:
    rows = []

    for html_path in html_paths:
        print(f"Parsing {html_path}...")
        with open(html_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")

        for lot_block in soup.find_all("div", class_="row", recursive=True):
            text_block = lot_block.get_text(" ", strip=True)

            if date_filter not in text_block or auctioneer not in text_block:
                continue
            if "Lot " not in text_block:
                continue

            lot_match = LOT_NUMBER_RE.search(text_block)
            if not lot_match:
                continue
            lot_number = int(lot_match.group(1))

            price_match = PRICE_RE.search(text_block)
            if not price_match:
                print(f"  Warning: no hammer price found for lot {lot_number}")
                continue
            hammer_price = float(price_match.group(1))

            title_tag = lot_block.find("a", class_="font-weight-bold")
            if title_tag:
                lot_title = title_tag.get_text(strip=True)
            else:
                try:
                    after_lot = text_block.split(f"Lot {lot_number}:")[1]
                    lot_title = after_lot.split(f" by {auctioneer}")[0].strip()
                except Exception:
                    lot_title = ""

            img_tag = lot_block.find("img")
            image_filename = None
            if img_tag:
                src = img_tag.get("data-src") or img_tag.get("src") or ""
                image_filename = os.path.basename(src) if src else None

            rows.append({
                "Lot number": lot_number,
                "Lot title": lot_title,
                "Hammer price": hammer_price,
                "Image filename": image_filename,
            })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("Lot number").reset_index(drop=True)
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build a lot crosswalk from HTML purchase history.")
    parser.add_argument("--html", nargs="+", required=True, help="Path(s) to purchase-history HTML files")
    parser.add_argument("--auctioneer", required=True, help="Auctioneer name to filter on")
    parser.add_argument("--date", required=True, help="Date string to filter on, as it appears in the page text")
    parser.add_argument("--out", required=True, help="Output CSV path")
    args = parser.parse_args()

    result_df = parse_purchase_history(args.html, args.auctioneer, args.date)
    print(f"Total rows collected: {len(result_df)}")
    result_df.to_csv(args.out, index=False)
    print(f"Saved crosswalk to {args.out}")
