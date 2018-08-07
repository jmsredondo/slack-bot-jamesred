import time
import re
import schedule
from slackclient import SlackClient
import tweepy
from config import SLACK_API_TOKEN, bot_token, consumer_key, consumer_secret, access_token, access_token_secret


slack_client = SlackClient(bot_token)
starterbot_id = None
RTM_READ_DELAY = 1  # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "trending"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

def bot_commands(slack_events):

    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None


def mention(message_text):

    matches = re.search(MENTION_REGEX, message_text)
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def trending():
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    dictionary = {}
    tweets = api.trends_place(1187115)

    temp1_trend = tweets[0]
    temp2_trend = temp1_trend['trends']
    for trend in temp2_trend:
        dictionary[trend['tweet_volume']] =  "> " + trend['name']
    sorted_trend = [value for (key, value) in sorted(dictionary.items(), reverse=True)]
    top_ten = sorted_trend[:10]
    p_trends =  "\n".join(top_ten)
    return "*Top 10 Trending on Twitter*\n" +  p_trends



def send():
    message = trending()
    chan = "general"
    slack_client.api_call(
        "chat.postMessage",
        channel=chan,
        text=message
    )

def p_command(command, channel):

    default_response = "Not sure what you mean. Try *{}*.".format(EXAMPLE_COMMAND)

    response = None
    if command.startswith(EXAMPLE_COMMAND):
        response = trending()

    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )


if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Twitter Bot running and ready!")
    starterbot_id = slack_client.api_call("auth.test")["user_id"]
    schedule.every().day.at("9:30").do(send)
    schedule.every().day.at("21:30").do(send)

    
    while True:
        schedule.run_pending()
        time.sleep(1)
        command, channel = bot_commands(slack_client.rtm_read())
        if command:
            p_command(command.lower(), channel)
        time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
