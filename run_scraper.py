"""
Quick launcher for Flipp scraper
Run this anytime you want to crawl fresh data from Flipp.com
"""

from flipp_scraper import FlippScraper


def quick_scrape(postal_code=None, output_filename=None):
    """
    Quick function to scrape Flipp.com and save to CSV
    
    Args:
        postal_code: Optional postal code for location (e.g., "M5V3A8")
        output_filename: Optional custom filename for CSV output
    """
    
    print("🛒 Starting Flipp.com scraper for Ontario...")
    print("Checking: Food Basics, Walmart, FreshCo, Metro, No Frills")
    print("Note: Scraping one store only (prices are same across all)")
    print("-" * 60)
    
    # Create scraper
    scraper = FlippScraper()
    
    # Scrape all stores
    products = scraper.scrape_all_stores(postal_code=postal_code)
    
    # Save results
    if products:
        scraper.save_to_csv(products, filename=output_filename)
        print("\n✅ Done! Check your CSV file for the results.")
    else:
        print("\n⚠️  No products found. Try a different postal code or check back later.")
    
    return products


if __name__ == "__main__":
    # Run the scraper
    # You can customize these parameters:
    quick_scrape(
        postal_code=None,  # Set to your postal code or leave None for default
        output_filename=None  # Set custom filename or leave None for auto-generated
    )
