from google.appengine.ext import db
from django.utils import simplejson as json


class JsonProperty(db.TextProperty):
    def validate(self, value):
        return value

    def get_value_for_datastore(self, model_instance):
        result = super(JsonProperty, self).get_value_for_datastore(model_instance)
        text = json.dumps(result, separators=(',', ':'))
        return db.Text(text)

    def make_value_from_datastore(self, value):
        try:
            value = json.loads(str(value))
        except:
            pass

        return super(JsonProperty, self).make_value_from_datastore(value)


class FinishedGame(db.Model):
    id = db.IntegerProperty(required=True)
    updated = db.DateTimeProperty(required=True)
    created = db.DateTimeProperty(required=True)
    players = JsonProperty()
    move_count = db.IntegerProperty()
    board = db.IntegerProperty()
    ruleset = db.IntegerProperty()
    tiles = JsonProperty() 
    end_game = db.IntegerProperty()
    win = db.BooleanProperty()


class User(db.Model):
    id = db.IntegerProperty(required=True)
    username = db.StringProperty(required=True)

