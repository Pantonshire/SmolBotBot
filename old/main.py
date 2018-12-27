from old import botlookup as search
import twitter
import codecs
import time
import re
import tweepy

robotfile = codecs.open("data/old-robot-table.csv", "r", "utf-8")
robots = [tuple(line.strip().split(",")) for line in robotfile]
robotfile.close()

responded_to = []
responded_dms = []


def save_robot(robot):
    outputfile = codecs.open("old-robot-table.csv", "a", "utf-8")
    outputfile.write(",".join([str(item) for item in robot]) + "\n")
    outputfile.close()
    print("Saved new robot: #" + str(robot[0]) + " " + robot[1])


def tweet_indexed(tweet_id):
    global robots
    for robot in robots:
        if int(robot[2]) == tweet_id:
            print("Already indexed " + robot[1])
            return True
    return False


def check_new_robots():
    global robots
    recent = twitter.recent_tweets("smolrobots", 10800)
    for tweet in recent:
        tweet_id = tweet.id
        if not(tweet_indexed(tweet_id)):
            tweet_text = tweet.text
            search = re.search("(^|\s)\d+\)\ [\w|\-]+bot\w*", tweet_text, re.IGNORECASE)
            if search != None:
                parts = search.group().strip().split(") ")
                number = parts[0].strip()
                name = parts[1].strip()
                new_robot = (number, name, tweet_id)
                print("Found new robot: #" + str(number) + " " + name)
                robots.append(new_robot)
                save_robot(new_robot)


def check_requests():
    global robots, responded_to
    mentions = twitter.mentions(20, 7200, responded_to)
    for mention in mentions:
        responded_to.append(mention.id)
        search_result = search.search(robots, mention.text)
        twitter.reply(mention, search_result)
        

def check_dms():
    global robots, responded_dms
    dms = twitter.direct_messages(7200, responded_dms)
    for dm in dms:
        responded_dms.append(dm["id"])
        text = dm["message_create"]["message_data"]["text"]
        search_result = search.search(robots, text).replace("\'", "’").replace("\"", "”")
        #print(search_result)
        sender_id = dm["message_create"]["sender_id"]
        if twitter.send_direct_message(sender_id, search_result):
            responded_dms.append(dm["id"])
            print("Sent a DM")
        else:
            print("DM failed to " + sender_id)


i = 0
while True:
  try:
     i += 1
     # Should be called once per hour
     if i >= 240:
        check_new_robots()
        i = 0
     # Should be called once per minute
     if i % 4 == 0:
        check_dms()
     check_requests()
     time.sleep(15)
  except tweepy.TweepError:
     time.sleep(30)
     continue

    