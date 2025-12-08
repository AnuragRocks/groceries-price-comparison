
from compare_prices import ProductComparator

def verify_display():
    c = ProductComparator()
    # Search for 'milk' which we know has mixed prices
    print("Testing display for 'milk':")
    c.display_comparison('milk')
    
    # Search for 'eggs'
    print("\nTesting display for 'eggs':")
    c.display_comparison('eggs')

if __name__ == "__main__":
    verify_display()
