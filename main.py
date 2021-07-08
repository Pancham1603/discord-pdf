import discord
from discord.ext import commands
from pymongo import MongoClient
import requests
import os
import fitz

client = MongoClient(
    "")
db = client.
open_pdf_collection = db['']

intents = discord.Intents.default()
intents.members = True
intents.reactions = True
bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command('help')

open_pdfs = {}
reactions = ['⬅️', '➡️']


@bot.command()
async def view(ctx, source=None):
    if ctx.message.attachments:
        url = ctx.message.attachments[0].url

        open_pdf_collection.insert_one({'_id': ctx.author.id})

        try:
            os.mkdir(f'{ctx.author.id}')
        except FileExistsError:
            pass
        filename = ctx.message.attachments[0].filename
        filename = "".join(x for x in filename if (x.isalnum() or x in "._- "))

        r = requests.get(url, allow_redirects=True)
        try:
            open(f'{ctx.author.id}/{filename}', 'wb').write(r.content)
        except FileExistsError:
            pass
        doc = fitz.open(f'{ctx.author.id}/{filename}')
        try:
            os.mkdir(f"{ctx.author.id}/{filename[:-4]}")
        except FileExistsError:
            pass
        page_num = 0
        while True:
            try:
                page = doc.loadPage(page_num)  # number of page
                pix = page.getPixmap()
                try:
                    pix.writePNG(f"{ctx.author.id}/{filename[:-4]}/page{page_num + 1}.png")
                except FileExistsError:
                    pass
                page_num += 1
            except:
                file = discord.File(f"{ctx.author.id}/{filename[:-4]}/page1.png")
                channel = discord.utils.get(ctx.guild.channels, name='dump')
                await channel.send(f"!reactionfile {ctx.author.id}", file=file, delete_after=1)
                embed = discord.Embed(title=filename[:-4], description=f"Requested by {ctx.author.id}")
                embed.set_image(url=str(open_pdf_collection.find_one({'_id': ctx.author.id})['url']))
                msg = await ctx.send(embed=embed)

                for reaction in reactions:
                    await msg.add_reaction(emoji=reaction)
                if ctx.author.id in open_pdfs:
                    embed = discord.Embed(title="Close the previous PDF: !close")
                    await ctx.send(embed=embed)
                else:
                    open_pdfs[ctx.author.id] = {'filename': filename[:-4], 'page': 1}
                    break


@bot.command()
async def close(ctx):
    try:
        open_pdf_collection.delete_one({'_id': ctx.author.id})
    except:
        embed = discord.Embed(title="No open PDFs found!")
        await ctx.send(embed=embed)
    try:
        filename = open_pdfs[ctx.author.id]['filename']
        del open_pdfs[ctx.author.id]
        embed = discord.Embed(title=f"Closed {filename}")
        await ctx.send(embed=embed)
    except:
        pass


@bot.event
async def on_reaction_add(reaction, user):
    if user.id == 861364842526801960:
        pass
    else:
        msg = reaction.message
        id = int(msg.embeds[0].description[13:])
        if reaction.emoji == reactions[0]:
            filename = open_pdfs[id]['filename']
            page = open_pdfs[id]['page']
            page -= 1
            try:
                file = discord.File(f"{id}/{filename}/page{page}.png")
                channel = discord.utils.get(msg.guild.channels, name='dump')
                await channel.send(f"!reactionfile {id}",file=file, delete_after=3)
                # await asyncio.sleep(1)
                embed = discord.Embed(title=filename, description=f"Requested by {id}")
                embed.set_image(url=open_pdf_collection.find_one({'_id': id})['url'])
                await msg.edit(embed=embed)
                open_pdfs[id]['page'] -= 1
            except:
                pass
        elif reaction.emoji == reactions[1]:
            filename = open_pdfs[id]['filename']
            page = open_pdfs[id]['page']

            page += 1
            try:
                file = discord.File(f"{id}/{filename}/page{page}.png")
                channel = discord.utils.get(msg.guild.channels, name='dump')
                await channel.send(f"!reactionfile {id}", file=file, delete_after=3)
                # await asyncio.sleep(1)
                embed = discord.Embed(title=filename, description=f"Requested by {id}")
                embed.set_image(url=open_pdf_collection.find_one({'_id': id})['url'])
                await msg.edit(embed=embed)
                open_pdfs[id]['page'] += 1
            except:
                pass


@bot.event
async def on_reaction_remove(reaction, user):
    if user.id == 861364842526801960:
        pass
    else:
        msg = reaction.message
        id = int(msg.embeds[0].description[13:])
        if reaction.emoji == reactions[0]:
            filename = open_pdfs[id]['filename']
            page = open_pdfs[id]['page']
            page -= 1
            try:
                file = discord.File(f"{id}/{filename}/page{page}.png")
                channel = discord.utils.get(msg.guild.channels, name='dump')
                await channel.send(f"!reactionfile {id}",file=file, delete_after=3)
                # await asyncio.sleep(1)
                embed = discord.Embed(title=filename, description=f"Requested by {id}")
                embed.set_image(url=open_pdf_collection.find_one({'_id': id})['url'])
                await msg.edit(embed=embed)
                open_pdfs[id]['page'] -= 1
            except:
                pass
        elif reaction.emoji == reactions[1]:
            filename = open_pdfs[id]['filename']
            page = open_pdfs[id]['page']

            page += 1
            try:
                file = discord.File(f"{id}/{filename}/page{page}.png")
                channel = discord.utils.get(msg.guild.channels, name='dump')
                await channel.send(f"!reactionfile {id}", file=file, delete_after=3)
                # await asyncio.sleep(1)
                embed = discord.Embed(title=filename, description=f"Requested by {id}")
                embed.set_image(url=open_pdf_collection.find_one({'_id': id})['url'])
                await msg.edit(embed=embed)
                open_pdfs[id]['page'] += 1
            except:
                pass


@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.channel == discord.utils.get(message.guild.text_channels, name='dump'):
        if str(message.content).split()[0] == '!reactionfile':
            url = message.attachments[0].url
            id = str(message.content).split()[1]
            open_pdf_collection.update_one({'_id': int(id)}, {'$set': {
                'url': str(url)}})




token = ''
bot.run(token)
