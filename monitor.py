import ssl
import time

from utils.config import TIMEOUT
from utils.config import USERS
from utils.log import logger
from visa import Visa
# import undetected_chromedriver as uc
import threadpool
import pyttsx3


def init_driver():
    profile = {
        "profile.default_content_setting_values.notifications": 1  # block notifications
    }
    ssl._create_default_https_context = ssl._create_unverified_context
    chrome_options = uc.ChromeOptions()
    chrome_options.add_experimental_option('prefs', profile)
    chrome_options.add_argument("--incognito")

#     driver = uc.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    driver.delete_all_cookies()
    return driver


def monitor(email, password, url, centers, mode):

    driver = init_driver()
    visa = Visa(driver)
    try:
        time.sleep(1)
        visa.go_to_appointment_page(url)
        time.sleep(1)
        visa.login(email, password)
        time.sleep(1)
        visa.go_to_book_appointment(url, email)
        visa.select_centre(centers[0], centers[1], centers[2], email)
        while True:
            dates = visa.check_available_dates(mode, centers[3], email)
            if dates:
                logger.info(f"USER {email} DAY AVAILABLE: {dates}")
                pyttsx3.speak(f"say day available {email} {dates}")
                time.sleep(10)
                # 10s 后继续进入下一个循环
            else:
                logger.info(f"{email}: NO DAY AVAILABLE...")
                driver.refresh()
                time.sleep(TIMEOUT)

    except Exception as e:
        logger.error(f'Monitor runtime error from {email} {e}')
        driver.quit()
        monitor(email, password, url, centers, mode)


if __name__ == "__main__":

    # 执行部分
    pool = threadpool.ThreadPool(len(USERS))
    gl_tasks = threadpool.makeRequests(monitor, USERS)
    for task in gl_tasks:
        pool.putRequest(task)
    pool.wait()
