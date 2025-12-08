"""
Flipp.com Web Scraper
Extracts product data from Food Basics, Walmart, FreshCo, and Metro flyers
"""

import requests
import csv
import json
from datetime import datetime
from typing import List, Dict
import time
import re


class FlippScraper:
    """Scraper for Flipp.com flyers"""
    
    def __init__(self):
        self.base_url = "https://cdn-gateflipp.flippback.com/bf/flipp"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Referer': 'https://flipp.com/'
        }
        
        # Target retailers - just need one since prices are the same
        self.target_stores = {
            'food basics': ['food basics', 'foodbasics'],
            'walmart': ['walmart'],
            'freshco': ['freshco', 'fresh co'],
            'metro': ['metro'],
            'no frills': ['no frills', 'nofrills']
        }
        
        self.postal_code = "M5H2N2"  # Default Toronto, Ontario postal code
        self.scrape_single_store_only = True  # Only scrape first available store
        
    def set_postal_code(self, postal_code: str):
        """Set postal code for location-based search"""
        self.postal_code = postal_code.replace(" ", "")
        
    def get_flyers(self) -> List[Dict]:
        """Fetch available flyers for the postal code"""
        url = f"{self.base_url}/flyers"
        params = {
            'postal_code': self.postal_code,
            'locale': 'en-CA'
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get('flyers', [])
        except Exception as e:
            print(f"Error fetching flyers: {e}")
            return []
    
    def search_flyers_by_merchant(self, merchant_query: str) -> List[Dict]:
        """Search for flyers by merchant name across Flipp"""
        url = f"{self.base_url}/flyers"
        params = {
            'postal_code': self.postal_code,
            'locale': 'en-CA',
            'q': merchant_query  # Search query parameter
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get('flyers', [])
        except Exception as e:
            print(f"Error searching flyers for '{merchant_query}': {e}")
            return []
    
    def get_all_target_flyers(self) -> List[Dict]:
        """Get flyers using multiple search strategies"""
        all_flyers = []
        seen_ids = set()
        
        # Strategy 1: Get all flyers in the area
        print("Searching for flyers in your area...")
        local_flyers = self.get_flyers()
        
        for flyer in local_flyers:
            flyer_id = flyer.get('id')
            if flyer_id not in seen_ids:
                seen_ids.add(flyer_id)
                all_flyers.append(flyer)
        
        # Strategy 2: Search specifically for each target store
        print("Searching specifically for target stores...")
        for store_name in self.target_stores.keys():
            search_flyers = self.search_flyers_by_merchant(store_name)
            for flyer in search_flyers:
                flyer_id = flyer.get('id')
                if flyer_id not in seen_ids:
                    seen_ids.add(flyer_id)
                    all_flyers.append(flyer)
            time.sleep(0.3)  # Small delay between searches
        
        return all_flyers
    
    def filter_target_flyers(self, flyers: List[Dict]) -> List[Dict]:
        """Filter flyers for target stores only"""
        filtered = []
        
        for flyer in flyers:
            merchant_name = flyer.get('merchant_name', '').lower()
            name = flyer.get('name', '').lower()
            
            # Check if this flyer matches any of our target stores
            for store_key, store_variants in self.target_stores.items():
                if any(variant in merchant_name or variant in name for variant in store_variants):
                    flyer['store_category'] = store_key
                    filtered.append(flyer)
                    break
        
        return filtered
    
    def get_flyer_items(self, flyer_id: str) -> List[Dict]:
        """Get all items from a specific flyer"""
        url = f"{self.base_url}/flyers/{flyer_id}/items"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get('items', [])
        except Exception as e:
            print(f"Error fetching items for flyer {flyer_id}: {e}")
            return []
    
    def parse_item(self, item: Dict, merchant_name: str, store_category: str) -> Dict:
        """Parse item data into a structured format"""
        
        # Extract basic info
        name = item.get('name', '').strip()
        description = item.get('description', '').strip()
        
        # Price information
        current_price = item.get('current_price')
        price = current_price if current_price else item.get('price', 'N/A')
        
        # Pre-price text (often contains pricing details like "2 for $5")
        pre_price_text = item.get('pre_price_text', '')
        post_price_text = item.get('post_price_text', '')
        sale_story = item.get('sale_story', '')
        
        # Quantity/weight extraction
        quantity = self.extract_quantity(name, description, sale_story)
        
        return {
            'store': merchant_name,
            'store_category': store_category,
            'product_name': name,
            'description': description,
            'price': price,
            'pre_price_text': pre_price_text,
            'post_price_text': post_price_text,
            'quantity': quantity['value'],
            'unit': quantity['unit'],
            'sale_story': sale_story,
            'valid_from': item.get('valid_from', ''),
            'valid_to': item.get('valid_to', ''),
            'brand': item.get('brand', ''),
            'category': item.get('category', '')
        }
    
    def extract_quantity(self, name: str, description: str, sale_story: str) -> Dict:
        """Extract quantity and unit from product information"""
        
        combined_text = f"{name} {description} {sale_story}".lower()
        
        # Patterns for weight/quantity
        patterns = [
            (r'(\d+(?:\.\d+)?)\s*kg', 'kg'),
            (r'(\d+(?:\.\d+)?)\s*g(?:ram)?s?(?:\s|$)', 'g'),
            (r'(\d+(?:\.\d+)?)\s*lb(?:s)?', 'lb'),
            (r'(\d+(?:\.\d+)?)\s*oz', 'oz'),
            (r'(\d+(?:\.\d+)?)\s*ml', 'ml'),
            (r'(\d+(?:\.\d+)?)\s*l(?:itre)?s?(?:\s|$)', 'L'),
            (r'(\d+)\s*pack', 'pack'),
            (r'(\d+)\s*ct', 'count'),
        ]
        
        for pattern, unit in patterns:
            match = re.search(pattern, combined_text)
            if match:
                return {'value': match.group(1), 'unit': unit}
        
        return {'value': '', 'unit': ''}
    
    def scrape_all_stores(self, postal_code: str = None) -> List[Dict]:
        """Main method to scrape all target stores"""
        
        if postal_code:
            self.set_postal_code(postal_code)
        
        print(f"Starting scrape for Ontario location (postal code: {self.postal_code})")
        print(f"Looking for any of: {', '.join(self.target_stores.keys())}")
        print("Note: Prices are the same across stores, so we'll scrape just one.")
        print("-" * 60)
        
        all_products = []
        
        # Get all flyers using multiple strategies
        print("Fetching flyers using multiple search methods...")
        flyers = self.get_all_target_flyers()
        print(f"Found {len(flyers)} total flyers")
        
        # Filter for target stores
        target_flyers = self.filter_target_flyers(flyers)
        print(f"Found {len(target_flyers)} flyers from target stores")
        
        if not target_flyers:
            print("⚠️  No flyers found from target stores in this location.")
            return []
        
        # Only process the first available store since prices are the same
        if self.scrape_single_store_only and target_flyers:
            print(f"\n✓ Using first available store (prices are same across all stores)")
            target_flyers = [target_flyers[0]]
        
        print("-" * 60)
        
        # Process each flyer
        for flyer in target_flyers:
            flyer_id = flyer.get('id')
            merchant_name = flyer.get('merchant_name', 'Unknown')
            store_category = flyer.get('store_category', 'unknown')
            
            print(f"\nProcessing: {merchant_name} (ID: {flyer_id})")
            
            # Get items from flyer
            items = self.get_flyer_items(flyer_id)
            print(f"  Found {len(items)} items")
            
            # Parse each item
            for item in items:
                parsed_item = self.parse_item(item, merchant_name, store_category)
                all_products.append(parsed_item)
            
            # Be respectful - add delay between requests
            time.sleep(0.5)
        
        print("\n" + "=" * 60)
        print(f"Total products scraped: {len(all_products)}")
        print("=" * 60)
        
        return all_products
    
    def save_to_csv(self, products: List[Dict], filename: str = None):
        """Save products to CSV file"""
        
        if not products:
            print("No products to save!")
            return
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"flipp_products_{timestamp}.csv"
        
        # Ensure .csv extension
        if not filename.endswith('.csv'):
            filename += '.csv'
        
        fieldnames = [
            'store', 'store_category', 'product_name', 'description', 
            'price', 'quantity', 'unit', 'pre_price_text', 'post_price_text',
            'sale_story', 'valid_from', 'valid_to', 'brand', 'category'
        ]
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(products)
            
            print(f"\n✓ Data saved to: {filename}")
            print(f"  Total rows: {len(products)}")
            
            # Print summary by store
            print("\nBreakdown by store:")
            store_counts = {}
            for product in products:
                store = product['store_category']
                store_counts[store] = store_counts.get(store, 0) + 1
            
            for store, count in sorted(store_counts.items()):
                print(f"  {store.title()}: {count} products")
                
        except Exception as e:
            print(f"Error saving CSV: {e}")


def main():
    """Main execution function"""
    
    print("=" * 60)
    print("FLIPP.COM SCRAPER - ONTARIO")
    print("Checking: Food Basics, Walmart, FreshCo, Metro, No Frills")
    print("Note: Scraping one store only (prices are same across all)")
    print("=" * 60)
    print()
    
    # Create scraper instance
    scraper = FlippScraper()
    
    # Optional: Set custom postal code
    # You can change this to your preferred Ontario location
    postal_code = input("Enter Ontario postal code (or press Enter for Toronto M5H2N2): ").strip()
    if postal_code:
        scraper.set_postal_code(postal_code)
    
    # Scrape all stores
    products = scraper.scrape_all_stores()
    
    # Save to CSV
    if products:
        scraper.save_to_csv(products)
        print("\n✓ Scraping completed successfully!")
    else:
        print("\n⚠ No products found. The stores might not have active flyers in this location.")
    
    print("\nYou can run this script anytime to refresh the data.")


if __name__ == "__main__":
    main()
