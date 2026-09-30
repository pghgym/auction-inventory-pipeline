# Auction Inventory Pipeline

Automates the process of turning raw auction purchase data into a sellable, financially-modeled inventory sheet, replacing a manual, spreadsheet-by-hand workflow with a repeatable pipeline.

## Problem

When buying resale inventory from online auctions (e.g., AuctionZip-hosted auctioneers), purchase history and lot photos live in different places: an HTML purchase-history export and network capture (HAR) files containing the actual lot images. Reconciling lot numbers, titles, hammer prices, and photos by hand across dozens of lots, then manually calculating buyer's premium, tax, and shipping allocation for each item, does not scale.

## What this pipeline does

1. **Extract** - Pulls JPEG lot images out of a browser HAR capture (`extract_jpegs_from_har.py`), since auction sites often lazy-load images in ways that make simple scraping unreliable.
2. **Parse** - Parses saved HTML purchase-history pages with BeautifulSoup to extract lot number, title, hammer price, and image reference per lot (`crosswalk_builder.py`).
3. **Model** - Calculates total landed cost per lot: buyer's premium (17.5%), sales tax on premium (6%), and pro-rated shipping across all lots in a session.
4. **Assemble** - Builds a final Excel workbook with embedded lot photos next to each row, so the sheet can be used directly for resale listing and pricing decisions (`build_inventory_workbook.py`).

## Why it matters

This is a small, real ETL pipeline: unstructured web data in, structured financial-decision data out. The same pattern (scrape, parse, reconcile across sources, enrich, model cost, visualize) applies directly to healthcare and business analytics work: reconciling records across systems, calculating derived metrics, and producing decision-ready outputs.

## Tech stack

- **Python**: pandas, BeautifulSoup4, openpyxl
- Regex-based HTML parsing for semi-structured web exports
- HAR file parsing and base64 image decoding
- Excel automation with embedded images (openpyxl.drawing.image)

## Status

Functional end-to-end for a single auction session; in progress - next steps are generalizing the HTML parser beyond one auctioneer's page structure.

## Usage

```bash
pip install -r requirements.txt

python extract_jpegs_from_har.py --har path/to/capture.har --out ./images

python crosswalk_builder.py --html path/to/purchase_history.html --auctioneer "Silver City Auctions" --date "July 7th, 2026" --out ./crosswalk.csv

python build_inventory_workbook.py --csv ./crosswalk.csv --images ./images --shipping 19.50 --out ./inventory.xlsx
```

See `config.py` for adjustable fee assumptions.
