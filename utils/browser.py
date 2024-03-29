import time
import os
import sys
import random
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


def wait(seconds):
    """
    指定した秒数待機する

    Args:
        seconds (int): 待機する秒数

    Raises:
        KeyboardInterrupt: キーボードからの割り込みが発生した場合

    Returns:
        None

    Example:
        >>> wait(600)
        # 10分待機します
        # 再開時刻は23:30:00です
        # 再開します

    Dependencies:
        - time
    """
    # 小数点第1位までの分に変換
    minutes = round(seconds / 60, 1)
    print(str(minutes) + '分待機します')
    print(f'再開時刻は{time.strftime("%H:%M:%S", time.localtime(time.time() + seconds))}です')
    time.sleep(seconds)
    print('再開します')

    #ブラウザを初期化する
def init_browser():
    """
    ブラウザを初期化する
    Returns:
        selenium.webdriver.chrome.webdriver.WebDriver: ブラウザのウィンドウ
    Example:
        >>> driver = init_browser()
    Dependencies:
        - os
        - random
        - time
        - selenium.webdriver.chrome.webdriver.WebDriver
    """
    print("ブラウザを初期化します")
    # ランダムにエージェントを切り替える
    print("UAを設定します")
    agents = {
        "Windows_chrome_1": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
        "windows_chrome_2": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
        "windows_edge_1": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.34",
        "windows_edge_2": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.62",
    }
    key_list = list(agents.keys())
    random.seed(time.time())
    key = key_list[random.randint(0, len(key_list) - 1)]
    agent = agents[key]
    print("UA: " + agent)

    # profileを指定
    # ファイルパスを変更
    application_path = os.path.abspath(sys.argv[0]) 
    profile_path = os.path.abspath(os.path.join(application_path, '..\\profile'))
    print('profile_path: ' + profile_path)

    print('optionを設定します')
    options = webdriver.ChromeOptions()
    options.add_argument('--user-data-dir=' + profile_path)
    options.add_argument('--no-first-run')  # 最初の実行時のダイアログを非表示にする
    options.add_argument('--no-default-browser-check')  # デフォルトのブラウザチェックを無効にする
    options.add_argument('--user-agent=' + agent)
    options.add_argument('--verbose')


    service = Service(executable_path=ChromeDriverManager().install())
    print('service: ' + str(service._path))
    driver = webdriver.Chrome(service=service, options=options)

    return driver


def scroll_to_end(driver):
    """
    ページを最下部までスクロールする。

    Parameters:
        driver : webdriver.Chrome
            Twitterにログインして操作を行うためのWebDriverインスタンス。

    Returns:
        None
    """
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # ページの最下部までスクロール
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # 新しいコンテンツの読み込みを待つ
        time.sleep(1)
        # ページの新しい高さを取得
        new_height = driver.execute_script("return document.body.scrollHeight")
        # 高さが変わっていない場合、スクロールを終了
        if new_height == last_height:
            break
        last_height = new_height

def scroll_down(driver):
    """
    ページを一定量スクロールする。

    Parameters:
        driver : webdriver.Chrome
            Twitterにログインして操作を行うためのWebDriverインスタンス。
    
    Returns:
        None
    """
    driver.execute_script("window.scrollBy(0, 1000);")
    time.sleep(1)