"""
基于undetected_edgedriver的ChatGPT ApiKey 提取脚本

Author: Eli Lee
Version: 1.0
Import: chatgpt.csv
Export: api.csv

"""

import csv

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from undetected_edgedriver import Edge, EdgeOptions
from webdriver_manager.microsoft import EdgeChromiumDriverManager


def register(mail, password):
    options = EdgeOptions()
    options.add_argument("--inprivate")  # 启用Edge浏览器无痕模式
    driver = Edge(driver_executable_path=EdgeChromiumDriverManager().install(), options=options)
    wait = WebDriverWait(driver, 60)  # 最长等待时间为60秒
    driver.get('https://platform.openai.com/account/api-keys')
    wait.until(ec.title_contains('OpenAI API'))  # 等待标题包含“OpenAI API”
    driver.find_element(By.XPATH, "//span[@class='btn-label-inner' and contains(text(), 'Log in')]").click()
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
    create_button = wait.until(ec.element_to_be_clickable((By.XPATH, "//button[contains(., 'Create new secret key')]")))
    create_button.click()
    key_input = wait.until(ec.presence_of_element_located(
        (By.XPATH, "//input[@class='text-input text-input-sm text-input-full' and @type='text']")))
    value = key_input.get_attribute('value')
    driver.close()
    return value


def main():
    with open('chatgpt.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        rows = [row for row in reader]
        rows_to_delete = []
        flag = True  # 循环标志
        for index, row in enumerate(rows):
            # 提取邮箱和密码信息
            mail = row[0]
            password = row[1]
            print('正在获取邮箱：{}，密码：{}'.format(mail, password))
            try:
                value = register(mail, password)
            except Exception as e:
                print('获取失败：{}'.format(e))
            while True:
                confirm = input("Was registration successful? (y/n/e): ")
                if confirm.lower() == 'y':
                    with open('api.csv', 'a', newline='') as csv_file:
                        writer = csv.writer(csv_file)
                        writer.writerow([mail, password, value])
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
        with open('chatgpt.csv', 'w', newline='') as chatcsvfile:
            writer = csv.writer(chatcsvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for row in rows:
                writer.writerow(row)


if __name__ == '__main__':
    main()
