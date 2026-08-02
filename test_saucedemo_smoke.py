from pages import LoginPage, InventoryPage
def test_homepage_has_correct_title(page):
    page.goto("https://www.saucedemo.com/")
    assert page.title() == "Swag Labs"
    pass

def test_login_navigates_to_inventory_page(page):
    login_page = LoginPage(page)
    login_page.open()
    login_page.login("standard_user", "secret_sauce")
    assert page.url == "https://www.saucedemo.com/inventory.html"
    pass

def test_add_item_to_cart_updates_badge(page):
    login_page = LoginPage(page)
    login_page.open()
    login_page.login("standard_user", "secret_sauce")
    inventory_page = InventoryPage(page)
    inventory_page.add_item_to_cart("add-to-cart-sauce-labs-backpack")
    assert inventory_page.get_cart_badge_count() == "1"
    pass