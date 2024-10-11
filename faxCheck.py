import os
import sys
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import time as t
import requests
import json
import pandas as pd
from bs4 import BeautifulSoup
with open('C:\\Users\\USER\\ve_1\\DB\\3loginInfo.json', 'r', encoding='utf-8') as f:
    login_info = json.load(f)
with open('C:\\Users\\USER\\ve_1\\DB\\6faxInfo.json', 'r',encoding='utf-8') as f:
    fax_info = json.load(f)
works_login = pd.Series(login_info['nFax'])
bot_info = pd.Series(login_info['nFaxbot'])
check_bot = pd.Series(login_info['emailbot'])
fax = pd.DataFrame(fax_info)
def getHome(page):
    #로그인 정보입력(아이디)
    id_box = page.find_element(By.XPATH,'//input[@id="userId"]')
    id = works_login['id']
    ActionChains(page).send_keys_to_element(id_box, '{}'.format(id)).perform()
    t.sleep(1)
    #로그인 정보입력(비밀번호)
    password_box = page.find_element(By.XPATH,'//input[@id="userPwd"]')
    loginbtn = page.find_element(By.XPATH, '//button[@id="btnLogin"]')
    password = works_login['pw']
    ActionChains(page).send_keys_to_element(password_box, '{}'.format(password)).click(loginbtn).perform()
    t.sleep(1)
    page.get("https://www.enfax.com/fax/view/receive")
#엔팩스 메일 확인
def newFax(page):
    page.refresh()
    t.sleep(2)
    faxSoup = BeautifulSoup(page.page_source,'html.parser')
    newfax = faxSoup.find('span', attrs={'class':'state_box stt_notread'})
    #요소 검증
    if newfax != None:
        #수신확인
        if newfax.get_text()=="안읽음":
            faxNumber = faxSoup.find('div', attrs={'class':'t_row stt_notread faxReceiveBoxListRow'}).get('data-send-fax-number')
            if faxNumber in fax['faxNumber'].tolist():
                tell = f"신규 팩스 수신, 확인필요\n팩스번호 : {faxNumber}\n원천사 : {fax[fax['faxNumber'] == faxNumber]['원천사'].values}"
                #텔레그램 전송
                requests.get(f"https://api.telegram.org/bot{bot_info['token']}/sendMessage?chat_id={bot_info['chatId']}&text={tell}")
                t.sleep(2)
            else:
                tell = f"신규 팩스 수신, 확인필요\n팩스번호 : {faxNumber}\n원천사 : 확인불가"
                #텔레그램 전송
                requests.get(f"https://api.telegram.org/bot{bot_info['token']}/sendMessage?chat_id={bot_info['chatId']}&text={tell}")
                t.sleep(2)
    else:pass
def main():
    reset_time = t.time()
    while True:
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument('--disable-gpu')
            options.add_argument("--disable-javascript")
            options.add_argument('--disable-extensions')
            options.add_argument('--blink-settings=imagesEnabled=false')
            driver = webdriver.Chrome(options=options)
            driver.get("https://www.enfax.com/fax/view/receive")
            getHome(driver)
            browser_runtime = 600
            max_runtime = 1800
            start_time = t.time()
            while t.time()-start_time < browser_runtime:
                print(int(t.time()-start_time))
                newFax(driver)
                t.sleep(10)
            requests.get(f"https://api.telegram.org/bot{bot_info['token']}/sendMessage?chat_id={check_bot['chatId']}&text=브라우저_재시작")
            t.sleep(2)
            driver.quit()                
            if t.time()-reset_time >= max_runtime:
                requests.get(f"https://api.telegram.org/bot{bot_info['token']}/sendMessage?chat_id={check_bot['chatId']}&text=스크립트_재시작")
                t.sleep(2)
                os.execl(sys.executable, sys.executable, *sys.argv)
            else:pass
        except Exception as e:
            requests.get(f"https://api.telegram.org/bot{bot_info['token']}/sendMessage?chat_id={check_bot['chatId']}&text=오류발생:{e}")
            t.sleep(2)
            os.execl(sys.executable, sys.executable, *sys.argv)
if __name__ == "__main__":main()