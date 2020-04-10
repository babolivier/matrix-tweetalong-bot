import datetime
import time

import twitter
import yaml

with open("config.yaml", "rb") as fp:
    config = yaml.safe_load(fp.read())

api = twitter.Api(
    consumer_key=config["twitter"]["app"]["consumer_key"],
    consumer_secret=config["twitter"]["app"]["consumer_secret"],
    access_token_key=config["twitter"]["app"]["access_token_key"],
    access_token_secret=config["twitter"]["app"]["access_token_secret"],
)

screen_name, slug = config["twitter"]["list_full_name"].split("/")

try:
    timeline = api.GetListTimeline(
        slug=slug,
        owner_screen_name=screen_name,
    )
except twitter.TwitterError as e:
    print("API returned an error: %s" % e.message[0]["message"])
    exit(1)

since_id = timeline[0].id if len(timeline) else None

while True:
    # The /lists/statuses API endpoint is rate-limited to 900 requests every 15min, which
    # amounts to a request every second. Sleeping for a second here is a simple and easy
    # way of avoiding getting rate-limited. It means we're not getting the tweets as soon
    # as possible because the request will take more than 0ms, but we don't really care
    # being a few ms behind.
    time.sleep(1)

    now_iso = datetime.datetime.now().isoformat()
    print("%s - Requesting tweets more recent than %s" % (now_iso, since_id))

    try:
        timeline = api.GetListTimeline(
            slug=slug,
            owner_screen_name=screen_name,
            since_id=since_id,
        )
    except twitter.TwitterError as e:
        print("API returned an error: %s" % e.message[0]["message"])

    if not len(timeline):
        continue

    since_id = timeline[0].id

    for tweet in timeline:
        text = tweet.text  # type: str
        hashtag = config["twitter"].get("hashtag")
        if hashtag and hashtag.lower() not in text.lower():
            continue

        print("%s: %s" % (tweet.user.name, text))
