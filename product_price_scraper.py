"""
Flipp.com Product Price Scraper
Searches for commonly bought grocery products and extracts their prices
"""

import requests
import csv
from datetime import datetime
from typing import List, Dict
import time
import re


class FlippProductScraper:
    """Scraper for searching products on Flipp.com"""
    
    def __init__(self):
        self.base_url = "https://cdn-gateflipp.flippback.com/bf/flipp"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Referer': 'https://flipp.com/'
        }
        
        self.postal_code = "M5H2N2"  # Toronto, Ontario
        
        # Commonly bought grocery products
        self.common_products = [
            # Dairy & Eggs
            "milk", "eggs", "cheese", "butter", "yogurt",
            # Meat & Protein
            "chicken breast", "ground beef", "pork chops", "bacon", "salmon",
            # Produce
            "bananas", "apples", "oranges", "tomatoes", "potatoes", "onions", "lettuce", "carrots",
            # Bread & Bakery
            "bread", "bagels", "tortillas",
            # Pantry Staples
            "rice", "pasta", "flour", "sugar", "oil", "coffee", "tea",
            # Canned & Packaged
            "canned tomatoes", "beans", "soup", "cereal", "oatmeal",
            # Frozen
            "frozen vegetables", "frozen pizza", "ice cream",
            # Beverages
            "orange juice", "apple juice", "soda", "water bottles",
            # Snacks
            "chips", "crackers", "cookies",
            # Condiments
            "ketchup", "mayonnaise", "mustard", "salt", "pepper"
        ]
        
    def set_postal_code(self, postal_code: str):
        """Set postal code for location-based search"""
        self.postal_code = postal_code.replace(" ", "")
    
    def search_product(self, product_name: str) -> List[Dict]:
        """Search for a specific product"""
        url = f"{self.base_url}/items/search"
        params = {
            'postal_code': self.postal_code,
            'locale': 'en-CA',
            'q': product_name
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get('items', [])
        except Exception as e:
            print(f"Error searching for '{product_name}': {e}")
            return []
    
    def extract_quantity_and_unit(self, text: str) -> tuple:
        """Extract quantity and unit from text"""
        if not text:
            return "", ""
        
        # Common patterns for quantities
        patterns = [
            r'(\d+(?:\.\d+)?)\s*(kg|g|lb|oz|ml|l|litre|liter)',
            r'(\d+)\s*(pack|count|ct)',
            r'(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)\s*(kg|g|lb|oz|ml|l)',
        ]
        
        text_lower = text.lower()
        
        for pattern in patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                if len(match.groups()) >= 2:
                    return match.group(1), match.group(2)
        
        return "", ""
    
    def parse_price(self, price_text: str) -> str:
        """Extract numeric price from price text"""
        if not price_text:
            return ""
        
        # Extract numbers and decimal point
        match = re.search(r'\$?(\d+(?:\.\d{1,2})?)', str(price_text))
        if match:
            return f"${match.group(1)}"
        return price_text
    
    def scrape_all_products(self) -> List[Dict]:
        """Search for all common products and collect their data"""
        all_products = []
        
        print(f"Searching for {len(self.common_products)} common products...")
        print("=" * 80)
        
        for i, product in enumerate(self.common_products, 1):
            print(f"[{i}/{len(self.common_products)}] Searching: {product}...")
            
            items = self.search_product(product)
            
            if items:
                print(f"  ✓ Found {len(items)} results")
                
                for item in items[:5]:  # Take top 5 results per product
                    name = item.get('name', '')
                    price = item.get('current_price', '')
                    description = item.get('description', '')
                    brand = item.get('brand', '')
                    merchant = item.get('merchant_name', '')
                    category = item.get('category', '')
                    flyer_id = item.get('flyer_id', '')
                    item_id = item.get('id', '')
                    
                    # Build Flipp URL for the product
                    product_url = ''
                    if flyer_id and item_id:
                        product_url = f"https://flipp.com/en-ca/flyer/{flyer_id}/item/{item_id}"
                    elif flyer_id:
                        product_url = f"https://flipp.com/en-ca/flyer/{flyer_id}"
                    
                    # Extract quantity and unit
                    full_text = f"{name} {description}"
                    quantity, unit = self.extract_quantity_and_unit(full_text)
                    
                    product_data = {
                        'search_term': product,
                        'product_name': name,
                        'price': self.parse_price(price),
                        'quantity': quantity,
                        'unit': unit,
                        'brand': brand,
                        'store': merchant,
                        'category': category,
                        'description': description,
                        'product_url': product_url,
                        'scraped_date': datetime.now().strftime('%Y-%m-%d'),
                        'scraped_time': datetime.now().strftime('%H:%M:%S')
                    }
                    
                    all_products.append(product_data)
            else:
                print(f"  ✗ No results found")
            
            # Small delay to be respectful
            time.sleep(0.5)
        
        return all_products
    
    def save_to_csv(self, products: List[Dict], filename: str = None):
        """Save products to CSV file"""
        if not products:
            print("\n⚠ No products to save.")
            return
        
        if filename is None:
            filename = 'product_prices.csv'
        
        fieldnames = [
            'search_term', 'product_name', 'price', 'quantity', 'unit',
            'brand', 'store', 'category', 'description', 'product_url',
            'scraped_date', 'scraped_time'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(products)
        
        print("\n" + "=" * 80)
        print(f"✓ Successfully saved {len(products)} products to: {filename}")
        print("=" * 80)


def main():
    print("\n" + "=" * 80)
    print("FLIPP.COM PRODUCT PRICE SCRAPER - ONTARIO")
    print("Searching for commonly bought grocery products")
    print("=" * 80 + "\n")
    
    scraper = FlippProductScraper()
    
    # Optional: Allow user to set postal code
    user_postal = input("Enter Ontario postal code (or press Enter for Toronto M5H2N2): ").strip()
    if user_postal:
        scraper.set_postal_code(user_postal)
    
    print(f"\nStarting product search for Ontario location (postal code: {scraper.postal_code})")
    print("-" * 80 + "\n")
    
    # Scrape all products
    products = scraper.scrape_all_products()
    
    # Save to CSV
    scraper.save_to_csv(products)
    
    print("\nYou can run this script anytime to refresh the product prices.")


if __name__ == "__main__":
    main()
