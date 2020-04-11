# Matrix Tweetalong

A simplistic Matrix bot for Twitter-backed watchalongs.

![screenshot](https://user-images.githubusercontent.com/5547783/79041841-4306a600-7bf3-11ea-9838-4a02a65495ae.png)

## How it works

Every second, the bot polls new tweets from a given Twitter list and
sends them to a given Matrix room. If a hashtag is also provided, only
tweets containing the hashtag (regardless of case) will be sent.

## Install

```bash
# Clone the repository
git clone https://github.com/babolivier/matrix-tweetalong-bot.git
cd matrix-tweetalong-bot
# Create a virtualenv
virtualenv -p python3 env
. env/bin/activate
# Install the dependencies
pip install -r requirements.txt
```

## Configure

Copy [`config.sample.yaml`](/config.sample.yaml) into `config.yaml`.
This sample configuration includes comments documenting how to configure
the bot.

## Run

```bash
python main.py
```
