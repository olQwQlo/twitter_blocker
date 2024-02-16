# Twitterブロックツール

## 使い方
1. このリポジトリをクローンする
2. login_info.jsonを作成する(詳細はsampleを参照)
3. `python3 twitter_block.py`を実行する
4. username_list.txtが生成されるので、ブロックしたいユーザー名を追記する
5. `python3 twitter_block.py`を実行する

## login_info.jsonの書き方
```json
{
    "username": "ユーザー名",
    "password": "パスワード"
}
```

## username_list.txtの書き方
```
ユーザー名
ユーザー名
ユーザー名
```

## 注意
1. このツールは、seleniumを使用しています。  
   APIを使用していないため、Twitterの仕様変更により動作しなくなる可能性があります。  
   また多用するとアカウントを凍結される可能性があります。自己責任でお願いします。
2. 生成されるcsvファイルはブロック済かどうかの判定に使用しています。  
   削除しないでください。  
   ブロック済みをブロック処理の対象から外すので重複した内容を含んでも問題ありません。  
- ※(5000件ほどの動作は確認済ですが、それ以上は未確認です)
- ※(まだTwitterの強制ログアウト対策が甘いのでちょくちょく止まります。ご了承ください)