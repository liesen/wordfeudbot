# -*- coding: UTF-8 -*-
import logging as log
import urllib
import wordfeud

try:
    import json
    import urllib2
    appengine = False
except ImportError:
    from django.utils import simplejson as json
    from google.appengine.api import urlfetch
    from google.appengine.api import memcache
    appengine = True


class Wordfeusk(object):
    def __init__(self):
        pass

    def get_moves(self, game):
        return self._get_moves(game.tiles, game.me.rack)

    def _get_moves(self, tiles, rack):
        form_data = dict(letters=self._format_letters(rack),
                         board=self._format_board(tiles))
        log.debug("Attempting Wordfeusk with %s" % form_data)
        data = urllib.urlencode(form_data)

        url = "http://www.wordfeusk.se/feusk"

        if appengine:
            resp = urlfetch.fetch(url, payload=data, method='POST', deadline=30)
            words = json.loads(resp.content)
        else:
            req = urllib2.Request(url, data)
            resp = urllib2.urlopen(req)
            words = json.load(resp)

        log.debug("%s" % words)
        words = words.get('words', [])

        for x, y, across, word, points in words:
            direction = wordfeud.Word.ACROSS if across else wordfeud.Word.DOWN
            yield wordfeud.Word(word, x, y, direction)
        else:
            log.debug("No words in reply")

    def _format_letters(self, rack):
        letter = lambda x: '*' if len(x) == 0 else x.lower()
        return ''.join(map(letter, rack)).encode('utf-8')

    def _format_board(self, tiles):
        board = dict([((x, y), letter) for x, y, letter, blank in tiles])

        def get(x, y):
            return board.get((x, y), ' ').lower().encode('utf-8')

        lines = map(lambda y: ''.join(map(lambda x: get(x, y), range(0, 15))),
                    range(0, 15))
        return json.dumps(lines, ensure_ascii=False) 


