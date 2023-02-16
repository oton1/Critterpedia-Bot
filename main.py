import discord
import asyncio
import requests
import os
import pandas as pd
from dotenv import load_dotenv
import datetime
from discord.ext import commands
import numpy


load_dotenv()

intent = discord.Intents.default()
intent.members = True
intent.message_content = True
client = discord.Client(intents=intent)

#


@client.event
async def on_message(message):
    if message.author == client.user:
        return


# Reading and creating the !bug command, based on time and month

    if message.content.startswith('!bug'):
        bugs = pd.read_json('bugs.json')
        bug_name = "_".join(message.content.split(' ')[1:])
        try:
            bugs = bugs[bug_name]
            current_month = datetime.datetime.now().month
            current_hour = datetime.datetime.now().hour
            months = bugs["availability"]["month-array-southern"]
            hours = bugs["availability"]["time-array"]
            if current_month in months and current_hour in hours:
                availability = "está disponível neste momento!"
            else:
                availability = f"está disponível no horário: {bugs['availability']['time'] if len(bugs['availability']['time'])!=0 else 'All day'}"
            response = f"Esse bug vale {bugs['price']} bells e {availability}"
        except KeyError:
            response = "Esse bug não existe, meu chapa..."

        await message.channel.send(response)
    

# Reading and creating the !fish command
    
    if message.content.startswith('!fish'):
        fishes = pd.read_json('fish.json')
        fish_name = "_".join(message.content.split(' ')[1:])
        try:
            fish = fishes[fish_name]
            current_month = datetime.datetime.now().month
            current_hour = datetime.datetime.now().hour
            months = fish["availability"]["month-array-southern"]
            hours = fish["availability"]["time-array"]
            if current_month in months and current_hour in hours:
                availability = "está disponível neste momento!"
            else:
                availability = f"está disponível no horário: {fish['availability']['time'] if len(fish['availability']['time'])!=0 else 'All day'}"
            response = f"Esse peixe vale {fish['price']} bells e {availability}"
        except KeyError:
            response = "Esse peixe não existe, meu chapa..."

        await message.channel.send(response)

# Reading and creating the !sea command

    if message.content.startswith('!sea'):
        sea_creatures = pd.read_json('sea.json')
        sea_creatures_name = message.content.split(' ')[1:]
        sea_creatures_name = " ".join(sea_creatures_name).lower().strip().replace(" ", "_")
        try:
            sea = sea_creatures[sea_creatures_name]
            current_month = datetime.datetime.now().month
            current_hour = datetime.datetime.now().hour
            months = sea["availability"]["month-array-southern"]
            hours = sea["availability"]["time-array"]
            if current_month in months and current_hour in hours:
                availability = "está disponível neste momento!"
            else:
                availability = f"está disponível no horário: {sea['availability']['time'] if len(sea['availability']['time'])!=0 else 'Dia inteiro'}"
            response = f"Essa criatura marinha vale {sea['price']} bells e {availability}"
        except KeyError: 
            response = "Essa criatura marinha não existe, meu chapa"

        await message.channel.send(response)

    

            
            
# Client event for the bot entrance on the server

@client.event
async def on_ready():
    print("Critterbot pronto pra uso! {0.user}".format(client))


# Discord token, essential for validation on entrance. in this case, we are using .env ft. gitignore to supress the token

client.run(os.getenv("TOKEN")) 

