from datetime import datetime, timedelta

from information_extraction.globals import MONTHS

def iso(date):
    day, month_str, year, hour, minute = date.groups()
    day = int(day)
    month = MONTHS[month_str.lower()]
    year = int(year)
    
    if hour and minute:
        hour = int(hour)
        minute = int(minute)
        if hour == 24:
            hour = 0
            dt = datetime(year, month, day, hour, minute) + timedelta(days=1)
        else:
            dt = datetime(year, month, day, hour, minute)
    else:
        dt = datetime(year, month, day, 0, 0)
    
    return dt.strftime("%Y-%m-%dT%H:%M")

def concat_articles(pdf, chapter, article_range):
    text = ""

    for article_num in article_range:
        article_str = str(article_num)
        article = pdf[chapter]["articles"][article_str]
        text += f"Artículo {article_str}. {article['title']}\n{article['content']}\n\n"
    
    return text