import tweepy
import os
from graph_process import TwitterGraphBuilder

consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET")
access_token = os.environ.get("ACCESS_TOKEN")
access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

graph_builder = TwitterGraphBuilder()


# override tweepy.StreamListener to add logic to on_status
class CustomStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        graph_builder.process(status)

    def on_error(self, status_code):
        if status_code == 420:
            # returning False in on_error disconnects the stream
            return False
        # returning non-False reconnects the stream, with backoff.


stream_listener = CustomStreamListener()
stream = tweepy.Stream(auth=api.auth, listener=stream_listener)

stream.filter(track=['COVID-19'], is_async=True)
