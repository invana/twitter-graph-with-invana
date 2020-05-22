import pprint

from gremlin_python.statics import long
from invana.client import GraphClient
import logging
from datetime import datetime
import copy

logging.basicConfig(filename='graph.log', filemode="w", level=logging.DEBUG)


class DataExtractor:

    def __init__(self, tweet):
        pprint.pprint(tweet)
        self.tweet = tweet

    def get_tweet_id(self):
        return self.tweet.id

    def get_is_retweet(self):
        return self.tweet.retweeted

    def get_user_info(self):
        return self.tweet._json['user']

    def get_url_entities(self):
        return [url['expanded_url'] for url in self.tweet._json['entities']['urls']]

    def get_hashtag_entities(self):
        return [hashtag['text'] for hashtag in self.tweet._json['entities']['hashtags']]

    def get_user_mention_entities(self):
        return [
            {"name": mention['name'], "id": int(mention['id'])}
            for mention in
            self.tweet._json['entities']['user_mentions']
        ]

    def get_tweet_extended_entities(self):
        return self.tweet['extended_entities']

    def get_tweet_info(self):
        return {
            "id": long(self.get_tweet_id()),
            "text": self.tweet.text,
            "is_retweet": self.get_is_retweet(),
            "created_at": self.tweet.created_at
        }


class TwitterGraphBuilder:
    """

    Extract user  ["id", "name", "screen_name", "location",
    "description", "verified", "profile_image_url_https"]
    Extract tweet text
    Extract tweet hashtags



    """
    graph_client = GraphClient("ws://127.0.0.1:8182/gremlin")

    def convert_to_date(self, date_time_str):
        return datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f')

    def validate_properties_data(self, properties):
        """
        since janusgraph does allow id to be set by user, we need to remove it
        or convert into specific format https://github.com/JanusGraph/janusgraph/issues/45

        :param properties:
        :return:
        """

        properties = copy.copy(properties)
        if "id" in properties:
            properties["_id"] = long(properties['id'])
            del properties['id']

        properties_cleaned = {}
        for k, v in properties.items():
            # delete any properties with value None
            if v is not None:
                if k in ["created_at", "updated_at"]:
                    pass
                    # properties_cleaned[k] = self.convert_to_date(v)
                else:
                    properties_cleaned[k] = v

        return properties_cleaned

    def extract_entities(self, tweet):
        extractor = DataExtractor(tweet)
        user_data = extractor.get_user_info()
        tweet_data = extractor.get_tweet_info()
        hashtags_data = extractor.get_hashtag_entities()
        mentions_data = extractor.get_user_mention_entities()
        urls_data = extractor.get_url_entities()
        is_retweet = extractor.get_is_retweet()
        print("user", user_data)
        print("tweet", tweet_data)
        print("hashtags", hashtags_data)
        print("mentions", mentions_data)
        print("urls", urls_data)
        print("is_retweet", is_retweet)
        if is_retweet is False:
            tweet_obj = self.graph_client.vertex.create(
                label="Tweet",
                properties=self.validate_properties_data(tweet_data)
            )
            print("======tweet_obj", tweet_obj)
            print("read one user_data", user_data)

            user_obj = self.graph_client.vertex.read_one(
                label="TwitterProfile",
                query={"_id": self.validate_properties_data(user_data)["_id"]}
            )
            if user_obj is None:
                print("-----creating TwitterProfile", self.validate_properties_data(user_data))
                user_obj = self.graph_client.vertex.create(
                    label="TwitterProfile",
                    properties=self.validate_properties_data(user_data)
                )


            print("======user_obj", user_obj)
            tweet_user_relationship = self.graph_client.edge.create(
                label="has_tweeted",
                # properties={"distance_in_kms": 384400},
                outv={"query": {"id": user_obj['id']}},
                inv={"query": {"id": tweet_obj['id']}}
            )

            for hashtag in hashtags_data:
                hashtag_obj = self.graph_client.vertex.get_or_create(
                    label="HashTag",
                    query={"name": hashtag}
                )
                tweet_hashtag_relationship = self.graph_client.edge.create(
                    label="has_hashtag",
                    # properties={"distance_in_kms": 384400},
                    outv={"query": {"id": tweet_obj['id']}},
                    inv={"query": {"id": hashtag_obj['id']}}
                )
                user_hashtag_relationship = self.graph_client.edge.create(
                    label="writes_about",
                    # properties={"distance_in_kms": 384400},
                    outv={"query": {"id": user_obj['id']}},
                    inv={"query": {"id": hashtag_obj['id']}}
                )

    def add_event_to_event_store(self, tweet):
        pass

    def process(self, event):
        self.add_event_to_event_store(event)
        self.extract_entities(event)
        print("==========================")
