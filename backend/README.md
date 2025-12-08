# Flipp.com Price Comparison Scraper

This tool scrapes product data from **Food Basics**, **Walmart**, **FreshCo**, **Metro**, and **No Frills** flyers on Flipp.com.

## Features

- ✅ Scrapes product name, price, quantity, and unit (kg, g, lb, oz, ml, L)
- ✅ Saves data to CSV file with timestamp
- ✅ Location-based search using postal codes
- ✅ Extracts sale information and validity dates
- ✅ Easy to run on-demand

## Installation

1. Install Python dependencies:
```powershell
pip install -r requirements.txt
```

## Usage

### Quick Start

Simply run the scraper:
```powershell
python flipp_scraper.py
```

You'll be prompted to enter a postal code (or use the default Toronto location).

### Command Line Examples

```powershell
# Run with default settings
python flipp_scraper.py

# Or use the quick run script
python run_scraper.py
```

### Using as a Module

You can also import and use the scraper in your own Python code:

```python
from flipp_scraper import FlippScraper

# Create scraper
scraper = FlippScraper()

# Scrape with custom postal code
products = scraper.scrape_all_stores(postal_code="M5V3A8")

# Save to custom filename
scraper.save_to_csv(products, filename="my_products.csv")
```

## Output

The scraper creates a CSV file with the following columns:

- **store**: Store name (e.g., "Food Basics")
- **store_category**: Normalized store name
- **product_name**: Product name
- **description**: Product description
- **price**: Current price
- **quantity**: Extracted quantity value
- **unit**: Unit of measurement (kg, g, lb, oz, ml, L, pack, count)
- **pre_price_text**: Additional pricing info (e.g., "2 for $5")
- **post_price_text**: Additional pricing info
- **sale_story**: Sale description
- **valid_from**: Sale start date
- **valid_to**: Sale end date
- **brand**: Product brand
- **category**: Product category

## CSV Output Example

The file will be named something like: `flipp_products_20231208_143052.csv`

```csv
store,store_category,product_name,price,quantity,unit
Food Basics,food basics,Bananas,0.99,1,lb
Walmart,walmart,Milk 2%,4.99,4,L
FreshCo,freshco,Ground Beef,5.99,500,g
Metro,metro,Bread,2.49,675,g
```

## Notes

- The scraper includes delays between requests to be respectful to the server
- Available products depend on active flyers in your location
- Some products may not have quantity/unit information if not specified in the flyer
- The tool uses Flipp's public API endpoints

## Troubleshooting

**No products found?**
- Try a different postal code - not all stores have flyers in all locations
- Check your internet connection
- The stores might not have active flyers at the moment

**Missing quantity data?**
- Some products don't specify quantity in the flyer
- The quantity field will be empty in these cases

## Re-running the Scraper

Simply run the script again anytime you want fresh data:
```powershell
python flipp_scraper.py
```

Each run creates a new CSV file with a timestamp, so your previous data is preserved.
