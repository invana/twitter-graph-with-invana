import pprint

from gremlin_python.statics import long
import logging
from datetime import datetime
import copy
from .models import UserProfile, Tweet, HashTag, UsedHashTag, HasHashTag

from data_extractor import TwitterDataExtractor

logging.basicConfig(filename='graph.log', filemode="w", level=logging.DEBUG)


class TwitterGraphBuilder:
    """

    Extract user  ["id", "name", "screen_name", "location",
    "description", "verified", "profile_image_url_https"]
    Extract tweet text
    Extract tweet hashtags



    """

    @staticmethod
    def convert_to_date(date_time_str):
        return datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f')

    def validate_properties_data(self, properties, model):
        """
        since JanusGraph does not allow id to be set by user, we need to remove it
        or convert into other key. Refer https://github.com/JanusGraph/janusgraph/issues/45

        :param properties:
        :return:
        """
        model_property_keys = list(model.properties.keys())
        properties = copy.copy(properties)
        if "id" in properties:
            properties["twitter_id"] = long(properties['id'])
            del properties['id']

        properties_cleaned = {}
        for k, v in properties.items():
            # delete any properties that are not in model.properties
            if k in model_property_keys:
                if k in ["created_at", "updated_at"]:
                    properties_cleaned[k] = self.convert_to_date(v)
                else:
                    properties_cleaned[k] = v
        return properties_cleaned

    def extract_entities(self, tweet):
        extractor = TwitterDataExtractor(tweet)

        is_retweet = extractor.get_is_retweet()
        # print("tweet", tweet_data)
        # print("hashtags", hashtags_data)
        # print("mentions", mentions_data)
        # print("urls", urls_data)
        print("is_retweet", is_retweet)
        if is_retweet is False:

            # create Tweet
            tweet_data = extractor.get_tweet_info()
            serialised_tweet_data = self.validate_properties_data(tweet_data, Tweet)
            tweet_obj = Tweet.objects.create(**serialised_tweet_data)
            print("======tweet_obj", tweet_obj)

            # create UserProfile
            user_data = extractor.get_user_info()
            serialised_user_data = self.validate_properties_data(user_data, UserProfile)
            user_obj = UserProfile.objects.search(has__twitter_id=serialised_user_data["twitter_id"]).to_list()
            if user_obj.__len__() > 0:
                user_obj = UserProfile.objects.create(**serialised_user_data)

            hashtags_data = extractor.get_hashtag_entities()
            mentions_data = extractor.get_user_mention_entities()
            urls_data = extractor.get_url_entities()

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
