from playwright.sync_api import Page

def test_sort_inventory_by_price_low_to_high(page: Page):
    saucedemo_inventory_URL = "https://www.saucedemo.com/v1/inventory.html"
    max_explicit_timeout = 1

    # 1. Open the SauceDemo Inventory Page
    page.goto(saucedemo_inventory_URL)
    
    # Wait up to 5 seconds for inventory list to load
    page.wait_for_selector(".inventory_item_price", timeout=max_explicit_timeout)

    # 2. Locate the Sorting Dropdown
    sort_dropdown = page.locator("select.product_sort_container")

    # 3. Select "Price (Low to High)"
    sort_dropdown.select_option("lohi")

    # Wait up to 5 seconds for page to update after sorting
    page.wait_for_selector(".inventory_item_price", timeout=max_explicit_timeout)

    # Retrieve all item prices
    prices = page.locator(".inventory_item_price").all_text_contents()
    
    # Convert prices to float for comparison
    prices = [float(price.replace("$", "")) for price in prices]

    # a. Verify that prices list is not empty
    assert prices, "Test failed: No prices found which indicates inventory is empty!"    

    # b. Verify that first item is lowest price
    assert prices[0] == min(prices), f"Test failed: First price ${prices[0]} is not the lowest ${min(prices)} price!"

    # c. Verify that last item is highest price
    assert prices[-1] == max(prices), f"Test failed: Last price ${prices[-1]} is not the highest ${max(prices)} price!"
    
    # d. Verify that prices are sorted in ascending order
    assert prices == sorted(prices), "Test failed: Items are not sorted by price from low to high!"
