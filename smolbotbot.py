import robots
import robotdata
import search
import twitter
import schedule
import time
import random


running = True

responded_tweets = []
responded_dms = []

admin_ids = ["4494622517"]


saved_responded_tweets = open("state/responded-tweets.txt", "r")
for tweet_id in saved_responded_tweets:
    try:
        responded_tweets.append(int(tweet_id.strip()))
    except ValueError:
        continue
saved_responded_tweets.close()
del saved_responded_tweets
print("Loaded responded tweets: " + str(responded_tweets))

saved_responded_dms = open("state/responded-dms.txt", "r")
for dm_id in saved_responded_dms:
    responded_dms.append(dm_id.strip()) # DM ids are stored as strings for convenience
saved_responded_dms.close()
del saved_responded_dms
print("Loaded responded dms: " + str(responded_dms))


greeting_phrases = [""]
introduction_phrases = [""]


def tweet_next_robot():
    global greeting_phrases, introduction_phrases
    robot = robots.next_daily_robot()
    name = robot["name"]
    date = time.strftime("%d/%m/%y")
    greeting = random.choice(greeting_phrases)
    introduction = random.choice(introduction_phrases)
    link = "https://twitter.com/smolrobots/status/" + str(robot["tweet_id"])
    text = date + "\n" + greeting + " " + introduction + " " + name + "!" + link
    twitter.tweet(text)


def check_new_robots():
    recent_tweets = twitter.recent_tweets("smolrobots", 10800)
    print(str(len(recent_tweets)) + " recent tweets found from @smolrobots, looking for new robots")
    for tweet in recent_tweets:
        if robotdata.generate_robot_data(tweet.full_text, tweet.id):
            print("Registered a new robot")


def check_tweets():
    global responded_tweets
    mentions = twitter.mentions(20, 10800, responded_tweets)
    for mention in mentions:
        search_result = search.search(mention.full_text)
        twitter.reply(mention, search_result)
        print("Sent a reply")

        responded_tweets.append(mention.id)
        if len(responded_tweets) > 20:
            responded_tweets = responded_tweets[1:]


def check_direct_messages():
    global responded_dms, admin_ids
    dms = twitter.direct_messages(7200, responded_dms)
    for dm in dms:
        text = dm["message_create"]["message_data"]["text"]
        sender_id = dm["message_create"]["sender_id"]

        response = ""

        if sender_id in admin_ids and text.startswith("$"):
            response = do_command(text[1:].strip())

        else:
            response = search.search(text).replace("\'", "’").replace("\"", "”")

        if twitter.send_direct_message(sender_id, response):
            responded_dms.append(dm["id"])
            print("Sent a DM")

            responded_dms.append(dm["id"])
            if len(responded_dms) > 20:
                responded_dms = responded_dms[1:]
        else:
            print("DM failed to " + sender_id)


def do_command(command):
    global running
    if command == "ldrobots":
        loaded = robots.reload()
        return "Loaded " + str(loaded) + " robots"
    elif command == "ldphrases":
        load_phrases()
        return "Reloaded phrases"
    elif command == "stop":
        running = False
        return "Stopping at end current loop"
    return "Unrecognised command"


def load_phrases():
    global greeting_phrases, introduction_phrases

    greetings_file = open("data/greetings.txt", "r")
    greeting_phrases = [line.strip() for line in greetings_file]
    greetings_file.close()

    if not greeting_phrases:
        greeting_phrases = ["[INTERNAL ERROR]"]

    intros_file = open("data/botd-intros.txt", "r")
    introduction_phrases = [line.strip() for line in intros_file]
    intros_file.close()

    if not introduction_phrases:
        introduction_phrases = ["[INTERNAL ERROR]"]


def close_bot():
    global responded_tweets, responded_dms

    tweets_file = open("state/responded-tweets.txt", "w")
    for tweet_id in responded_tweets:
        tweets_file.write(str(tweet_id))
    tweets_file.close()
    print("Saved responded tweet ids")

    dms_file = open("state/responded-dms.txt", "w")
    for dm_id in responded_dms:
        dms_file.write(dm_id)
    dms_file.close()
    print("Saved responded dm ids")


load_phrases()

schedule.every().day.at("07:00").do(tweet_next_robot)
schedule.every().hour.do(check_new_robots)
schedule.every().minute.do(check_direct_messages)
schedule.every(15).seconds.do(check_tweets)


while running:
    try:
        time.sleep(1)
        schedule.run_pending()
    except KeyboardInterrupt:
        print("Keyboard interrupt, stopping")
        break
    except:
        print("An uncaught error occurred in schedule loop")

close_bot()
print("Goodbye!")
