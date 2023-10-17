# ======================[ IMPORTS AND INITIALIZATIONS ]======================

import warnings
import discord 
from discord.ext import commands
import asyncio
import openai
import tracemalloc
import os
from config import TamaToken, TamaKey



tracemalloc.start()

# ======================[ GLOBAL VARIABLES ]================================
user_message_logs = {}


# ======================[ BOT SETUP ]======================
# Your OpenAI API key and Bot Token
openai.api_key = TamaKey
Token = TamaToken

# Define the bot
client = commands.Bot(command_prefix="!", intents=discord.Intents.all())
client.chatlog_dir = "logs/"



# Inside your code, before the warning occurs, you can suppress it like this:
warnings.filterwarnings("ignore", category=UserWarning)



# ======================[ UTILITY FUNCTIONS ]======================

# ==========================
# Message Logging
# ==========================


def add_message_to_log(author_id, content):
    if author_id not in user_message_logs:
        user_message_logs[author_id] = [{"role": "system", "content": "Assume the role of Fuuma Tama, a clumsy, airheaded, yet loyal and playful ninja catgirl. You have purple hair, blue eyes, cat ears, and a cat tail. You love coddles, fluffy food, cosplay, and fighting. Always wear your unique outfit of a purple T-shirt, short skirt, purple panties, and short white socks, complemented by hairpins and a scarf. Treat everyone as if they're your big brothers and sisters. Maintain a friendly, protective, immature, relaxed, and play-loving nature in all interactions."
}]
    user_message_logs[author_id].append({"role": "user", "content": content})




# ======================[ EVENT HANDLERS ]======================


## ---- On Ready Event ----

@client.event
async def on_ready():
    try:
        print("on_ready Triggered")
        guild = discord.utils.get(client.guilds, name='The Dark Void of Gaming')
        if guild:
            print(f"Guild found: {guild.name}")
        else:
            print("Guild not found")
            return
        

        channel = discord.utils.get(guild.text_channels, name='tamachat')

        messages = []
        async for message in channel.history(limit=10):
            messages.append(message)

        for message in messages:
            if message.author.bot:
                continue
            add_message_to_log(message.author.id, message.content)

    except Exception as e:
        print(f"An error occurred in on_ready: {e}")


## ---- On Message Event ----

@client.event
async def on_message(message):
    try:
        # Check if the message starts with '!'
        if message.content.startswith('!'):
            await client.process_commands(message)  # Process the command
            return  # Exit the function without further processing for OpenAI
        
                # Check if the message starts with '!'
        if message.content.startswith('!') and message.channel.name == "rpg":
            await client.process_commands(message)  # Process the command
            return  # Exit the function without further processing for OpenAI
       
        # Ignore messages from bots and channels other than "tamachat"
        if message.author.bot or message.channel.name != "tamachat":
            return



        # Add the received message to the log
        add_message_to_log(message.author.id, message.content)

        # Check if there's enough messages for a proper conversation
        if len(user_message_logs[message.author.id]) >= 2:
            # Make an OpenAI API call to get the completion
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=user_message_logs[message.author.id],
                max_tokens=100,
                temperature=0.7
            )

        # Get the text response from the API call
        response_text = completion.choices[0].message['content']

        # If the message is too long, trim it
        if len(response_text.split()) > 140:
            response_text = ". ".join(response_text.split(". ")[:-1]) + "."

        # Add the response to the log
        user_message_logs[message.author.id].append({"role": "assistant", "content": response_text})

        # Send the text response
        await message.channel.send(response_text)

    except Exception as e:
        print(f"Error in on_message: {str(e)}")

    await client.process_commands(message)



# ======================[ COGS]======================

@client.command()
async def load(ctx, extension):
    try:
        client.load_extension(f'Cogs.{extension}')
        await ctx.send(f'Loaded {extension} successfully!')
    except Exception as e:
        await ctx.send(f'Could not load {extension}. Error: {e}')

@client.command()
async def unload(ctx, extension):
    try:
        client.unload_extension(f'Cogs.{extension}')
        await ctx.send(f'Unloaded {extension} successfully!')
    except Exception as e:
        await ctx.send(f'Could not unload {extension}. Error: {e}')

@client.command()
async def reload(ctx, extension):
    try:
        await client.unload_extension(f'Cogs.{extension}')
        await client.load_extension(f'Cogs.{extension}')
        await ctx.send(f'Reloaded {extension} successfully!')
    except Exception as e:
        await ctx.send(f'Could not reload {extension}. Error: {e}')




 # ======================[ MAIN ROUTINE ]======================



async def load():
    for filename in os.listdir('./Cogs'):
        if filename.endswith('.py'):
            await client.load_extension(f'Cogs.{filename[:-3]}')
        else:
            print(f'Unable to load {filename[:-3]}')

# =====================
# Main Async Function
# =====================

async def main():
    async with client:
        await load()
        print("Tama Online!")
        await asyncio.gather(
            client.start(Token),
        )


if __name__ == "__main__":
    asyncio.run(main())
