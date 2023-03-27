"""
基于undetected_edgedriver的ChatGPT自动登录脚本，ChatGPT使用微软账号首次登录，无法正常重定向，本脚本的目的是预处理注册好的微软账号，使其可以正常登录ChatGPT。
selenium不能通过cf盾，使用undetected_edgedriver可以绕过cf盾。
偶尔会弹出cf盾验证，需要手动验证。

Author: Eli Lee
Version: 1.0
Import: outlook.csv
Export: ok.csv

"""

from selenium.webdriver.common.by import By
from undetected_edgedriver import Edge, EdgeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import csv

from webdriver_manager.microsoft import EdgeChromiumDriverManager


def register(mail, password):
    options = EdgeOptions()
    options.add_argument("--inprivate")  # 启用Edge浏览器无痕模式
    driver = Edge(driver_executable_path=EdgeChromiumDriverManager().install(), options=options)
    wait = WebDriverWait(driver, 60)  # 最长等待时间为60秒
    driver.get('https://chat.openai.com/auth/login')
    wait.until(ec.title_contains('ChatGPT | OpenAI'))  # 等待标题包含“Log In - OpenAI Chat”
    driver.find_element(By.XPATH,
                        '//div[@class="flex w-full items-center justify-center gap-2" and text()="Sign up"]').click()
    wait.until(ec.element_to_be_clickable(
        (By.XPATH, '//span[@class="c47d81fe7" and text()="Continue with Microsoft Account"]')))
    driver.find_element(By.XPATH, '//span[@class="c47d81fe7" and text()="Continue with Microsoft Account"]').click()
    wait.until(ec.element_to_be_clickable((By.ID, 'idSIButton9')))
    driver.find_element(By.ID, 'i0116').send_keys(mail)
    driver.find_element(By.ID, 'idSIButton9').click()
    wait.until(ec.element_to_be_clickable((By.ID, 'idA_PWD_ForgotPassword')))
    driver.find_element(By.ID, 'i0118').send_keys(password)
    driver.find_element(By.ID, 'idSIButton9').click()

    element = wait.until(ec.any_of(ec.element_to_be_clickable((By.ID, 'piplConsentContinue')),
                                   ec.element_to_be_clickable((By.ID, 'KmsiCheckboxField'))))
    if element.get_attribute('id') == 'piplConsentContinue':
        driver.find_element(By.ID, 'piplConsentContinue').click()
        wait.until(ec.element_to_be_clickable((By.ID, 'idBtn_Back')))
        driver.find_element(By.ID, 'idSIButton9').click()
        wait.until(ec.element_to_be_clickable((By.ID, 'idBtn_Accept')))
        driver.find_element(By.ID, 'idBtn_Accept').click()
    else:
        driver.find_element(By.ID, 'idSIButton9').click()
        wait.until(ec.element_to_be_clickable((By.ID, 'idBtn_Accept')))
        driver.find_element(By.ID, 'idBtn_Accept').click()
    driver.close()


def main():
    with open('outlook.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        rows = [row for row in reader]
        rows_to_delete = []
        flag = True
        for index, row in enumerate(rows):
            mail = row[0]
            password = row[1]
            print('正在注册邮箱：{}，密码：{}'.format(mail, password))
            try:
                register(mail, password)
            except Exception as e:
                print('注册失败：{}'.format(e))
            while True:
                confirm = input("Was operation successful? (y/n/e): ")
                if confirm.lower() == 'y':
                    # write registration details to a csv file
                    with open('ok.csv', 'a', newline='') as csv_file:
                        writer = csv.writer(csv_file)
                        writer.writerow([mail, password])
                    rows_to_delete.append(index)
                    break
                elif confirm.lower() == 'n':
                    break
                elif confirm.lower() == 'e':
                    flag = False
                    break
                else:
                    print("Invalid input. Please enter 'y' or 'n' or 'e'.")
            if not flag:
                break
        # 删除需要删除的行
        for index in reversed(rows_to_delete):
            rows.pop(index)
        # 将修改后的数据写回到CSV文件中
        with open('outlook.csv', 'w', newline='') as okcsvfile:
            writer = csv.writer(okcsvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for row in rows:
                writer.writerow(row)


if __name__ == '__main__':
    main()
