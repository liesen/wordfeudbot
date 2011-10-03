from datetime import timedelta


def format_timedelta(delta):
    hours, seconds = divmod(delta.seconds, 3600)
    minutes = seconds // 60

    if delta.days:
        return '%d %s' % (delta.days, pluralize('day', delta.days))

    if hours:
        return '%d %s and %d %s' % (hours, pluralize('hour', hours), minutes, pluralize('minute', minutes))

    if minutes:
        return '%d %s' % (minutes, pluralize('minute', minutes))

    return '%d %s' % (delta.seconds, pluralize('second', delta.seconds))

def pluralize(singular, count=0):
    try:
        size = len(count)
    except:
        size = int(count)

    return singular if size == 1 else singular + 's'

