from gremlin_python.statics import long


class TwitterDataExtractor:

    def __init__(self, tweet):
        self.tweet = tweet

    @property
    def tweet_json(self):
        return self.tweet._json

    def get_tweet_id(self):
        return self.tweet.id

    def get_is_retweet(self):
        return self.tweet.retweeted

    def get_user_info(self):
        return self.tweet_json['user']

    def get_url_entities(self):
        return [url['expanded_url'] for url in self.tweet_json['entities']['urls']]

    def get_hashtag_entities(self):
        return [hashtag['text'] for hashtag in self.tweet_json['entities']['hashtags']]

    def get_user_mention_entities(self):
        return [
            {"name": mention['name'], "id": int(mention['id'])}
            for mention in
            self.tweet_json['entities']['user_mentions']
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
