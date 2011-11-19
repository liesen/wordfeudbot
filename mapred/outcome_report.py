from google.appengine.ext import db
from google.appengine.ext.mapreduce import operation as op

def process(game):
    yield op.counters.Increment('outcome_%d' % game.outcome)
