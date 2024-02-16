import os
import json
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

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
        
        elif driver.current_url == 'https://twitter.com/i/flow/login':
            
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

            #「認証コード」の文字列があるか確認
            pattern = re.compile(r'認証コード')
            if pattern.search(driver.page_source):
                # 認証コードを入力
                print('認証コードを入力してください')
                auth_code = input('認証コードを入力してください: ')
                auth_code_input = driver.find_element(By.NAME, "text")
                auth_code_input.click()
                auth_code_input.send_keys(auth_code)
                auth_code_input.send_keys(Keys.ENTER)
                
        elif driver.current_url == 'https://twitter.com/account/access':
            # reCAPTCHA認証にリダイレクトさせられた場合
            print('reCAPTCHA認証にリダイレクトされました')
            print('手動で認証を行ってください')
            input('認証を完了させ、いずれかのキーを押してください')
            if driver.current_url == 'https://twitter.com/home':
                print('ログインに成功しました')
                return driver
            else:
                print('認証が未完了です')
                print('もう一度待機します。ホーム画面に遷移してから、いずれかのキーを押してください')
                input('認証を完了させ、いずれかのキーを押してください')
                if driver.current_url == 'https://twitter.com/home':
                    print('ログインに成功しました')
                    return driver
            print('認証に失敗しました')
            print('ブラウザを終了します')
            driver.quit()
            return None
        else:
            print('不明なURLです')
            print(f'URL: {driver.current_url}')

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
