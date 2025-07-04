# ---------------------------------------------------------------------------- #
#                                  Voyager BOT                                 #
# ---------------------------------------------------------------------------- #
# This System is made by Voyager Systems, All Terms of Service applies to this 
# product. Distribution of this system outside of Voyager's Premises is considered
# as copy-right infringment, do not attempt to distribute or re-use  this product 
# or any denomination, or function of it unless authorized by the Voyager Lead
# Developer.

# Terms: https://voyagersys.xyz/terms
# Privacy: https://voyagersys.xyz/privacy
 
# ---------------------------------- Imports --------------------------------- #
# Here are the system imports and packages that run the system.
# ---------------------------------------------------------------------------- #
import json
import discord
import requests
import datetime
from roblox import Client
from discord import app_commands
from discord.ext import commands, tasks

# ------------------------------- Configuration ------------------------------ #
# Here are the BOT configuration system.
# ---------------------------------------------------------------------------- #
from settings import server_settings, bot_settings, mile_settings

#? BOT Setup
Roblox = Client()
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="?", intents=intents)
# ---------------------------------------------------------------------------- #

# ----------------------------- Background Tasks ----------------------------- #
# These are tasks that run in the background process.
# ---------------------------------------------------------------------------- #
@tasks.loop(seconds=60) 
async def Sync_BOT_Commands():
    try:
        await bot.tree.sync()
    except Exception as err:
        print(f"Error syncing commands: {err}")
    
# ---------------------------------------------------------------------------- #

# --------------------------------- Functions -------------------------------- #
# These are the functions that will be used through out the system.
# ---------------------------------------------------------------------------- #
def ErrorEmbed(Error):
    """
    [Embeds] Create an error embed, to be used for execution errors.
    """  
    print(f'|   {datetime.datetime.now()}   |   [ ❌ ]  An error has occured while processing a request: {Error}')
    
    embed = discord.Embed(color= 0xc05757, description= f'There has been an error while processing this request, please view details below. ```{Error}``` ')

    embed.set_author(name= ' Error')
    return {"embed": embed}

def SuccessEmbed(Prompt):
    """
    [Embeds] Create a success embed, used when a successful prompt has been made
    """  
        
    embed = discord.Embed(color= 0x097969, description=Prompt)
    embed.set_author(name= ' Success')
    return {"embed": embed}
# ---------------------------------- Events ---------------------------------- #
# These are the events that the bot registers when online.
# ---------------------------------------------------------------------------- #
@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user}")

    Sync_BOT_Commands.start()
# ---------------------------------------------------------------------------- #

# --------------------------------- Commands --------------------------------- #
# These are the bot commands that are available in the bot.
# ---------------------------------------------------------------------------- #
class AdminGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="miles", description="Voyager Miles API Commands")
    
    @app_commands.command(name='fetch', description='Fetch the miles amount a player has in the server')
    async def miles_Fetch(self, interaction: discord.Interaction, roblox: str = None):#type:ignore
        try:
            await interaction.response.defer()
            
            try:
                user = await Roblox.get_user_by_username(roblox)
                
            except:
                user = None
            
            if user is not None:
                serverdata = requests.get('https://api.voyagersys.xyz/miles/configuration/', 
                                    headers={'Authorization': mile_settings['Password']},
                                    params={
                                        'server': server_settings['MainServer']
                                    })
                
                milesdata = requests.get('https://api.voyagersys.xyz/miles/points/', 
                                    headers={'Authorization': mile_settings['Password']},
                                    params={
                                        'server': server_settings['MainServer'],
                                        'roblox': roblox
                                    })
                
                if serverdata.status_code == 200 and milesdata.status_code == 200:
                    serverdata = json.loads(serverdata.content)
                    amount = json.loads(milesdata.content).get('Amount')

                    embed = discord.Embed(
                        description=f'**{user.display_name} ([@{user.name}](https://www.roblox.com/users/{user.id}/profile))** currently has `{amount}` miles', #type:ignore
                        color=serverdata['Color']
                    )

                    embed.set_author(name=f'{serverdata['Name']}')
                    view = discord.ui.View()
                    button = discord.ui.Button(style=discord.ButtonStyle.link, url=f'https://voyagersys.xyz/leaderboard/?roblox={user.id}', label=f'{user.name}\'s Miles') #type:ignore
                    
                    view.add_item(button)
                    
                    await interaction.followup.send(embed=embed, view=view)
                
                elif serverdata.status_code != 200:
                    error = ErrorEmbed(str(serverdata.content))
                    await interaction.followup.send(embed=error['embed'])
                    
                elif milesdata.status_code != 200:
                    error = ErrorEmbed(str(milesdata.content))
                    await interaction.followup.send(embed=error['embed'])   
            else:
                error = ErrorEmbed('Roblox user has not been found')
                await interaction.followup.send(embed=error['embed']) 
                
        except Exception as err:
            error = ErrorEmbed(str(err))
            await interaction.followup.send(embed=error['embed'])
    
# Slash command
@bot.tree.command(name="hello", description="Say hello!")
async def hello_command(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hello {interaction.user.name}!", ephemeral=True)

# Run the bot
bot.run(bot_settings['token'])
