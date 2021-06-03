from invana_twitter.extractor import TweetDataExtractor
from gremlin_python.statics import long
from datetime import datetime
import copy

from invana_twitter.utils import convert_dict_to_vertex


class InvanaGraphBuilderBase:
    extractor = None

    def __init__(self, graph_client, debug=True, entity_labels=None, relationship_labels=None):
        self.graph_client = graph_client
        self.debug = debug

        self.entity_labels = entity_labels
        self.relationship_labels = relationship_labels

    @staticmethod
    def convert_str_to_date(date_time_str):
        return datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f')

    @staticmethod
    def clean_properties_data(properties):
        """
        since JanusGraph doesn't allow id to be set by user, we need to remove it
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
                    # properties_cleaned[k] = self.convert_str_to_date(v)
                elif type(v) is list:
                    pass
                else:
                    properties_cleaned[k] = v

        properties_cleaned['entry_created_at'] = datetime.now()
        return properties_cleaned


class InvanaTwitterGraphBuilder(InvanaGraphBuilderBase):
    """

    Extract user  ["id", "name", "screen_name", "location",
    "description", "verified", "profile_image_url_https"]
    Extract tweet text
    Extract tweet hashtags




    """

    def create_tweet_entity(self):
        if self.debug:
            print("Creating {} entry with text: {}".format(
                self.entity_labels.tweet_label,
                self.extractor.get_tweet_info().get("text")))
        return self.graph_client.vertex.get_or_create(
            label=self.entity_labels.tweet_label,
            properties=self.clean_properties_data(self.extractor.get_tweet_info()))

    def create_user_entity(self):
        if self.debug:
            print("Creating {} entry with screen_name: {}".format(
                self.entity_labels.user_profile_label,
                self.extractor.get_user_info().get("screen_name")))
        return self.graph_client.vertex.create(
            label=self.entity_labels.user_profile_label,
            properties=self.clean_properties_data(self.extractor.get_user_info()))

    def create_tweet_user_mention_entities_and_relationships(self, tweet_instance):

        for user_mention_data in self.extractor.get_user_mention_entities():
            if self.debug:
                mentioned_user = convert_dict_to_vertex(user_mention_data, self.entity_labels.user_profile_label, "id")
                mentioned_user_instance = self.graph_client.vertex.get_or_create(
                    label=mentioned_user['label'],
                    properties=mentioned_user['properties']
                )
                _ = self.create_tweet_user_mention_relationship(tweet_instance=tweet_instance,
                                                                user_mentioned_instance=mentioned_user_instance)

    def create_tweet_user_mention_relationship(self, user_mentioned_instance=None, tweet_instance=None):
        return self.graph_client.edge.create(
            label=self.relationship_labels.has_mentioned_user_in_tweet_label,
            properties=None,
            outv=tweet_instance.id,
            inv=user_mentioned_instance.id
        )

    def create_hashtag_entities_and_relationships(self, tweet_instance=None, user_instance=None):
        for hashtag in self.extractor.get_hashtag_entities():
            if self.debug:
                print("Creating {} entry with name: {}".format(self.entity_labels.hashtag_label, hashtag))
            hashtag_instance = self.graph_client.vertex.get_or_create(
                label=self.entity_labels.hashtag_label,
                properties={"name": hashtag}
            )
            if tweet_instance:
                self.create_hashtag_tweet_relationship(tweet_instance=tweet_instance, hashtag_instance=hashtag_instance)

            if user_instance:
                self.create_hashtag_user_relationship(user_instance=user_instance, hashtag_instance=hashtag_instance)

    def create_hashtag_tweet_relationship(self, tweet_instance=None, hashtag_instance=None):
        return self.graph_client.edge.create(
            label=self.relationship_labels.has_hashtag_label,
            properties=None,
            outv=tweet_instance.id,
            inv=hashtag_instance.id
        )

    def create_hashtag_user_relationship(self, user_instance=None, hashtag_instance=None):
        return self.graph_client.edge.create(
            label=self.relationship_labels.tweeted_about_label,
            properties=None,
            outv=user_instance.id,
            inv=hashtag_instance.id
        )

    def create_tweet_user_relationship(self, user_instance=None, tweet_instance=None):
        return self.graph_client.edge.create(
            label=self.relationship_labels.has_tweeted_label,
            properties=None,
            outv=user_instance.id,
            inv=tweet_instance.id
        )

    def process(self, tweet):
        self.extractor = TweetDataExtractor(tweet)
        urls_data = self.extractor.get_url_entities()
        is_retweet = self.extractor.get_is_retweet()
        print("urls", urls_data)
        print("is_retweet", is_retweet)
        # print("mentions_data", mentions_data)
        if is_retweet is False:
            tweet_instance = self.create_tweet_entity()
            tweet_author_user_instance = self.create_user_entity()

            self.create_tweet_user_relationship(
                user_instance=tweet_author_user_instance,
                tweet_instance=tweet_instance)

            self.create_hashtag_entities_and_relationships(tweet_instance=tweet_instance,
                                                           user_instance=tweet_author_user_instance)

            self.create_tweet_user_mention_entities_and_relationships(tweet_instance)

        if self.debug:
            print("=============================================")
