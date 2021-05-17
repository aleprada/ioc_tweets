#!/usr/bin/env python
from pymisp import PyMISP,MISPEvent, PyMISPError
from tweepy import OAuthHandler
from time import sleep
from datetime import date
import configparser
import argparse
import tweepy
import json
import os


def config_parser(section, key):
    config = configparser.ConfigParser()
    try:
        config.read(os.path.join(os.path.dirname(__file__)+"/config/config.ini"))
        result = config.get(section, key)
        return result
    except config.NoOptionError:
        raise Exception("There was a problem with configuration file. The key does not exist.")
    except config.NoSectionError:
        raise Exception("There was a problem with configuration file. The key does not exist.")


def load_file(filename):
    with open(os.path.dirname(__file__)+"/config/"+filename, "r") as ins:
        array = []
        for line in ins:
            array.append(line.strip())
        ins.close()
    return array


def misp_connection(url, misp_key, proxy_usage):
    try:
        if proxy_usage:
            proxies = {}
            proxies ["http"] = config_parser("misp","http")
            proxies ["https"] = config_parser("misp","https")
            misp = PyMISP(url, misp_key, False, 'json', proxies=proxies)
        else:
            misp = PyMISP(url, misp_key, False, 'json',None)
    except PyMISPError:
        print("\t [!] Error connecting to MISP instance. Check if your MISP instance it's up!")
        return None

    return misp


def create_event(misp):
    event = MISPEvent()
    event.distribution = 0
    event.threat_level_id = 1
    event.analysis = 0
    return event


def send2misp(tweet, proxy_usage):
    url = config_parser("misp", "url")
    api_key = config_parser("misp", "api_key")
    misp = misp_connection(url, api_key, proxy_usage)
    event = create_event(misp)
    event.add_tag("tweet-ioc")
    event.info = "[Tweet] New IoCs discovered on Twitter"
    event.add_attribute('twitter-id', tweet.user.screen_name)
    event.add_attribute('other', tweet.text)
    event.add_attribute('other', tweet.created_at.strftime("%Y-%m-%dT%H:%M:%S"))
    if 'hashtags' in tweet.entities:
        for h in tweet.entities['hashtags']:
            event.add_attribute('other', h['text'])
    if 'urls' in tweet.entities:
        for h in tweet.entities['urls']:
            event.add_attribute('link', h['url'])
    event = misp.add_event(event, pythonify=True)
    print("\t [*] Event with ID " + str(event.id) + " has been successfully stored.")


def init_twitter_config():
    consumer_key = config_parser('twitter_api', 'consumer_key')
    consumer_secret = config_parser('twitter_api', 'consumer_secret')
    access_token = config_parser('twitter_api', 'access_token')
    access_secret = config_parser('twitter_api', 'access_secret')
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    return auth


def filter_tweets(tweet_str):
    alert = False
    filters = load_file("filters.txt")
    for f in filters:
        if f.lower() in tweet_str.lower():
            alert = True
            break
    return alert


def print_tweet(tweet):
    print("\t[!] Tweet by " + tweet.user.screen_name + " on " + str(tweet.created_at) + ":")
    if 'hashtags' in tweet.entities:
        for h in tweet.entities['hashtags']:
            print("\t[!] #"+h['text'])
    if 'urls' in tweet.entities:
        for h in tweet.entities['urls']:
            print("\t[!] url: " + h['url'])
    print("\t[!]Tweet content:")
    print("\t\t" + tweet.text.replace("\n", "\n\t\t"))


def search_on_twitter(api, alerts):
    tweets_list = []
    keywords = load_file("keywords.txt")
    today = date.today()
    for k in keywords:
        sleep(5)
        print("[+] Tweet containing: " + k)
        tweets = tweepy.Cursor(api.search, q=k, lang="en", since= today).items(100)
        if alerts:
            for tweet in tweets:
                if filter_tweets(tweet.text):
                    print_tweet(tweet)
                    tweets_list.append(tweet)
        else:
            for tweet in tweets:
                print_tweet(tweet)
                tweets_list.append(tweet)
    print("[*] Number of tweets gathered: " + str(len(tweets_list)))
    return tweets_list


def start_listen_twitter():
    auth = init_twitter_config()
    api = tweepy.API(auth, wait_on_rate_limit=True)
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--alerts", help=" Filter tweets gathered in case of matach with any "
                                               "keywords of your list.",
                                               action="store_true")
    parser.add_argument("-m", "--misp", help="Send IoCs from Twitter to MISP", action="store_true")
    parser.add_argument("-p", "--proxy", help="Set a proxy for sending the alert to your MISP instance..",
                        action="store_true")
    args = parser.parse_args()
    proxy_usage = False
    print("[*] Searching IoC's on Twitter:")

    if args.alerts:
        print("[*] Checking if the tweets gathered contain any keyword of your list.")
        tweets = search_on_twitter(api, True)
        if args.misp:
            if args.proxy:
                proxy_usage = True
            print("[*] Sending alerts to MISP")
            for t in tweets:
                send2misp(t, proxy_usage)
    else:
        search_on_twitter(api, False)


if __name__ == '__main__':
    start_listen_twitter()

