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
    #WOEID is on global
    tweets = api.trends_place(1)
    top_ten = []

    temp1_trend = tweets[0]
    temp2_trend = temp1_trend['trends']
    temp_date = temp1_trend['created_at']
    temp = sorted(temp2_trend, key=lambda x: x['tweet_volume'], reverse= True)
    for a in temp[:10]:
        top_ten.append("> " + a['name'])
    p_trends =  "\n".join(top_ten)
    return "*Top 10 World Wide Trending on Twitter* \n" +  p_trends



def send_trending():
    message = trending()
    channel = "assignment1"
    send(message , channel)

def send(message, channel):
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=message
    )

def send_instructions():
    message = "Hi I am *Twitterbot*\n> I can display the top 10 World Wide Trending on Twitter\n> The keyword is: *trending* \n>e.g. _@twitterbot_ *trending*"
    channel = "assignment1"
    send(message, channel)

def p_command(command, channel):

    default_response = "Not sure what you mean. Try *{}*.".format(EXAMPLE_COMMAND)

    response = None
    if command.startswith(EXAMPLE_COMMAND):
        response = trending()
    send(response or default_response, channel)


if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Twitter Bot running and ready!")
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        #schedule to post at 9:30 am
        schedule.every().day.at("9:30").do(send_trending)
        #schedule to post at 9:30 pm
        schedule.every().day.at("21:30").do(send_trending)
        #schedule to post every 10 minutes
        #schedule.every(10).minutes.do(send_trending)
        send_instructions()

    
        while True:
            schedule.run_pending()
            time.sleep(1)
            command, channel = bot_commands(slack_client.rtm_read())
            if command:
                p_command(command.lower(), channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
