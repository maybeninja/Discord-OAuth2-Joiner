from discord.ext import commands
from Modules.utils import *
from Modules.key import *
from Modes.autobuy import *
import discord
from typing import *
config = load_config()

embed_color = config['MainBotSettings']['EmbedColor']
footer = config['MainBotSettings']['EmbedFooter']
footer_icon = config['MainBotSettings']['FooterIcon']
status_channel = config['MainBotSettings']['StatusChaannel']


def make_embed(title,desciption):
    embed = discord.Embed(title=title,description=desciption)
    embed.color = embed_color
    embed.set_footer(text=footer,icon_url=footer_icon)
    return embed

bot = commands.Bot(command_prefix=',',help_command=None,intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    sync = await bot.tree.sync()
    print(f'Synced {len(sync)} commands.')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=config['MainBotSettings']['Activity']))


@bot.hybrid_command(name='gen_bulk_keys', description='Generate bulk keys')
async def gen_bulk_keys(ctx, amount: int, service_quantity: int, service: Literal['Members', 'Boosts'], type: Literal['1 Month', '3 Months', 'Offline', 'Online']):
    await ctx.interaction.response.defer(thinking=True, ephemeral=True)

    if ctx.author.id != int(config['MainBotSettings']['OwnerID']):
        embed = make_embed("❌ Error", "You do not have permission to use this command.")
        return await ctx.interaction.followup.send(embed=embed, ephemeral=True)

    type_mapping = {
        "1 Month": "1m",
        "3 Months": "3m",
        "Offline": "Offline",
        "Online": "Online"
    }

    mapped_type = type_mapping.get(type)
    service_lower = service.lower()

    keys = gen_bulk(service_lower, mapped_type, amount, service_quantity)

    if isinstance(keys, str):
        embed = make_embed("❌ Failed", f"Error while generating keys: `{keys}`")
        return await ctx.interaction.followup.send(embed=embed, ephemeral=True)

    formatted_keys = "\n".join(keys)
    embed = make_embed("✅ Keys Generated", f"Generated `{len(keys)}` keys for **{service} - {type}**:\n```{formatted_keys}```")
    await ctx.interaction.followup.send(embed=embed, ephemeral=True)






def start_bot():
    start()




start_bot()