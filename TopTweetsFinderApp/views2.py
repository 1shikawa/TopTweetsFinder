from django.shortcuts import render

# Create your views here.
import tweepy
import pandas as pd
from django.utils.decorators import method_decorator  # @method_decoratorに使用
from django.contrib.auth.decorators import login_required  # @method_decoratorに使用
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.urls import reverse_lazy
from django.views import generic

# from flask import Flask, render_template, request, logging, Response, redirect, flash
from .config import CONFIG

# 各種ツイッターのキーをセット
CONSUMER_KEY = CONFIG["CONSUMER_KEY"]
CONSUMER_SECRET = CONFIG["CONSUMER_SECRET"]
ACCESS_TOKEN = CONFIG["ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = CONFIG["ACCESS_TOKEN_SECRET"]

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


@method_decorator(login_required, name='dispatch')
class TwitterFinderIndex(generic.TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.POST.get('user_id')

        if user_id:
            context['user_id'] = user_id
            context['tweets_df'] = get_tweets_df(user_id)
            context['grouped_df'] = get_grouped_df(tweets_df)
            context['sorted_df'] = get_sorted_df(tweets_df)
            return context

        # else:
        #     return redirect('TopTweetsFinder:TwitterFinderIndex')


def get_tweets_df(user_id):
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
        except Exception as e:
            print(e)
    tweets_df["created_at"] = pd.to_datetime(tweets_df["created_at"])  # 6
    return tweets_df  # 7


def get_profile(user_id):
    user = api.get_user(screen_name=user_id)  # 1
    profile = {  # 2
        "id": user.id,
        "user_id": user_id,
        "image": user.profile_image_url,
        "description": user.description  # 自己紹介文の取得
    }
    return profile  # 3


def get_grouped_df(tweets_df):
    grouped_df = tweets_df.groupby(tweets_df.created_at.dt.date).sum().sort_values(by="created_at", ascending=False)
    return grouped_df


def get_sorted_df(tweets_df):
    sorted_df = tweets_df.sort_values(by="retweets", ascending=False)
    return sorted_df
