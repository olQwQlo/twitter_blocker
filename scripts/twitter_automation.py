import re
import time
from typing import Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup


#特定のユーザーをブロックする
def block_user(driver: webdriver.Chrome, url: str) -> Optional[str]:
    """
    Twitter上の指定されたユーザーをブロックする。

    Parameters
    ----------
    driver : webdriver.Chrome
        Twitterにログインして操作を行うためのWebDriverインスタンス。
    username : str
        ブロックするユーザーのユーザー名。

    Returns
    -------
    Optional[str]
        ブロック操作の結果を "username, date, status" の形式の文字列で返す。
        status は以下のいずれかの文字列を含む:
        - "block success" : ユーザーが成功的にブロックされた場合。
        - "already blocked" : ユーザーがすでにブロックされていた場合。
        - "not found account" : 指定したユーザー名のアカウントが存在しない場合。
        - "not found page" : 指定したユーザーのプロフィールページが存在しない場合。
        - "suspended" : 指定したユーザーのアカウントが凍結されている場合。
        - "login failed" : ログインに失敗した場合。

    Raises
    ------
    Exception
        "再度お試しください"メッセージが表示された場合、再ログインが必要と判断し、例外をスローする。

    Notes
    -----
    指定したユーザー名のアカウントが存在しない、または既にブロックされている場合、ブロック操作は行われず、
    その情報がステータスとして返される。また、"再度お試しください"メッセージが表示された場合、ブラウザの
    状態が不適切であると判断し、再ログインが必要であることを示すために例外をスローする。
    """
    driver.get(url)
    #url_sample:https://twitter.com/username
    username = url.split('/')[-1]
    time.sleep(1)
    
    try:
        #aria-label="もっと見る"をクリック
        more_look = '[aria-label="もっと見る"]'
        driver.find_element(By.CSS_SELECTOR, more_look).click()
    except:
        #もっと見るがない場合、凍結、削除、ログアウトのどれかの可能性がある
        #「再度お試しください」がspanタグに入っているか確認
        pattern = re.compile(r'再度お試しください')
        span_elements = driver.find_elements(By.TAG_NAME, 'span')
        for span_element in span_elements:
            match = re.search(pattern, span_element.text)
            if match:
                # エラーを返す
                raise Exception('再ログインが必要です')
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
        # 上記以外の場合はログアウトしている可能性があるのでエラーを返す
        raise Exception('再ログインが必要です')
    #exceptの処理はここまで

    #ブロックを実行
    try:
        #「@usernameさんをブロック」をクリック
        time.sleep(0.5)
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


def extract_follower_links(html_content: str) -> list:
    """
    Extract follower links from the provided HTML content.
    
    Parameters:
    - html_content: str - The HTML content to extract links from.
    
    Returns:
    - list - A list of unique follower links.
    """
    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract the section with aria-label "タイムライン: フォロワー"
    follower_section_element = soup.find(attrs={"aria-label": "タイムライン: フォロワー"})
    like_section_element = soup.find(attrs={"aria-label": "タイムライン: いいねしたユーザー"})
    section_element = []
    # If the section is not found, return an empty list
    if not follower_section_element:
        if not like_section_element:
            return []
        else:
            section_element = like_section_element
    else:
        section_element = follower_section_element
    
    # Remove all <span> tags
    for span_tag in section_element.find_all('span'):
        span_tag.decompose()
    
    # Extract all <a> tags within the section
    a_tags_in_target_section = section_element.find_all('a')
    
    # Extract href attributes and remove duplicates
    home_links = list(set([a.get('href') for a in a_tags_in_target_section if a.has_attr('href')]))
    
    # Filter out non-account links
    home_links = [link for link in home_links if not link.startswith('https://')]
    
    return home_links

pattern_find_name_id_profile = r'([^@]+)@([\w.]+?)(ブロック中|フォロー)クリックして'
def extract_following_user_ids(html_content: str) -> list:
    """
    Extract user IDs of the users with the status "フォロー" from the provided HTML content.
    
    Parameters:
    - html_content: str - The HTML content to extract user IDs from.
    
    Returns:
    - list - A list of user IDs with the status "フォロー".
    """
    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract the section with aria-label "タイムライン: フォロワー"
    follower_section_element = soup.find(attrs={"aria-label": "タイムライン: フォロワー"})
    like_section_element = soup.find(attrs={"aria-label": "タイムライン: いいねしたユーザー"})
    section_element = []
    # If the section is not found, return an empty list
    if not follower_section_element:
        if not like_section_element:
            return []
        else:
            section_element = like_section_element
    else:
        section_element = follower_section_element
    
    # Extract user info using the regular expression
    matches = re.findall(pattern_find_name_id_profile, section_element.text)
    
    # Return user IDs with the status "フォロー"
    return matches