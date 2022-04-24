from datetime import datetime


def year(request):
    years = int(datetime.now().strftime('%Y'))
    return {
        'year': years,
    }
