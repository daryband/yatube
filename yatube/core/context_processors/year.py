import datetime as dt


def year(request):
    """Adds current year variable"""
    return {
        'year': dt.datetime.now().year
    }
