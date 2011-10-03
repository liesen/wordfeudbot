from google.appengine.api import memcache
from google.appengine.ext import db
import random


class CounterShard(db.Model):
    name = db.StringProperty(required=True)
    num_shards = db.IntegerProperty(required=True, default=10)


class Counter(db.Model):
    name = db.StringProperty(required=True)
    count = db.IntegerProperty(required=True, default=0)


def get(counter_name):
    total = memcache.get(counter_name)

    if total is None:
        total = 0

        for counter in Counter.all().filter('name = ', counter_name):
            total += counter.count

        memcache.add(counter_name, total, 60 * 15)

    return total

def incr(counter_name):
    shards = CounterShard.get_or_insert(counter_name, name=counter_name)

    def txn():
        shard_index = random.randint(0, shards.num_shards)
        shard_name = counter_name + str(shard_index)
        counter = Counter.get_by_key_name(shard_name)

        if counter is None:
          counter = Counter(key_name=shard_name, name=counter_name)

        counter.count += 1
        counter.put()

    db.run_in_transaction(txn)
    memcache.incr(counter_name)

