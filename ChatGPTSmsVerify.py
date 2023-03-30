"""
基于undetected_edgedriver的ChatGPT自动手机号验证脚本。
selenium不能通过cf盾，使用undetected_edgedriver可以绕过cf盾。
偶尔会弹出cf盾验证，需要手动验证。

Author: Eli Lee
Version: 1.0
Import: ok.csv
Export: chatgpt.csv

"""

import csv

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from smsactivate.api import SMSActivateAPI
from undetected_edgedriver import Edge, EdgeOptions
from webdriver_manager.microsoft import EdgeChromiumDriverManager


def register(mail, password, sa, number):
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
    driver.implicitly_wait(20)
    driver.find_element(By.ID, 'idSIButton9').click()

    wait.until(ec.element_to_be_clickable((By.ID, 'KmsiCheckboxField')))
    driver.find_element(By.ID, 'idSIButton9').click()

    element = wait.until(ec.element_to_be_clickable((By.XPATH,
                                                     '//button[@class="btn btn-full btn-lg btn-filled btn-primary '
                                                     'onb-uinfo-continue" and @type="submit"]')))
    element.click()
    wait.until(ec.element_to_be_clickable((By.XPATH,
                                           '//button[@class="btn btn-full btn-lg btn-filled btn-primary '
                                           'onb-send-code-primary" and @type="submit"]')))
    driver.find_element(By.XPATH, '//div[@class=" css-12wvehw-control"]').click()
    element = wait.until(ec.element_to_be_clickable((By.ID, 'react-select-2-option-103')))
    element.click()
    driver.find_element(By.XPATH,
                        '//input[@class="text-input text-input-lg text-input-full" and @type="text"]').send_keys(
        str(number['phone'])[2:])
    whatsapp_no_element = wait.until(
        ec.element_to_be_clickable((By.CSS_SELECTOR, "label[for='whatsapp-opt-in-radio-no']")))
    whatsapp_no_element.click()
    send_sms_element = wait.until(ec.element_to_be_clickable((By.XPATH,
                                                              '//button[@class="btn btn-full btn-lg btn-filled '
                                                              'btn-primary onb-send-code-primary" and '
                                                              '@type="submit"]')))
    send_sms_element.click()
    wait.until(ec.element_to_be_clickable((By.XPATH, '//div[@class="link-style onb-back-btn"]')))
    while sa.getStatus(id=number['activation_id'])[7:9] != 'OK':
        print('Waiting for code...')
    driver.find_element(By.XPATH,
                        '//input[@class="text-input text-input-lg text-input-full" and @type="text"]').send_keys(
        sa.getStatus(number['activation_id'])[10:])
    wait.until(ec.title_contains('New chat'))  # 等待标题包含“New chat”
    sa.setStatus(id=number['activation_id'], status=3)  # 3: 接收下一个号码
    driver.close()


def main():
    sa = SMSActivateAPI('')  # 需要更改为自己的API key
    # Get number
    number = sa.getNumber(service='dr', country=6)  # dr: openai 6: 印度尼西亚
    success_count = 0

    with open('ok.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        rows = [row for row in reader]
        rows_to_delete = []
        flag = True  # 循环标志
        for index, row in enumerate(rows):
            # 提取邮箱和密码信息
            mail = row[0]
            password = row[1]
            print('正在注册邮箱：{}，密码：{}'.format(mail, password))
            try:
                register(mail, password, sa, number)
            except Exception as e:
                print('注册失败：{}'.format(e))
            while True:
                confirm = input("Was registration successful? (y/n/e/r): ")
                if confirm.lower() == 'y':
                    success_count += 1
                    if success_count >= 2:
                        sa.setStatus(id=number['activation_id'], status=6)  # 6: 释放号码
                        number = sa.getNumber(service='dr', country=6)  # dr: openai 6: 印度尼西亚
                        success_count = 0
                    # write registration details to a csv file
                    with open('chatgpt.csv', 'a', newline='') as csv_file:
                        writer = csv.writer(csv_file)
                        writer.writerow([mail, password])
                    rows_to_delete.append(index)
                    break
                elif confirm.lower() == 'n':
                    break
                elif confirm.lower() == 'e':
                    flag = False
                    break
                elif confirm.lower() == 'r':
                    number = sa.getNumber(service='dr', country=6)  # dr: openai 6: 印度尼西亚
                    break
                else:
                    print("Invalid input. Please enter 'y' or 'n' or 'e' or 'r'.")
            if not flag:
                break
        # 删除需要删除的行
        for index in reversed(rows_to_delete):
            rows.pop(index)
        # 将修改后的数据写回到CSV文件中
        with open('ok.csv', 'w', newline='') as okcsvfile:
            writer = csv.writer(okcsvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for row in rows:
                writer.writerow(row)


if __name__ == '__main__':
    main()
