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

month_name = None

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

    if message.content.startswith('!help'):
        embed = discord.Embed(title="Comandos disponíveis", description="Retorna informações sobre as criaturas e lista as disponíveis no mês especificado.", color=0xA1300E)
        embed.add_field(name="!info <nome_da_criatura>", value="Retorna informações sobre a criatura.", inline=False)
        embed.add_field(name="!lista <mês>", value="Retorna uma lista de criaturas disponíveis no mês especificado.", inline=False)
        await message.channel.send(embed=embed)

    elif message.content.startswith('!info'):
        creature_name = "_".join(message.content.split(' ')[1:])
        creature_name = creature_name.lower().replace(" ", "-")
        print(f"Processando o nome da criatura: {creature_name}")

        creature = getCreature(creature_name)
        print(f"Resultado de getCreature para {creature_name}: {creature}")

        if creature is not None:
            try:
                current_month = datetime.datetime.now().month
                current_hour = datetime.datetime.now().hour
                months = creature["availability"]["month-array-southern"]
                month_names = [MONTH_NAMES[m - 1] for m in months]
                hours = creature["availability"]["time-array"]

                print(f"Meses disponíveis: {month_names}")  
                print(f"Horas disponíveis: {hours}") 

                if current_month in months and current_hour in hours:
                    availability = "está disponível nesta época do ano e neste horário!"
                else:
                    if current_month not in months:
                        availability = f"não está disponível neste mês. Estará disponível nos seguintes meses: {', '.join(month_names)}."
                    else:
                        availability = "está disponível neste mês, mas em outros horários."
                response = f"Essa criatura vale {creature['price']} bells e {availability}"
                print(f"Resposta formada: {response}")  

                embed = discord.Embed(title=creature_name.title().replace("_", " "), description=f"```{response}```", color=0xA1300E)
                embed.set_image(url=creature['image_uri'])
                await message.reply(embed=embed)
                print("Embed enviado com sucesso.")  
            except Exception as e:
                print(f"Erro ao construir ou enviar embed: {e}")  
                await message.channel.send("Houve um problema ao enviar a informação, por favor tente novamente.")
        else:
            response = "Essa criatura não existe, meu chapa..."
            await message.channel.send(response)
            print(f"Enviando mensagem de erro: {response}")  


    elif message.content.startswith('!lista'):
        month_name = message.content.split(' ')[1].capitalize()
        if month_name in MONTH_NAMES:
            list_bugs = []
            list_sea = []
            list_fish = []
            for file in ['bugs.json', 'sea.json', 'fish.json']:
                df = pd.read_json(file)
                for col in df.columns:
                    availability = df[col]['availability']
                    if availability.get('isAllYear', False) or month_name in [MONTH_NAMES[m - 1] for m in availability['month-array-southern']]:
                        if file == 'bugs.json':
                            list_bugs.append(' '.join([w.capitalize() for w in col.split('_')]))
                        elif file == 'sea.json':
                            list_sea.append(' '.join([w.capitalize() for w in col.split('_')]))
                        else:
                            list_fish.append(' '.join([w.capitalize() for w in col.split('_')]))

            if month_name in MONTH_NAMES:
                embed = discord.Embed(title=f"Criaturas disponíveis em {month_name}", color=0xA1300E)
                if list_bugs:
                    embed.add_field(name="Bugs", value="\n".join(list_bugs), inline=False)
                if list_sea:
                    embed.add_field(name="Sea Creatures", value="\n".join(list_sea), inline=False)
                if list_fish:
                    embed.add_field(name="Fish", value="\n".join(list_fish), inline=False)
                await message.channel.send(embed=embed)
        
        else:
            response = "Nome de mês inválido, tente novamente com um dos seguintes nomes de mês: " + ", ".join(MONTH_NAMES)
            await message.channel.send(response)
            print(response)

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='!help para ver os comandos do bot'))
    print("Critterbot pronto pra uso! {0.user}".format(client))

client.run(os.getenv("TOKEN"))