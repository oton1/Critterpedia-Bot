import asyncio
import os
import pandas as pd
from dotenv import load_dotenv
import datetime
from discord.ext import commands
import discord
import requests

load_dotenv()

intent = discord.Intents.default()
intent.members = True
intent.message_content = True
client = discord.Client(intents=intent)

MONTH_NAMES = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
               'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']


def get_availability(url):
    response = requests.get(url)
    data = response.json()
    availability_dict = data['availability']
    months = []
    hours = []
    for month in availability_dict['month-array-southern']:
        months += list(range(month[0], month[1]+1))
    for hour in availability_dict['time-array']:
        hours += list(range(hour[0], hour[1]+1))
    hours = [h % 24 for h in hours]
    return (months, hours)


def getCreature(name):
    creature = None

    list_bugs = []
    list_sea = []
    list_fish = []

    for file in ['bugs.json', 'sea.json', 'fish.json']:
        if name.capitalize() in MONTH_NAMES:

            month_number = MONTH_NAMES.index(name.capitalize())+1
            df = pd.read_json(file)
            for col in df.columns:
                obj_month_array_southern = df[col]['availability']['month-array-southern']
                if month_number in obj_month_array_southern:
                    if file == 'bugs.json':
                        list_bugs.append(col)
                    elif file == 'sea.json':
                        list_sea.append(col)
                    else:
                        list_fish.append(col)
                else:
                    continue

        else:
            try:
                creature = pd.read_json(file)[name]
            except:
                pass

    if name.capitalize() in MONTH_NAMES:
        df = pd.DataFrame([list_bugs, list_sea, list_fish])
        df = df.transpose()
        df.columns = ['bugs','sea','fish']
        
    return creature


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!info'):
        creature_name = "_".join(message.content.split(' ')[1:])
        creature_name = creature_name.lower().replace(" ", "-")
        creature = getCreature(creature_name)

        if creature is not None:
            current_month = datetime.datetime.now().month
            current_hour = datetime.datetime.now().hour
            months = creature["availability"]["month-array-southern"]
            month_names = [MONTH_NAMES[m - 1] for m in months]
            hours = creature["availability"]["time-array"]
            if current_month in months and current_hour in hours:
                month_names = [datetime.date(
                    1900, m, 1).strftime('%B') for m in months]
                availability = "está disponível nesta época do ano e neste horário!"
            else:
                if current_month not in months:
                    availability = f"não está disponível neste mês. Estará disponível nos seguintes meses: {', '.join(month_names)}."
                else:
                    availability = f"está disponível neste mês, mas nos seguintes horários: {creature['availability']['time'] if len(creature['availability']['time']) != 0 else 'O dia todo!'}"
                response = f"Essa criatura vale {creature['price']} bells e {availability}"
                embed = discord.Embed(title=creature_name.title().replace(
                    "_", " "), description=f"```{response}```")
                embed.set_image(url=creature['image_uri'])
                await message.reply(embed=embed)
        else:
            response = "Essa criatura não existe, meu chapa..."
            await message.channel.send(response)

@client.event
async def on_ready():
    print("Critterbot pronto pra uso! {0.user}".format(client))

client.run(os.getenv("TOKEN"))
