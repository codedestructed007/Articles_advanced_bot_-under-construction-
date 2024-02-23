from datetime import datetime, timedelta


def datetime_format(value, format="%H:%M %d-%m-%y", reverse = False):
    return value.strftime(format)



def time_ago(date):
    now = datetime.now()
    delta = now - date
    if delta.days > 7:
        weeks = delta.days // 7
        return f"{weeks} {'weeks' if weeks > 1 else 'week'} ago"
    elif delta.days > 0:
        return f"{delta.days} {'days' if delta.days > 1 else 'day'} ago"
    elif delta.seconds // 3600 > 0:
        hours = delta.seconds // 3600
        return f"{hours} {'hours' if hours > 1 else 'hour'} ago"
    elif delta.seconds // 60 > 0:
        minutes = delta.seconds // 60
        return f"{minutes} {'minutes' if minutes > 1 else 'minute'} ago"
    else:
        return "Just now"