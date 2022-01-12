import tweepy
import os
from twitter_graph_with_invana.graph_process import TwitterGraphBuilder

consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET")
access_token = os.environ.get("ACCESS_TOKEN")
access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")


class CustomStreamListener(tweepy.Stream):

    def on_status(self, status):
        graph_builder = TwitterGraphBuilder()
        graph_builder.store_tweet(status)

    def on_error(self, status_code):
        if status_code == 420:
            # returning False in on_error disconnects the stream
            # return False
            return True
        return True
        # returning non-False reconnects the stream, with backoff.


stream_listener = CustomStreamListener(
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret,
)
stream_listener.filter(track=['COVID', ], threaded=True)
