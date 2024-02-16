from typing import List

from utils.browser import *
from utils.browser import wait

from utils.twitter_access import *
from utils.twitter_automation import *


# メイン処理
def main():
    print('処理を開始します')
    # Twitterにログイン
    print('ブラウザを起動します')
    driver = init_browser()
    print('Twitterにログインします')
    login_twitter(driver)
        
    # ログイン後の処理を記述
    # ブロック対象を収集するためのリンクを入力する
    print('注意：当ツールによって不利益が発生しても責任は負いかねます')
    print('sample: https://twitter.com/username/followers')
    target_link = input('userIDを取得する対象のリンクを入力してください: ')
    driver.get(target_link)
    wait(3)

    #既存のブロックIDリストをファイルから読み込む
    blocked_id_list = []
    try:
        with open('blocked_id_list.txt', 'r') as f:
            blocked_id_list = f.readlines()
    except:
        print('blocked_id_list.txtが存在しません')
        print('新規作成します')
        with open('blocked_id_list.txt', 'w') as f:
            pass
        blocked_id_list = []
    #改行文字を削除
    blocked_id_list = [s.strip() for s in blocked_id_list]

    ids = []
    matches = []
    matches_len_old = 0
    # HTMLの取得、解析、リンクの抽出、リンク配列の結合を行う
    while True:
        # Get the page HTML
        html = driver.page_source
        # extract like
        matches_new = extract_following_user_ids(html)
        matches += matches_new
        ids += [match[1] for match in matches_new if match[2] == "フォロー"]
        # 重複の削除
        matches = list(set(matches))
        # 要素数が変わらない場合は終了
        if matches_len_old == len(matches):
            break
        else:
            matches_len_old = len(matches)
            # Scroll down to bottom
            scroll_down(driver)

    # ブロック済みのIDを除外する
    ids = [user_id for user_id in ids if user_id not in blocked_id_list]
    # 重複の削除
    ids = list(set(ids))

    # Block Process
    # url = "/username"
    for user_id in ids:
        print(user_id)
        target_url = "https://twitter.com" + '/' + user_id
        #ブロック処理
        block_user(driver, target_url)
        #ブロック済みIDをファイルに書き込む
        with open('blocked_id_list.txt', 'a') as f:
            f.write(user_id + '\n')

    wait(3)
    return 0



def handle_interrupt():
    """Handle a KeyboardInterrupt by waiting for a specified time."""
    try:
        print('5分間待機します')
        wait(WAIT_TIME)
    except KeyboardInterrupt:
        print('処理を中断します')
        return False
    return True

# 定数を定義
MAX_RETRIES = 4
WAIT_TIME = 300  # 5 minutes

if __name__ == '__main__':
    retry_count = 0

    while retry_count < MAX_RETRIES:
        try:
            main()
            print("main()が正常に終了しました")
            break

        except KeyboardInterrupt:
            print('処理を終了します')
            break

        except Exception as e:
            print(f'エラーが発生しました: {str(e)}')
            print(f'リトライします。{retry_count + 1}回目')
            if not handle_interrupt():
                break
            retry_count += 1
    else:
        print('最大リトライ回数を超えました。\n処理を終了します')