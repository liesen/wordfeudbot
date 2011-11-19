from google.appengine.ext import db
from google.appengine.ext.mapreduce import operation as op
from models import JsonProperty
from wordfeud import *
import logging as log


def process(game):
    if game.outcome == 0:
        me = None
        opponents = []

        for p in game.players:
            if p.get('username') == 'ladyboner':
                me = p
            else:
                opponents.append(p)

        if me is None:
            log.debug("didn't find me")
            return

        result = cmp(int(me.get('score')),\
                     max(map(lambda p: int(p.get('score')), opponents)))

        if result != 0:
            log.debug('changing from tie to %d: %s', result, game)
            game.outcome = result
            yield op.db.Put(game)
