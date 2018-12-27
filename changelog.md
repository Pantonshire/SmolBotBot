# Changelog

## Version 2.0.2
- Increased the maximum size of the blacklist lists from 20 items to 1024 items.
- The date and time of sending a tweet or direct message is now written to a log file.

## Version 2.0.1
- Fixed an issue in which responded tweet and dm ids were written to a single line in their respective text files.

## Version 2.0.0
- Improved robot data collection algorithm. The image URL, image alt text, mentions and hashtags are now collected and stored.
- Tags are now generated for each robot, based on nouns and adjectives appearing in the text and alt text.
- Implemented a daily robot feature; a different small robot is tweeted each day at 07:00 GMT.
- Random selection of robots is now biased to prevent the same robot from being selected twice.
- Improved search algorithm; as well as searching by name and number, robots can now be searched by their tags.
- Removed "amalgam" search method since it was returning many unexpected results.
- Up to 4 small robots may be returned per request.
- Scheduling is now done using [schedule](https://github.com/dbader/schedule) module.
- A few different admin commands may be now be supplied to the robot via direct messages.
- Robots are now indexed in dictionaries by name, number, tags and mentions for quick lookups.
- Replied tweet and DM ids are now saved to disk so that restarting does not cause the bot to re-reply to recent requests.
- Tweets and DMs containing the word "ignore" in parentheses, along with any other characters inside the parentheses, will now be ignored by the bot.