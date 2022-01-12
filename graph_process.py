import pprint

from gremlin_python.statics import long
import logging
from datetime import datetime
import copy
from .models import UserProfile, Tweet, HashTag, UsedHashTag, HasHashTag, HasTweeted

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

    def create_tweet(self, extractor):
        # create Tweet
        tweet_data = extractor.get_tweet_info()
        serialised_tweet_data = self.validate_properties_data(tweet_data, Tweet)
        tweet_obj = Tweet.objects.create(**serialised_tweet_data)
        print("======tweet_obj", tweet_obj)
        return tweet_obj

    def create_user(self, extractor):
        # create UserProfile
        user_data = extractor.get_user_info()
        serialised_user_data = self.validate_properties_data(user_data, UserProfile)
        user_obj = UserProfile.objects.search(has__twitter_id=serialised_user_data["twitter_id"]).to_list()
        if user_obj.__len__() > 0:
            user_obj = UserProfile.objects.create(**serialised_user_data)
        return user_obj

    @staticmethod
    def create_hash_tag(extractor):
        # create has tags
        hashtags_data = extractor.get_hashtag_entities()
        hashtag_objects = [HashTag.objects.get_or_create(text=hashtag) for hashtag in hashtags_data]
        return hashtag_objects

    def extract_entities(self, tweet):
        extractor = TwitterDataExtractor(tweet)

        is_retweet = extractor.get_is_retweet()
        # print("tweet", tweet_data)
        # print("hashtags", hashtags_data)
        # print("mentions", mentions_data)
        # print("urls", urls_data)
        print("is_retweet", is_retweet)
        if is_retweet is False:
            # mentions_data = extractor.get_user_mention_entities()
            # urls_data = extractor.get_url_entities()

            tweet_object = self.create_tweet(extractor)
            user_object = self.create_user(extractor)
            hashtag_objects = self.create_hash_tag(extractor)

            HasTweeted.objects.create(user_object.id, tweet_object.id)
            for hashtag_object in hashtag_objects:
                HashTag.objects.create(tweet_object.id, hashtag_object.id)
                UsedHashTag.objects.create(user_object.id, hashtag_object.id)

    def store_tweet(self, event):
        self.extract_entities(event)
        print("==========================")
