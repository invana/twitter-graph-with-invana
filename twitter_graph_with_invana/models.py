from invana_py import InvanaGraph
from invana_py.ogm.models import VertexModel, EdgeModel
from invana_py.ogm.fields import StringProperty, IntegerProperty, DoubleProperty, DateTimeProperty, BooleanProperty
from datetime import datetime

graph = InvanaGraph("ws://localhost:8182/gremlin", call_from_event_loop=False)


class UserProfile(VertexModel):
    graph = graph
    properties = {
        "user_id": DoubleProperty(),
        "name": StringProperty(),
        "screen_name": StringProperty(),
        "location": StringProperty(allow_null=True),
        "description": StringProperty(allow_null=True),
        "lang": StringProperty(allow_null=True),
        "profile_background_image_url_https": StringProperty(allow_null=True),
        "profile_image_url_https": StringProperty(allow_null=True),
        "verified": BooleanProperty(default=False),
        "followers_count": IntegerProperty(),
        "friends_count": IntegerProperty(),
        "listed_count": IntegerProperty(),
        "favourites_count": IntegerProperty(),
        "statuses_count": IntegerProperty(),
        "created_at": DateTimeProperty(),
        "entry_created_at": DateTimeProperty(default=lambda: datetime.now()),
        # geo: GeoProperty(allow_null=True)
        # coordinates: GeoProperty(allow_null=True)
    }


class Tweet(VertexModel):
    graph = graph
    properties = {
        "tweet_id": DoubleProperty(),
        "text": StringProperty(),
        "lang": StringProperty(),
        "timestamp_ms": StringProperty(),
        "is_retweet": BooleanProperty(),
        "created_at": DateTimeProperty(),
        "entry_created_at": DateTimeProperty(default=lambda: datetime.now()),
    }


class HashTag(VertexModel):
    graph = graph
    properties = {
        "text": StringProperty(),
        "entry_created_at": DateTimeProperty(default=lambda: datetime.now()),
    }


class HasTweeted(EdgeModel):
    # for UserProfile - Tweet
    graph = graph
    properties = {
        "entry_created_at": DateTimeProperty(default=lambda: datetime.now()),
    }


class HasHashTag(EdgeModel):
    # for Tweet - Hashtag
    graph = graph
    properties = {
        "entry_created_at": DateTimeProperty(default=lambda: datetime.now()),
    }


class UsedHashTag(EdgeModel):
    # for UserProfile - Hashtag
    graph = graph
    properties = {
        "entry_created_at": DateTimeProperty(default=lambda: datetime.now()),
    }
