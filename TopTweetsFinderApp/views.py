from django.shortcuts import render

# Create your views here.
import tweepy
import pandas as pd
from django.views import generic
from . import config

# 各種Twitterーのキーをセット
CONSUMER_KEY = config.CONFIG["CONSUMER_KEY"]
CONSUMER_SECRET = config.CONFIG["CONSUMER_SECRET"]
ACCESS_TOKEN = config.CONFIG["ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = config.CONFIG["ACCESS_TOKEN_SECRET"]

# Tweepy
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

# APIインスタンスを作成
api = tweepy.API(auth)

# Viewの処理
columns = [
    "tweet_id",
    "created_at",
    "text",
    "fav",
    "retweets"
    # ,"url"
]


class TwitterFinderIndex(generic.TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 入力フォームからuser_id取得
        user_id = self.request.GET.get('user_id')
        # columns定義したDataFrameを作成
        tweets_df = pd.DataFrame(columns=columns)  # 1
        # Tweepy,Statusオブジェクトから各値取得
        for tweet in tweepy.Cursor(api.user_timeline, screen_name=user_id, exclude_replies=True).items():  # 2
            try:
                if not "RT @" in tweet.text:  # 3
                    se = pd.Series([  # 4
                        tweet.id,
                        tweet.created_at,
                        tweet.text.replace('\n', ''),
                        tweet.favorite_count,
                        tweet.retweet_count
                        # ,tweet.url
                    ]
                    , columns
                    )
                tweets_df = tweets_df.append(se, ignore_index=True)  # 5
            except tweepy.TweepError as e:
                print(e)
        # created_atを日付型に変換
        tweets_df["created_at"] = pd.to_datetime(tweets_df["created_at"])  # 6

        grouped_df = tweets_df.groupby(tweets_df.created_at.dt.date).sum().sort_values(by="created_at", ascending=False)
        # リツイート＆いいね数が多い順にソート
        sorted_df = tweets_df.sort_values(["retweets","fav"], ascending=False)[:50]

        # Userオブジェクトからプロフィール情報取得
        user = api.get_user(screen_name=user_id)  # 1
        profile = {  # 2
            "id": user.id,
            "user_id": user_id,
            "user_name":user.name,
            "followers_count":user.followers_count,
            "image": user.profile_image_url,
            "description": user.description  # 自己紹介文の取得
        }
        # created_atをキーに昇順ソート
        sorted_df_created_at = sorted_df.sort_values('created_at', ascending=True)

        if user_id:
            context['user_id'] = user_id
            context['tweets_df'] = tweets_df
            context['grouped_df'] = grouped_df
            context['sorted_df'] = sorted_df
            context['profile'] =profile

            context['sorted_df_created_at'] = sorted_df_created_at
            context['sorted_df'] = sorted_df
            context['profile'] =profile
        else:
            print('userが存在しません')
        return context

    # else:
    #     return redirect('TopTweetsFinder:TwitterFinderIndex')








