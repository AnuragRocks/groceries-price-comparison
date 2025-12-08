
import csv

def debug_csv():
    with open('product_prices.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        print(f"Headers: {headers}")
        
        products = list(reader)
        if products:
            print(f"First product keys: {products[0].keys()}")
            print(f"First product values: {products[0]}")
            
            # Check for 'milk' category specifically
            milk_items = [p for p in products if p.get('search_term') == 'milk']
            print(f"Found {len(milk_items)} items with search_term='milk'")

if __name__ == "__main__":
    debug_csv()
