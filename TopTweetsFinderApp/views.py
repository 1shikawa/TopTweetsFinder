from django.shortcuts import render

# Create your views here.
import tweepy
import pandas as pd

# from flask import Flask, render_template, request, logging, Response, redirect, flash
from . import config

# 各種ツイッターのキーをセット
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
]


class TwitterFinderIndex(generic.TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.GET.get('user_id')

        tweets_df = pd.DataFrame(columns=columns)  # 1
        for tweet in tweepy.Cursor(api.user_timeline, screen_name=user_id, exclude_replies=True).items():  # 2
            try:
                if not "RT @" in tweet.text:  # 3
                    se = pd.Series([  # 4
                        tweet.id,
                        tweet.created_at,
                        tweet.text.replace('\n', ''),
                        tweet.favorite_count,
                        tweet.retweet_count
                    ]
                        , columns
                    )
                tweets_df = tweets_df.append(se, ignore_index=True)  # 5
            except tweepy.TweepError as e:
                print(e)
        tweets_df["created_at"] = pd.to_datetime(tweets_df["created_at"])  # 6
        grouped_df = tweets_df.groupby(tweets_df.created_at.dt.date).sum().sort_values(by="created_at", ascending=False)
        sorted_df = tweets_df.sort_values(by="retweets", ascending=False)

        user = api.get_user(screen_name=user_id)  # 1
        profile = {  # 2
            "id": user.id,
            "user_id": user_id,
            "image": user.profile_image_url,
            "description": user.description  # 自己紹介文の取得
        }

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








