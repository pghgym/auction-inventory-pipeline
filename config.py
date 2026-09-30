"""
Configuration for the auction inventory pipeline.
Adjust these values per auction session; nothing else in the pipeline
should need hardcoded paths or fee assumptions.
"""

# Fee assumptions
BUYERS_PREMIUM_RATE = 0.175   # 17.5% of hammer price
TAX_RATE_ON_PREMIUM = 0.06    # 6% tax, applied to the buyer's premium

# Auction session metadata (used for filtering HTML purchase-history exports)
AUCTION_PLATFORM = "AuctionZip"
AUCTIONEER_NAME = "Silver City Auctions"
AUCTION_DATE = "2026-07-07"

# Excel output settings
IMAGE_COLUMN_LETTER = "M"
ROW_HEIGHT = 80
IMAGE_WIDTH_PX = 80
IMAGE_HEIGHT_PX = 80
