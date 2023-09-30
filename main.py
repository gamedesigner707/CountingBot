import discord
from discord.ext import commands
import os
from keep_alive import keep_alive
from replit import db

botID = os.environ["botID"]
BOT_USER_ID = 946577137815670794
MY_ID = 430358551974772739
CHECK_MARK_STR = "\u2705"
X_STR = "\u274C"

# Dictionaries containing game information relevant to each server
# Format is {Server1 ID: Value1, Server2 ID: Value2, ...}

# Value: The id of the channel the bot has been assigned to
Channels = {}
# Value: The last number that was counted in the server
lastNumbers = {}
# Value: The id of the member who counted the last number
lastAuthors = {}
# Value: The id of the message associated with the last number counted
lastMessages = {}

# Returns two values:
# 1. Boolean representing whether a count was successful or not
# 2. A prompt for the bot to say if a count wasn't successful
def receive_msg(message):
    msg = message.content
    global lastNumbers
    global lastAuthors
    lastNumber = lastNumbers[message.guild.id]
    lastAuthor = lastAuthors[message.guild.id]
    try:
        number = int(msg,2)
        if number == lastNumber + 1:
          if (not lastAuthor or message.author.id != lastAuthor):
            return True,None
          else:
            return False,"You can't count two numbers in a row."
        else:
            return False,"Wrong number."
    # If the message isn't convertible to an integer then return None so the message is ignored
    except:
        return None,None

# Takes in a base 10 number and returns in binary as a string
def binary(n):
    return bin(n).replace("0b","")

Client = discord.Client()
client = commands.Bot(command_prefix="/")

# Runs when the bot is loaded and ready for action!
@client.event
async def on_ready():
  print("Bot is ready!")
  global Channels
  global lastNumbers
  global lastMessages
  global lastAuthors
  for i,v in db["Channels"].items():
    Channels[int(i)] = v
  for i,v in db["lastNumbers"].items():
    lastNumbers[int(i)] = v
  for i,v in db["lastMessages"].items():
    lastMessages[int(i)] = v
  for i,v in db["lastAuthors"].items():
    lastAuthors[int(i)] = v
  print("Data Loaded")

# Triggers when a user sends a message
@client.event
async def on_message(message):
    if message.author.id == BOT_USER_ID:
      return
    global Channels
    global lastNumbers
    global lastAuthors
    global lastMessages
    if message.author.id == message.guild.owner_id or message.author.id == MY_ID:
      if message.content.lower() == "binary count here":
        Channels[message.guild.id] = message.channel.id
        lastNumbers[message.guild.id] = 0
        lastAuthors[message.guild.id] = None
        lastMessages[message.guild.id] = None
        await message.channel.send("Okay!")
    if not message.guild.id in Channels.keys() or message.channel.id != Channels[message.guild.id]:
      return

    result,prompt = receive_msg(message)
    if result:
        await message.add_reaction(CHECK_MARK_STR)
        lastNumbers[message.guild.id] += 1
        lastAuthors[message.guild.id] = message.author.id
        lastMessages[message.guild.id] = message.id
    elif result == False:
        await message.add_reaction(X_STR)
        await message.channel.send(f"<@{message.author.id}> RUINED IT AT **{binary(lastNumbers[message.guild.id])}**!! "
                                   f"Next Number is **1. **"
                                  f" **{prompt}**")
        lastNumbers[message.guild.id] = 0
        lastAuthors[message.guild.id] = None
        lastMessages[message.guild.id] = message.id
    db['Channels'] = Channels
    db['lastNumbers'] = lastNumbers
    db['lastAuthors'] = lastAuthors
    db['lastMessages'] = lastMessages

# Triggers when a user deletes a message
@client.event
async def on_message_delete(message):
    global lastMessages
    global lastNumbers
    if message.id == lastMessages[message.guild.id]:
        await message.channel.send(f"<@{message.author.id}> deleted their count of **{binary(lastNumbers[message.guild.id])}**. "
                                   f"The next number is **{binary(lastNumbers[message.guild.id]+1)}**.")

keep_alive()
client.run(botID)
