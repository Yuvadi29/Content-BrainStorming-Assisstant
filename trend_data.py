from pytrends.request import TrendReq

pytrends = TrendReq(hl='en-US', tz=360)

def get_trending_keywords(keyword, timeframe='now 7-d'):
    pytrends.build_payload([keyword], cat=0, timeframe=timeframe, geo='IN', gprop='')
    trends = pytrends.interest_over_time()
    return trends

trends = get_trending_keywords("AI")
print(trends)