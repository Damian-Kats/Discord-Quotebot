import json
import sys
import datetime
import fileinput
import random
from discord.ext.commands import Bot
from discord.ext import commands as c


my_bot = Bot(command_prefix="!")


# Check if author is owner of bot
def is_owner():
    return c.check(lambda ctx: ctx.message.author.id == "")


# method for adding quote and keyword info to the quotes.txt file
async def add_quote(name, keyword, text, data):
    now = datetime.datetime.now()  # get date information
    year = now.strftime("%Y")  # get year as a string
    key_value = {keyword: [text, year]}
    data[name].update(key_value)


# add new keyword to list
def add_keyword_to_file(name, keyword):
    for line in fileinput.input('keyword_list.txt', inplace=1):
        if line.startswith(name):
            print('{0} {1}'.format(line.rstrip('\n'), keyword))
        else:
            sys.stdout.write(line)


# delete keyword from list
async def delete_keyword(*args):
    f = open('keyword_list.txt', 'r')
    lines = f.readlines()
    f.close()
    new_lines = []
    if len(args) == 1:
        for line in lines:
            new_lines.append(' '.join([word for word in line.split() if word != args[0]]))
    elif len(args) == 2:
        for line in lines:
            if line.startswith(args[1]):
                new_lines.append(' '.join([word for word in line.split() if word != args[0]]))
            else:
                new_lines.append(' '.join([word for word in line.split()]))
    else:
        return await my_bot.say("Error deleting keyword")
    f = open("keyword_list.txt", 'w')
    for line in new_lines:
        f.write("{}\n".format(line))
    f.close()


"""Events"""


#Use this for reading and responding to messages
#@my_bot.event
#async def on_message(message):


"""Commands"""


@my_bot.command(name="add", aliases=["new", "create"])
async def new_quote(name, keyword, body: str):
    """Add new quote to database"""
    infile = open('quotes.txt', 'r')  # open text file containing quote info
    quotes = json.load(infile)  # load quote info to a json format
    infile.close()
    if name in quotes:  # check if user is in the database
        if body not in quotes[name].values():  # check if quote is already in the database
            if keyword not in quotes[name]:  # check if keyword is already used
                await add_quote(name, keyword, body, quotes)
                add_keyword_to_file(name, keyword)
                with open('quotes.txt', 'w') as outfile:
                    json.dump(quotes, outfile)
                    for name, key in quotes.items():
                        if keyword in key:
                            user = name[:]
                            date = quotes[user][keyword][1]
                            output = "```" + '"' + quotes[user][keyword][
                                0] + '"' + "\n" + " -" + " " + user + "," + " " + date + "```"
                            return await my_bot.say(output)
                # return await my_bot.say("Quote added.")
            else:
                return await my_bot.say("That keyword is already being used.")
        else:
            return await my_bot.say("That quote already exists.")
    else:
        return await my_bot.say("That is not a follower of the Weregoat.")


@my_bot.command(name="quote", aliases=["show", "display"])
async def display_quote(*args):
    """Display quote"""
    with open('quotes.txt', 'r') as infile:
        quotes = json.load(infile)
        if len(args) == 1:  # if only keyword given as an argument then display first quote with that keyword
            for name, key in quotes.items():
                if args[0] in key:
                    user = name[:]
                    date = quotes[user][args[0]][1]
                    output = "```" + '"' + quotes[user][args[0]][0] + '"' + "\n" + " -" + " " + user + "," + " " + date + "```"
                    return await my_bot.say(output)
        elif len(args) == 2:  # if both keyword and name given as arguments then display that specific quote
            for name, key in quotes.items():
                if args[0] in key and name == args[1]:
                    user = name[:]
                    date = quotes[user][args[0]][1]
                    output = "```" + '"' + quotes[user][args[0]][0] + '"' + "\n" + " -" + " " + user + "," + " " + date + "```"
                    return await my_bot.say(output)
        else:
            return await my_bot.say("You entered the wrong number of arguments.")

        return await my_bot.say("There is no quote represented by that keyword.")


@my_bot.command(name="random", aliases=["any"])
async def display_random(*args):
    """Display a random quote"""
    with open('quotes.txt', 'r') as infile:
        quotes = json.load(infile)
        if len(args) == 1:  # if name is given as argument then display random quote from that person
            for name, values in quotes.items():
                if name == args[0]:
                    keyword, quote = random.choice(list(values.items()))
                    date = quote[1]
                    output = "```" + '"' + quote[0] + '"' + "\n" + " -" + " " + name + "," + " " + date + "```"
                    return await my_bot.say(output)
        elif len(args) == 0:  # if no arguments given then display any quote
            name, values = random.choice(list(quotes.items()))
            keyword, quote = random.choice(list(values.items()))
            date = quote[1]
            output = "```" + '"' + quote[0] + '"' + "\n" + " -" + " " + name + "," + " " + date + "```"
            return await my_bot.say(output)
        else:
            return await my_bot.say("You entered the wrong number of arguments.")


@my_bot.command(name="list", aliases=["keywords"])
async def list_keywords(*args):
    """Get list of keywords"""
    with open('keyword_list.txt', 'r') as f:
        if args:  # if name is given as argument then display only keywords for that person
            for line in f:
                keyword_str = ''
                if line.startswith(args[0]):
                    l = line.split(' ')
                    for item in l:
                        # print(item)
                        keyword_str += str(item) + ' '
                    return await my_bot.say(keyword_str)
        else:  # display all keywords for all users in the database
            for line in f:
                keyword_str = ''
                l = line.split(' ')
                for item in l:
                    # print(item)
                    keyword_str += str(item) + ' '
                await my_bot.say(keyword_str)


@my_bot.command(name="delete", aliases=["remove", "undo"])
async def delete_quote(*args):
    """Delete quote associated with keyword"""
    infile = open('quotes.txt', 'r')  # open text file containing quote info
    quotes = json.load(infile)  # load quote info to a json format
    infile.close()
    if len(args) == 1:  # if only keyword given as an argument then delete first quote found with that keyword
        for name, key in quotes.items():
            if args[0] in key:
                del quotes[name][args[0]]
                with open('quotes.txt', 'w') as outfile:
                    json.dump(quotes, outfile)
                await delete_keyword(args[0])
                return await my_bot.say("Quote deleted.")
        return await my_bot.say("There is no quote represented by that keyword.")
    elif len(args) == 2:  # if keyword and name given as arguments then delete that specific quote
        for name, key in quotes.items():
            if args[0] in key and name == args[1]:
                del quotes[name][args[0]]
                with open('quotes.txt', 'w') as outfile:
                    json.dump(quotes, outfile)
                await delete_keyword(args[0], args[1])
                return await my_bot.say("Quote deleted.")
        return await my_bot.say("There is no quote represented by that keyword from " + args[1])
    else:
            return await my_bot.say("You entered the wrong number of arguments.")


@my_bot.command(name="quit", aliases=["shutdown", "end", "stop"])
async def bot_quit():
    """Shut the bot down."""
    await my_bot.say("Shutting down...")
    await my_bot.logout()


my_bot.run("")

# way to add new names to database
