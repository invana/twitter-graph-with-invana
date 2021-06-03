import tweepy
import os
import logging
import sys
from http.client import IncompleteRead

sys.path.append("../")
from invana_twitter.graph import InvanaTwitterGraphBuilder
from invana_engine.gremlin.client import InvanaEngineClient
from invana_twitter.settings import DefaultEntityLabelNames, DefaultRelationShipLabelNames

gremlin_server_url = os.environ.get("GREMLIN_SERVER_URL", "ws://127.0.0.1:8182/gremlin")

consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET")
access_token = os.environ.get("ACCESS_TOKEN")
access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

logging.basicConfig(filename='graph.log', filemode="w", level=logging.DEBUG)


# override tweepy.StreamListener to add logic to on_status
class CustomStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        try:
            graph_builder.process(status)
        except Exception as e:
            print("Entry import ERROR", e)

    def on_error(self, status_code):
        if status_code == 420:
            # returning False in on_error disconnects the stream
            # return False
            return True
        return True
        # returning non-False reconnects the stream, with backoff.

    def on_exception(self, exception):
        """Called when an unhandled exception occurs."""

        """
        except IncompleteRead:
    # Oh well, reconnect and keep trucking
        continue
        
        """
        if isinstance(exception, IncompleteRead):
            return True
        return


invana_client = InvanaEngineClient(gremlin_server_url=gremlin_server_url)
graph_builder = InvanaTwitterGraphBuilder(
    invana_client,
    entity_labels=DefaultEntityLabelNames,
    relationship_labels=DefaultRelationShipLabelNames
)

stream_listener = CustomStreamListener()
stream = tweepy.Stream(auth=api.auth, listener=stream_listener)

stream.filter(track=['COVID', ], is_async=True)
