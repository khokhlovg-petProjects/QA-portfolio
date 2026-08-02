class LoginPage:
    def __init__(self, page):
        # TODO: сохрани page как атрибут self (вспомни call_oop.py — та же идея)
        self.page = page
        pass

    def open(self):
        # TODO: перейди на https://www.saucedemo.com/, используя self.page.goto(...)
        self.page.goto("https://www.saucedemo.com/")
        pass

    def login(self, username: str, password: str):
        # TODO: используя self.page.locator(...), найди поля username/password,
        # заполни их переданными username/password, и кликни кнопку логина
        # (локаторы у тебя уже есть в test_saucedemo_smoke.py — просто перенеси их сюда)
        self.page.locator("#user-name").fill(username)
        self.page.locator("#password").fill(password)
        self.page.locator("#login-button").click()
        pass

class InventoryPage:
    def __init__(self, page):
        # TODO: сохрани page как атрибут self (третий раз этот же паттерн — должно быть уже привычно)
        self.page = page
        pass

    def add_item_to_cart(self, item_test_id: str):
        # TODO: используя self.page.locator(...), найди кнопку "Add to cart" по data-test атрибуту.
        # Атрибут передаётся параметром item_test_id (например, "add-to-cart-sauce-labs-backpack"),
        # а не захардкожен внутри метода — собери селектор через f-строку, используя этот параметр
        self.page.locator(f"[data-test='{item_test_id}']").click()
        pass

    def get_cart_badge_count(self) -> str:
        # TODO: найди бейдж корзины (селектор ".shopping_cart_badge")
        # и верни (return) его текст, а не просто прочитай его
        return self.page.locator(".shopping_cart_badge").inner_text()
        pass