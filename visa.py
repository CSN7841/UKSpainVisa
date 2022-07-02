from datetime import datetime

from utils import config
from utils.basic import Basic
from utils.log import logger
from selenium.webdriver.support.select import Select


class Visa(Basic):

    def __init__(self, driver):
        super().__init__(driver)

    def open_page(self, page):
        self.driver.get(page)

    def select_centre(self, county, city, category, email):
        self.wait_for_secs()
        self.click_el(name="JurisdictionId")
        self.click_el(xpath="//select[@name='JurisdictionId']/option[contains(text(),'{}')]".format(county))
        self.wait_for_loading()
        self.click_el(name="centerId")
        self.click_el(xpath="//select[@name='centerId']/option[contains(text(),'{}')]".format(city))
        self.wait_for_secs()
        self.click_el(name="category")
        self.click_el(xpath="//select[@name='category']/option[contains(text(),'{}')]".format(category))
        self.wait_for_secs()
        self.click_el(name='checkDate')
        logger.info(f"User {email} select centre finished !")

    def go_to_appointment_page(self):
        self.wait_for_secs()
        self.open_page(config.FIXED)
        self.wait_for_loading()

    def login(self, email, password):
        try:
            element = self.driver.find_element_by_xpath("//a[contains(text(),'Log in')]")
            element.click()
            self.wait_for_secs()
            self.enter_message(email, name='email')
            self.wait_for_secs()
            self.enter_message(password, name='password')
            self.wait_for_secs()
            self.click_el(name="login")
            logger.info(f"User {email} log in finished !")
        except Exception as e:
            logger.error(e)

    def go_to_book_appointment(self, email):
        self.wait_for_loading()
        link = self.driver.current_url.split('/')[-1]
        element = self.driver.find_element_by_xpath("//a[contains(text(),'Book Appointment')]")
        element.click()
        logger.info(f"User {email} date appointment link = [{link}]")
        logger.info(f"User {email} go to book appointment finished !")

    def check_available_dates(self, mode, category, email):
        self.click_el(id="VisaTypeId")
        self.click_el(xpath="//select[@id='VisaTypeId']/option[contains(text(),'{}')]".format(category))
        self.wait_for_secs()

        # 勾选模式
        sms = self.driver.find_element_by_id("vasId12")
        if not sms.is_selected() and mode[0] == 'Yes':
            sms.click()
            self.wait_for_secs()
        photo = self.driver.find_element_by_id("vasId5")
        if not photo.is_selected() and mode[1] == 'Yes':
            photo.click()
            self.wait_for_secs()
        premium = self.driver.find_element_by_id("vasId1")
        if not premium.is_selected() and mode[2] == 'Yes':
            premium.click()
            self.wait_for_secs()
        courier = self.driver.find_element_by_id("courierId")
        if not courier.is_selected() and mode[3] == 'Yes':
            courier.click()
            self.wait_for_secs()

        # check date
        self.click_el(id="app_date")
        available_dates = {}
        next_button_xpath = "//div[@class = 'datepicker-days']//th[@class = 'next' and @style = 'visibility: visible;']"  # next month
        while True:
            nd = self.get_normal_dates(email)
            if nd:
                available_dates.update(nd)
            if self.driver.find_elements_by_xpath(next_button_xpath):
                self.wait_for_secs()
                self.click_el(xpath=next_button_xpath)
            else:
                break

        return available_dates

    def check_finished(self, email):
        self.wait_for_secs(3)
        if not self.driver.find_element_by_xpath("//*[contains(text(), '{}')]".format("Book Appointment")).is_enabled():
            logger.warning(f"User {email} has had a visa !!!")
            return 0
        else:
            logger.warning(f"User {email} doesn't have a visa !!!")
            return 1

    def get_normal_dates(self, email):
        normal_dates_xpath = "//div[@class='datepicker-days']//td[not(contains(@class, 'disabled'))]"
        # days in the current month
        result_dates = {}
        dates = []
        if len(self.driver.find_elements_by_xpath(normal_dates_xpath)):
            found_month = self.driver.find_element_by_xpath(
                "//div[@class='datepicker-days']//th[@class='datepicker-switch']").text
            for day in self.driver.find_elements_by_xpath(normal_dates_xpath):  # need refactor fix
                dates.append(day.text)
            for day in dates:
                found_date = datetime.strptime(day + " " + found_month, '%d %B %Y')
                result_dates[found_date.strftime("%d/%m/%Y")] = []

            logger.info(f"User {email} found date {result_dates}")
            self.click_el(normal_dates_xpath)  # 自动点击
            self.wait_for_secs()

            # 选择日期，最晚的那个
            select_el = self.driver.find_element_by_id("app_time")
            select_el.click()
            self.wait_for_secs()
            select = Select(select_el)
            # 在这里调第几个时间
            select.select_by_index(-1)
            logger.info(f" User {email} 's time selected !")

            # 点击确认
            self.wait_for_secs()
            confirm = self.driver.find_element_by_name("bookDate")
            confirm.click()
            logger.info(f"User {email} finished !")

        return result_dates
