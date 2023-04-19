#seleniumを用いてTwitterにログインする
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Optional

import time
import os
import json
import re
import random

# 概要: Twitterにログインしてブロックを行う
# 200回ブロックしたら5分待機
# 1ブロック処理につき約3秒かかる
# (3sec * 200) / 60 = 10min
# 10min + 5min = 15min/loop
# 1時間に200*4=800ブロック
# 24時間に200*4*24=19200ブロックが理論値
# 実際は途中で強制ログアウトによる再ログインが発生するため
# 理論値よりは少なくなる

# 必要なライブラリとインストール方法
# pip install selenium
# pip install webdriver-manager
# pip install chromedriver-binary


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
    # 小数点だ1位までの分に変換
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
    options = webdriver.ChromeOptions()
    # profileを指定
    # ファイルパスをこのディレクトに変更
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    # 同一ディレクトリのprofileを指定
    # 存在し無い場合は自動で作成される
    profile_path = os.path.join(os.getcwd(), 'profile')
    options.add_argument('--user-data-dir=' + profile_path)
    options.add_argument('--no-first-run')  # 最初の実行時のダイアログを非表示にする
    options.add_argument('--no-default-browser-check')  # デフォルトのブラウザチェックを無効にする
    # エージェントを切り替える
    agents = {
        "Windows_chrome_1": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
        "windows_chrome_2": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
        "windows_edge_1": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.34",
        "windows_edge_2": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.62",
    }
    key_list = list(agents.keys())
    #ランダムなagentをオプションに設定
    #乱数のシードを設定
    random.seed(time.time())
    key = key_list[random.randint(0, len(key_list) - 1)]
    agent = agents[key]
    print("UA: " + agent)
    options.add_argument('--user-agent=' + agent)
    
    driver = webdriver.Chrome(options=options)
    return driver


# ログイン情報を取得
def get_login_info():
    """
    ログイン情報を取得する。

    ログイン情報が保存されているファイル(`login_info.json`)を読み込み、その内容を辞書形式で返す。\n  
    ファイルが存在しない場合は、ユーザーにユーザー名とパスワードを入力してもらい、それらの情報を`login_info.json`に保存した上で返す。

    Returns:
    --------
        dict: ログイン情報(`username`と`password`をキーに持つ辞書)
                ファイルが存在しない場合は、ユーザーが入力したユーザー名とパスワードを保存した辞書

    Raises:
    -------
        Exception: ファイルが存在しているが、読み込みに失敗した場合

    Examples:
    ---------
        >>> get_login_info()
        $ユーザー名を入力してください: testuser
        $パスワードを入力してください: testpassword
        {'username': 'testuser', 'password': 'testpassword'}

    """
    try:
        # ファイルパスをこのディレクトに変更
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        #ファイルが存在しない場合は作成する
        if not os.path.exists('login_info.json'):
            with open('login_info.json', 'w') as f:
                # ログイン情報を入力
                username = input('ユーザー名を入力してください: ')
                password = input('パスワードを入力してください: ')
                login_info = {
                    'username': username,
                    'password': password
                }
                json.dump(login_info, f)
                return login_info
        # ログイン情報を取得
        else:
            with open('login_info.json', 'r') as f:
                login_info = json.load(f)
                return login_info
    except Exception as e:
        print(e)
        return None

# Twitterにログインする
def login_twitter(driver: webdriver.Chrome):
    """
    Twitterにログインする関数。

    Parameters:
    -----------
    driver : webdriver.Chrome
        WebDriverのインスタンス。

    Returns:
    --------
    driver : webdriver.Chrome
        ログイン後のWebDriverのインスタンス。ログインに失敗した場合はNoneを返す。
    """
    try:
        # ログイン情報を取得
        login_info = get_login_info()
        if login_info is None:
            print('ログイン情報の取得に失敗しました')
            return None

        # ログイン情報を取得
        username = login_info['username']
        password = login_info['password']

        # Twitterのログインページを開く
        driver.get('https://twitter.com/home')

        time.sleep(2)
        if driver.current_url == 'https://twitter.com/home':
            # 画面の要素からログインが完了しているか確認
            #「おすすめ」の文字列があるか確認
            pattern = re.compile(r'おすすめ')
            if pattern.search(driver.page_source):
                print('ログインに成功しました')
                return driver
        
        # ログインに失敗している場合
        # ブラウザを初期化して再度ログインを試みる
            # driverのUAを変更する
            driver.quit()
            time.sleep(3)
            driver = init_browser()
            driver.get('https://twitter.com/home')
            time.sleep(2)
            if driver.current_url == 'https://twitter.com/home':
                # 画面の要素からログインが完了しているか確認
                #「おすすめ」の文字列があるか確認
                pattern = re.compile(r'おすすめ')
                if pattern.search(driver.page_source):
                    print('ログインに成功しました')
                    return driver
            elif driver.current_url in 'login':
                
                # ログイン情報を入力
                # ユーザー名入力後でなければパスワードの入力はできない
                #ユーザー名入力
                time.sleep(2)
                username_input = driver.find_element(By.NAME, "text")
                username_input.click()
                username_input.send_keys(username)
                username_input.send_keys(Keys.ENTER)

                #パスワード入力
                time.sleep(2)
                password_input = driver.find_element(By.NAME, "password")
                password_input.click()
                password_input.send_keys(password)
                password_input.send_keys(Keys.ENTER)
            else:
                print('ログインに失敗しました')
                return None

        # ログインに成功したか確認
        time.sleep(2)
        if driver.current_url == 'https://twitter.com/home':
            print('ログインに成功しました')
            return driver
        else:
            print('ログインに失敗しました')
            return None
    except Exception as e:
        print(e)
        return None

#特定のユーザーをブロックする
def block_user(driver:webdriver.Chrome ,username) -> Optional[str]  :
    """
    ツイッターの指定されたユーザーをブロックする。

    Parameters
    ----------
    driver : webdriver.Chrome
        ブラウザのWebDriverオブジェクト
    username : str
        ブロックするユーザーのユーザー名

    Returns
    -------
    Optional[str]
        ブロックの処理結果を "username,date,status" の形式で返す。
        status は以下のいずれかの文字列である。
        - "block success" : ユーザーがブロックされた場合。
        - "already blocked" : 既にユーザーがブロックされていた場合。
        - "not found account" : 指定されたユーザーが存在しなかった場合。
        - "not found page" : 指定されたユーザーのプロフィールページが存在しなかった場合。
        - "suspended" : 指定されたユーザーが凍結されていた場合。
        - "login failed" : ログインに失敗した場合。
    """
    url = 'https://twitter.com/' + username
    driver.get(url)
    time.sleep(2)
    
    try:
        #aria-label="もっと見る"をクリック
        more_look = '[aria-label="もっと見る"]'
        driver.find_element(By.CSS_SELECTOR, more_look).click()
    except:
        #1秒待機してリトライ
        time.sleep(1)
        try:
            #aria-label="もっと見る"をクリック
            more_look = '[aria-label="もっと見る"]'
            driver.find_element(By.CSS_SELECTOR, more_look).click()
        #もっと見るがない場合、凍結、削除、ログアウトのどれかの可能性がある
        except:
            #「再度お試しください」がspanタグに入っているか確認
            pattern = re.compile(r'再度お試しください')
            span_elements = driver.find_elements(By.TAG_NAME, 'span')
            for span_element in span_elements:
                match = re.search(pattern, span_element.text)
                if match:
                    #ブラウザを再起動する
                    driver = login_twitter(driver)
            #「このアカウントは存在しません」がspanタグに入っているか確認
            pattern = re.compile(r'このアカウントは存在しません')
            span_elements = driver.find_elements(By.TAG_NAME, 'span')
            for span_element in span_elements:
                match = re.search(pattern, span_element.text)
                if match:
                    result = f"{username},{time.strftime('%Y/%m/%d %H:%M:%S')},not found account"
                    return result
            #「アカウントは凍結されています」がspanタグに入っているか確認
            pattern = re.compile(r'アカウントは凍結されています')
            span_elements = driver.find_elements(By.TAG_NAME, 'span')
            for span_element in span_elements:
                match = re.search(pattern, span_element.text)
                if match:
                    result = f"{username},{time.strftime('%Y/%m/%d %H:%M:%S')},suspended"
                    return result
            #「このページは存在しません」がspanタグに入っているか確認
            pattern = re.compile(r'このページは存在しません')
            span_elements = driver.find_elements(By.TAG_NAME, 'span')
            for span_element in span_elements:
                match = re.search(pattern, span_element.text)
                if match:
                    result = f"{username},{time.strftime('%Y/%m/%d %H:%M:%S')},not found page"
                    return result
            #上記以外の場合はログアウトしている可能性があるのでログインし直す
            #問題がなければdriverを更新し処理を続行する
            driver = login_twitter(driver)
            if driver is None:
                print('Twitterにログインできませんでした')
                result = f"{username},{time.strftime('%Y/%m/%d %H:%M:%S')},login failed"
                return  result    
    #exceptの処理はここまで

    #ブロックを実行
    try:
        pattern = r'(@.*さんをブロック)'
        span_elements = driver.find_elements(By.TAG_NAME, 'span')
        for span_element in span_elements:
            match = re.search(pattern, span_element.text)
            if match:
                span_element.click()
                span_elements_2 = driver.find_elements(By.TAG_NAME, 'span')
                for span_element_2 in span_elements_2:
                    if span_element_2.text == 'ブロック':
                        span_element_2.click()
                        result = f"{username},{time.strftime('%Y/%m/%d %H:%M:%S')},block success"
                        return result
    except:
        #要素がない場合、すでにブロック済である
        result = f"{username},{time.strftime('%Y/%m/%d %H:%M:%S')},already blocked"
        return result
    return None

# メイン処理
def main():
    try:
        # Twitterにログイン
        driver = init_browser()
        if driver is None:
            print('ブラウザを起動できませんでした')
            return 1
        
        if login_twitter(driver) is None:
            print('Twitterにログインできませんでした')
            return 1
        
        # ログイン後の処理を記述
        # username_listからユーザー名を取得
        username_list = []
        #ファイルの存在チェック
        if not os.path.exists('username_list.txt'):
            print('username_list.txtが存在しません')
            print('空のファイルを作成します')
            with open('username_list.txt', 'w') as f:
                pass #作成のみ
            print('username_list.txtを作成しました')
            print('ブロック対象のusernameを改行区切りで記述してください')
            input('キーを押して終了します')
            return 0
        else: #ファイルが存在する場合
            with open('username_list.txt', 'r') as f:
                for line in f:
                    username_list.append(line.strip())

        # result.csvの存在チェック
        if not os.path.exists('result.csv'):
            print('result.csvが存在しません')
            print('ファイルを作成します\n')
            with open('result.csv', 'w') as f:
                #作成だけするので何もしない
                pass
            print('result.csvを作成しました')
            print('ブロックしたusernameを記録します')
            print('sample: username,date,status')
        # result.csvから除外対象を取得
        # 空でも問題ない
        exclude_list = []
        with open('result.csv', 'r') as f:
            for line in f:
                exclude_list.append(line.split(',')[0])
        # 除外対象をusername_listから除外
        username_list = list(set(username_list) - set(exclude_list))

        #アルファベット順でソート
        username_list.sort()
        #文字数が多い順にソート
        username_list.sort(key=len, reverse=True)

        # ユーザー名を元にユーザーページを開く
        #sample:https://twitter.com/username
        try:
            # 結果を格納する
            result_list = []
            result = ""
            count = 0
            for username in username_list: #ブロック処理のループ
                count += 1
                result = block_user(driver,username)
                if result is not None:
                    result_list.append(result)
                else:
                    #再起動に備えてprofileを利用できるよう、実行中のブラウザを閉じる
                    driver.quit()
                    print(f"{username}のブロックに失敗しました")
                    print("再ログインにも失敗した可能性があります")
                    print("ログイン状態を確認してください")
                    return 1
                if count >= 200:
                    print("200回ブロックしました")
                    #UA変更のためにブラウザを再起動
                    driver.quit()
                    time.sleep(5)
                    driver = init_browser()
                    login_twitter(driver)
                    if driver is None:
                        print('Twitterにログイラできない')
                    # 5分待機
                    #待機時間、再開時刻はwait関数内で表示
                    wait(300)
                #countを空白埋めで3桁にする
                print(f"{str(count).zfill(3)}:{result}")
            #ブロック処理のループ終了
            print("ブロック処理が完了しました")

            return 0
        except KeyboardInterrupt as e:
            driver.quit()
            return 100

        except Exception as e:
            print(e)
            return 1
    finally:
        # 結果をcsvファイルに追記する
        print("結果をresult.csvに書き込みます")
        with open('result.csv', 'a') as f:
            for result in result_list:
                f.write(result+'\n')
        print("書き込み完了")

if __name__ == '__main__':
    retry_count = 0
    while True:
        try:
            ret = main()
            if ret == 0:
                print("main()が正常に終了しました")
                break

            elif ret == 1:
                print("main()が異常終了しました")
                time.sleep(10)

            elif ret == 100: #手動中断は100番台
                print("処理を中断します")
                break
            retry_count = 0

        except KeyboardInterrupt:
            print('処理を終了します')
            break

        except Exception as e:
            #リトライは4回まで
            
            if retry_count < 4:
                retry_count += 1
                print(f'リトライします。{retry_count}回目')

                try:
                    # 5分待機
                    #待機時間、再開時刻はwait関数内で表示
                    wait(300)

                except KeyboardInterrupt:
                    print('処理を中断します')
                    break
            else:
                print(e)
                print('最大リトライ回数を超えました。\n処理を終了します')
                break