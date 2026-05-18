import os
import subprocess
import re
import requests
from requests_oauthlib import OAuth1

BASE_URL = "https://rakutenmobilegevanni.github.io/rakutenmobilegevanni/"

ARTICLE_MESSAGES = {
    'campaign.html': '楽天モバイルの従業員紹介キャンペーン🎁\nMNP乗り換えで最大14,000ポイント獲得！申し込み手順・条件を完全解説しました。',
    'mnp.html': '他社から楽天モバイルにMNP乗り換えで最大14,000ポイント🔄\n電話番号そのままで乗り換えできます。ステップ別に手順をまとめました。',
    'family.html': '家族全員で楽天モバイルに乗り換えると通信費が激安に👨‍👩‍👧‍👦\n最強家族割・こども割・青春割を組み合わせると月々¥638〜も可能！',
    'esim.html': 'eSIMなら申し込みから最短3分で開通⚡\n店舗に行く必要なし。楽天モバイルのeSIM設定手順を詳しく解説。',
    'overseas.html': '海外旅行中も追加費用ゼロ🌍\n楽天モバイルは140カ国以上で毎月2GBの海外データが無料。設定はONにするだけ！',
    'plan.html': '楽天モバイルの料金は月¥1,078〜📋\n使った分だけ変わる3段階制で、無制限でも¥3,278。他社との料金比較も解説。',
    'iphone.html': 'MNP乗り換えでiPhone 17eが月1円📱\n実質24円で使える買い替え超トクプログラムの仕組みを詳しく解説。',
    'point.html': '楽天モバイルを契約するだけで楽天市場のポイントが+4倍💎\nSPUの仕組みと楽天経済圏をフル活用する方法をまとめました。',
}

HASHTAGS = "#楽天モバイル #スマホ乗り換え #格安SIM"


def get_new_html_files():
    result = subprocess.run(
        ['git', 'diff', '--name-status', 'HEAD~1', 'HEAD'],
        capture_output=True, text=True
    )
    new_files = []
    for line in result.stdout.split('\n'):
        line = line.strip()
        if line.startswith('A\t') and line.endswith('.html'):
            filename = line[2:].strip()
            if filename not in ('index.html', 'google2a566506e702fdf6.html'):
                new_files.append(filename)
    return new_files


def get_article_title(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
        if match:
            return match.group(1).split('|')[0].strip()
    except Exception:
        pass
    return None


def build_tweet(filename):
    url = BASE_URL + filename

    if filename in ARTICLE_MESSAGES:
        body = ARTICLE_MESSAGES[filename]
    else:
        title = get_article_title(filename) or "新しい記事を公開しました！"
        body = f"【新記事】{title}"

    tweet = f"{body}\n\n{url}\n\n{HASHTAGS}"

    if len(tweet) > 280:
        tweet = f"{body[:220]}...\n\n{url}\n{HASHTAGS}"

    return tweet


def post_tweet(text):
    auth = OAuth1(
        os.environ['X_API_KEY'],
        os.environ['X_API_SECRET'],
        os.environ['X_ACCESS_TOKEN'],
        os.environ['X_ACCESS_TOKEN_SECRET']
    )
    return requests.post(
        'https://api.twitter.com/2/tweets',
        json={'text': text},
        auth=auth
    )


manual_file = os.environ.get('MANUAL_FILE', '').strip()
files_to_post = [manual_file] if manual_file else get_new_html_files()

if not files_to_post:
    print("新規HTMLファイルなし。投稿をスキップします。")
    exit(0)

for filename in files_to_post:
    tweet_text = build_tweet(filename)
    print(f"投稿内容:\n{tweet_text}\n文字数: {len(tweet_text)}\n")

    response = post_tweet(tweet_text)
    if response.status_code == 201:
        print(f"✅ 投稿成功: {filename}")
    else:
        print(f"❌ 投稿失敗: {response.status_code}\n{response.text}")
        exit(1)
