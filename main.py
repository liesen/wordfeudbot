#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from datetime import datetime, timedelta
from django.utils import simplejson as json
from google.appengine.api import taskqueue
from google.appengine.api import urlfetch 
from google.appengine.ext import db
from google.appengine.ext import ereporter
from google.appengine.ext import webapp 
from google.appengine.ext.webapp import util
from models import * 
from util import *
from wordfeud import *
from wordfeusk import Wordfeusk
import itertools
import logging as log
import random
import statistics as stats

ereporter.register_logger()

W = login_by_username(config.username, config.password)


class MainHandler(webapp.RequestHandler):
    def get(self):
        stat = dict(statistics=dict(win_count=stats.get_win_count(),
                                    tie_count=stats.get_tie_count(),
                                    lose_count=stats.get_lose_count()))
        self.response.out.write(json.dumps(stat))


class UpdateHandler(webapp.RequestHandler):
    def get(self):
        self.schedule()

    def post(self):
        last_updated = memcache.get('last_updated')
        log.debug('Last update was %s', last_updated or 'never')
        s = W.get_status()
      
        for g in s.games:
            if last_updated is None or g.updated > last_updated:
                log.debug('Game %d updated since last check', g.id)
                taskqueue.add(queue_name='game',
                              url='/game',
                              params=dict(content=json.dumps(g.gamedata)))

        for invite in s.invites_received:
            log.debug('New invite: %s', invite)
            taskqueue.add(queue_name='invite',
                          url='/invite',
                          params=dict(content=json.dumps(invite)))

        countdown = random.randint(2*60, 5*60)
        last_updated = datetime.now()
        next_update = last_updated + timedelta(seconds=countdown)
        self.schedule(countdown)
        log.debug('Next update: %s', next_update)
        memcache.set('last_updated', datetime.now())

    def schedule(self, countdown=0):
        taskqueue.add(queue_name='update',
                      url='/update',
                      countdown=countdown)


class GameHandler(webapp.RequestHandler):
    def post(self):
        status_data = json.loads(self.request.get('content'))
        log.debug('Game on: %s', status_data)
        s = GameStatus(W, status_data)
        g = s.get_game()

        if not g.is_running:
            if g.last_move.get('move_type', '') == 'resign':
                tie = False
                win = g.last_move.get('user_id') != g.me.id
            else:
                oppenents_best_score = max(map(lambda x: x.score, g.opponents))
                tie = g.me.score == oppenents_best_score
                win = not tie and g.me.score > oppenents_best_score 

            log.debug('Game is dead. I %s', 'won :)' if win else 'lost :(')

            if tie:
                stats.increment_tie_count()
            elif win:
                stats.increment_win_count()
            else:
                stats.increment_lose_count()

            # Store game
            db.put_async(FinishedGame(key_name=str(g.id), id=g.id,
                                      updated=g.updated, created=g.created,
                                      players=g.players, move_count=g.move_count,
                                      board=g.board, ruleset=g.ruleset, tiles=g.tiles,
                                      end_game=g.end_game, win=win))

            for player in g.players:
                db.put_async(User(key_name=str(player.get('id')), id=player.get('id'),
                                  username=player.get('username')))

            return

        if not g.is_my_turn():
            log.debug("Not my turn")
            return

        if len(g.tiles) == 0:
            log.debug("Board is empty, playing something stupid")
            g.bot_play()
            return

        player = Wordfeusk()

        for move in itertools.islice(player.get_moves(g), 3):
            log.debug("Wordfeusk suggests '%s' at (%d, %d) %s",
                      move.word, move.x0, move.y0, ("across" if move.direction == Word.ACROSS else "down"))
            try:
                g.play(move.word, move.x0, move.y0, move.direction)
                return
            except:
                continue
        else:
            log.debug("Wordfeusk didn't find a word to play... crap.")

        g.pass_()


class InviteHandler(webapp.RequestHandler):
    def post(self):
        invite = json.loads(self.request.get('content'))
        log.debug('Received invite: %s', invite)

        if invite.get('board_type', 'normal') == 'normal' and invite.get('ruleset', 0) == 4:
            W.accept_invitation(invite.get('id'))
            log.debug('Accepted invitation from %s', invite.get('inviter'))
        else:
            W.reject_invitation(invite.get('id'))
            log.debug('Rejected invitation from %s', invite.get('inviter'))


def main():
    application = webapp.WSGIApplication([('/', MainHandler),
                                          ('/game', GameHandler),
                                          ('/update', UpdateHandler),
                                          ('/invite', InviteHandler)],
                                        debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

