import asyncio
import datetime
import time

import nio
import twitter
import yaml

with open("config.yaml", "rb") as fp:
    config = yaml.safe_load(fp.read())

screen_name, slug = config["twitter"]["list_full_name"].split("/")


def init_twitter():
    cli = twitter.Api(
        consumer_key=config["twitter"]["app"]["consumer_key"],
        consumer_secret=config["twitter"]["app"]["consumer_secret"],
        access_token_key=config["twitter"]["app"]["access_token"],
        access_token_secret=config["twitter"]["app"]["access_token_secret"],
    )

    timeline = cli.GetListTimeline(
        slug=slug,
        owner_screen_name=screen_name,
    )
    since_id = timeline[0].id if len(timeline) else None
    return cli, since_id


async def init_matrix():
    cli = nio.AsyncClient(
        homeserver=config["matrix"]["hs_url"],
        user=config["matrix"]["mxid"],
    )

    await cli.login(config["matrix"]["password"])

    # If the user isn't in the room, join it.
    room_id = config["matrix"]["room_id"]
    res = await cli.joined_rooms()
    if room_id not in res.rooms:
        await cli.join(room_id)

    return cli


async def loop():
    twitter_client, since_id = init_twitter()
    matrix_client = await init_matrix()

    while True:
        # The /lists/statuses Twitter API endpoint is rate-limited to 900 requests
        # every 15min, which amounts to a request every second. Sleeping for a second
        # here is a simple and easy way of avoiding getting rate-limited. It means
        # we're not getting the tweets as soon as possible because the request will
        # take more than 0ms, but we don't really care being a few ms behind.
        time.sleep(1)

        now_iso = datetime.datetime.now().isoformat()
        print("%s - Requesting tweets more recent than %s" % (now_iso, since_id))

        # Get the latest tweets in the list. If an error happened, loop over it.
        try:
            timeline = twitter_client.GetListTimeline(
                slug=slug,
                owner_screen_name=screen_name,
                since_id=since_id,
            )
        except twitter.TwitterError as e:
            print("Twitter API returned an error: %s" % e.message[0]["message"])
            continue

        # If no tweet was returned, loop over.
        if not len(timeline):
            continue

        since_id = timeline[0].id

        # Reverse the list so we're processing tweets in chronological order.
        timeline.reverse()

        # Iterate over the tweets.
        for tweet in timeline:
            text = tweet.text  # type: str

            # If a hashtag was provided and the tweet doesn't include it, pass over this
            # tweet.
            hashtag = config["twitter"].get("hashtag")
            if hashtag and hashtag.lower() not in text.lower():
                continue

            # Send the tweet as a notice to the Matrix room.
            message = "%s: %s" % (tweet.user.name, text)
            await matrix_client.room_send(
                room_id=config["matrix"]["room_id"],
                message_type="m.room.message",
                content={
                    "msgtype": "m.notice",
                    "body": message,
                },
            )

asyncio.get_event_loop().run_until_complete(loop())
