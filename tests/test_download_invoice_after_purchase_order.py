import pytest
import random
import string
from pages.home_page import HomePage
from pages.signup_login_page import SignupLoginPage
from pages.signup_form_page import SignupFormPage
from pages.personal_profile_page import PersonalProfilePage
from utils.test_data import Data
from pages.cart_page import CartPage
from pages.payment_page import PaymentPage
from utils.tools import take_screenshot


def generate_random_email():
    letters = string.ascii_lowercase
    email = ''.join(random.choice(letters) for i in range(10))
    email += '@example.com'
    return email


@pytest.fixture
def registered_user(new_page):
    page = new_page
    home_page = HomePage(page)
    signup_login = SignupLoginPage(page)
    signup_form = SignupFormPage(page)
    personal_profile = PersonalProfilePage(page)
    cart_page = CartPage(page)

    home_page.verify_that_home_page_is_visible()
    cart_page.hover_first_product()
    cart_page.click_add_to_cart_button1()
    cart_page.click_continue_shopping_button()
    cart_page.hover_second_page()
    cart_page.click_add_to_cart_button2()
    cart_page.click_continue_shopping_button()
    cart_page.click_cart_button_on_header()
    cart_page.verify_cart_page()
    cart_page.click_proceed_to_checkout_button()

    page.locator('[id="checkoutModal"] [href="/login"]').click()
    page.random_email = generate_random_email()
    signup_login.verify_new_user_title_visible()
    signup_login.enter_name(Data.username)
    signup_login.enter_email(page.random_email)
    signup_login.click_signup_button()

    signup_form.check_enter_account_information_title()
    signup_form.click_title_radio_button()
    signup_form.set_password(Data.password)
    signup_form.select_date_of_birth()
    signup_form.check_checkboxes()

    signup_form.fill_address_information(Data.firstname, Data.lastname, Data.companyname, Data.address1, Data.address2, Data.state, Data.city, Data.zipcode, Data.phonenumber)
    signup_form.click_create_account()

    signup_form.check_account_created_message()
    signup_form.click_continue_button()

    personal_profile.check_logged_in_page()


@pytest.mark.usefixtures("page", "registered_user")
class TestDownloadInvoiceAfterPurchaseOrder:

    @pytest.fixture
    def test_setup(self, new_page):
        self.page = new_page
        self.home_page = HomePage(self.page)
        self.signup_login = SignupLoginPage(self.page)
        self.personal_profile = PersonalProfilePage(self.page)
        self.cart_page = CartPage(self.page)
        self.payment_page = PaymentPage(self.page)

    def test_download_invoice_after_purchase_order(self, test_setup):
        """
        Test to Download Invoice after purchase order.
        :param test_setup: setting up the browser and page objects
        :return: None
        """

        self.cart_page.click_cart_button_on_header()
        self.cart_page.click_proceed_to_checkout_button()

        delivery_address = self.page.locator('[id="address_delivery"]').inner_text().lower()
        assert delivery_address == f"YOUR DELIVERY ADDRESS\nMr. {Data.firstname} {Data.lastname}\n{Data.companyname}\n{Data.address1}\n{Data.address2}\n{Data.city} {Data.state} {Data.zipcode}\nUnited States\n{Data.phonenumber}".lower()

        delivery_address = self.page.locator('[id="address_invoice"]').inner_text().lower()
        assert delivery_address == f"YOUR BILLING ADDRESS\nMr. {Data.firstname} {Data.lastname}\n{Data.companyname}\n{Data.address1}\n{Data.address2}\n{Data.city} {Data.state} {Data.zipcode}\nUnited States\n{Data.phonenumber}".lower()

        assert len(self.page.query_selector_all('tr[id*="product-"]')) == 2

        self.cart_page.enter_description_in_comment_text_area()
        self.cart_page.click_place_order_button()
        self.payment_page.enter_payment_details(Data.username, Data.card_number, Data.cvc, Data.expiration_month, Data.expiration_year)
        self.payment_page.click_pay_and_confirm_order_button()
        self.payment_page.verify_success_message()

        with self.page.expect_download() as event_info:
            self.payment_page.click_download_invoice_button()

        self.payment_page.click_continue_button()
        self.personal_profile.click_delete_account_link()
        self.personal_profile.verify_successful_deleted_account()
        self.personal_profile.click_continue2_button()

        take_screenshot(self.page, "download_invoice_after_purchase_order")