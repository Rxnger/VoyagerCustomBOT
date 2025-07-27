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
import sys
sys.dont_write_bytecode = True
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
bot = commands.Bot(command_prefix="?", intents=discord.Intents.all())
# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
print('--------------------------------------------------------------------------')
print('|                   [ Voyager ] Discord Module Runner                    |')
print('--------------------------------------------------------------------------')
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
# --------------------------------- Commands --------------------------------- #
# These are the bot commands that are available in the bot.
# ---------------------------------------------------------------------------- #
    
@app_commands.command(name='miles_fetch', description='Fetch the miles amount a player has in the server')
@app_commands.describe(
    roblox = 'Roblox Username'
)
async def miles_Fetch(interaction: discord.Interaction, roblox: str):#type:ignore
    try:
        await interaction.response.defer()
        if interaction.guild.id in server_settings['AllianceServers'] or interaction.guild.id == server_settings['MainServer']: #type:ignore
        
            try:
                user = await Roblox.get_user_by_username(roblox)
                
            except:
                user = None
            
            if user is not None:
                serverdata = requests.get('https://voyagersys.xyz/api/miles/configuration/', 
                                    headers={'Authorization': mile_settings['Password']},
                                    params={
                                        'server': server_settings['MainServer']
                                    })
                
                milesdata = requests.get('https://voyagersys.xyz/api/miles/points/', 
                                    headers={'Authorization': mile_settings['Password']},
                                    params={
                                        'server': server_settings['MainServer'],
                                        'roblox': user.id
                                    })
                
                if serverdata.status_code == 200 and milesdata.status_code == 200:
                    serverdata = json.loads(serverdata.content)
                    amount = json.loads(milesdata.content)
                    print(serverdata)
                    print(amount)
                    embed = discord.Embed(
                        description=f'**{user.display_name} ([@{user.name}](https://www.roblox.com/users/{user.id}/profile))** currently has `{amount['Amount']}` miles', #type:ignore
                        color=int(str(serverdata['Color']).replace('#', '0x'), 16)
                    )

                    embed.set_author(name=f'{serverdata["Miles"]}')
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
        
        else:
            error = ErrorEmbed('This server is not authorized to use this bot')
            await interaction.followup.send(embed=error['embed'])  
    except Exception as err:
        error = ErrorEmbed(str(err))
        await interaction.followup.send(embed=error['embed'])

@app_commands.command(name='miles_add', description='Add  miles amount to a player\'s account')
@app_commands.checks.has_permissions(administrator = True)  # Change this to suit your server's permission
@app_commands.describe(
    roblox = 'Roblox Username',
    amount = 'How much do you want to add to the user?'
)
async def miles_Add(interaction: discord.Interaction, roblox: str, amount: int):#type:ignore
    try:
        await interaction.response.defer()
        if interaction.guild.id in server_settings['AllianceServers'] or interaction.guild.id == server_settings['MainServer']: #type:ignore
        
            try:
                user = await Roblox.get_user_by_username(roblox)
                
            except:
                user = None
            
            if user is not None:
                serverdata = requests.get('https://voyagersys.xyz/api/miles/configuration/', 
                                    headers={'Authorization': mile_settings['Password']},
                                    params={
                                        'server': server_settings['MainServer']
                                    })
                
                milesdata = requests.post('https://voyagersys.xyz/api/miles/points/', 
                                    headers={'Authorization': mile_settings['Password']},
                                    params={
                                        'server': server_settings['MainServer'],
                                        'roblox': user.id,
                                        'amount': amount,
                                        'author': f'Manually added via Custom Discord BOT (Author: {interaction.user.name} - {interaction.user.id})'
                                    })
                
                if serverdata.status_code == 200 and milesdata.status_code == 200:
                    serverdata = json.loads(serverdata.content)

                    
                    await interaction.followup.send(embed=SuccessEmbed(f'Successfully added `{amount}` to **{user.display_name} ([@{user.name}](https://www.roblox.com/users/{user.id}/profile))**\'s account')['embed'])
                
                elif serverdata.status_code != 200:
                    error = ErrorEmbed(str(serverdata.content))
                    await interaction.followup.send(embed=error['embed'])
                    
                elif milesdata.status_code != 200:
                    error = ErrorEmbed(str(milesdata.content))
                    await interaction.followup.send(embed=error['embed'])   
            else:
                error = ErrorEmbed('Roblox user has not been found')
                await interaction.followup.send(embed=error['embed']) 
        
        else:
            error = ErrorEmbed('This server is not authorized to use this bot')
            await interaction.followup.send(embed=error['embed'])  
    except Exception as err:
        error = ErrorEmbed(str(err))
        await interaction.followup.send(embed=error['embed'])

@app_commands.command(name='miles_remove', description='Remove  miles amount from a player\'s account')
@app_commands.checks.has_permissions(administrator = True) # Change this to suit your server's permission
@app_commands.describe(
    roblox = 'Roblox Username',
    amount = 'How much do you want to remove from the user?'
)
async def miles_remove(interaction: discord.Interaction, roblox: str, amount: int):#type:ignore
    try:
        await interaction.response.defer()
        if interaction.guild.id in server_settings['AllianceServers'] or interaction.guild.id == server_settings['MainServer']: #type:ignore
        
            try:
                user = await Roblox.get_user_by_username(roblox)
                
            except:
                user = None
            
            if user is not None:
                serverdata = requests.get('https://voyagersys.xyz/api/miles/configuration/', 
                                    headers={'Authorization': mile_settings['Password']},
                                    params={
                                        'server': server_settings['MainServer']
                                    })
                
                milesdata = requests.post('https://voyagersys.xyz/api/miles/points/', 
                                    headers={'Authorization': mile_settings['Password']},
                                    params={
                                        'server': server_settings['MainServer'],
                                        'roblox': user.id,
                                        'amount': -amount,
                                        'author': f'Manually removed via Custom Discord BOT (Author: {interaction.user.name} - {interaction.user.id})'
                                    })
                
                if serverdata.status_code == 200 and milesdata.status_code == 200:
                    serverdata = json.loads(serverdata.content)

                    
                    await interaction.followup.send(embed=SuccessEmbed(f'Successfully removed `{amount}` from **{user.display_name} ([@{user.name}](https://www.roblox.com/users/{user.id}/profile))**\'s account')['embed'])

                
                elif serverdata.status_code != 200:
                    error = ErrorEmbed(str(serverdata.content))
                    await interaction.followup.send(embed=error['embed'])
                    
                elif milesdata.status_code != 200:
                    error = ErrorEmbed(str(milesdata.content))
                    await interaction.followup.send(embed=error['embed'])   
            else:
                error = ErrorEmbed('Roblox user has not been found')
                await interaction.followup.send(embed=error['embed']) 
        
        else:
            error = ErrorEmbed('This server is not authorized to use this bot')
            await interaction.followup.send(embed=error['embed'])  
    except Exception as err:
        error = ErrorEmbed(str(err))
        await interaction.followup.send(embed=error['embed'])


bot.tree.add_command(miles_Fetch)
bot.tree.add_command(miles_Add)
bot.tree.add_command(miles_remove)

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

# ---------------------------------- Events ---------------------------------- #
# These are the events that the bot registers when online.
# ---------------------------------------------------------------------------- #
@bot.event
async def on_ready():
    print('|                                |')
    print(f'|   {datetime.datetime.now()}   |   [ 🟢 ] Connected to Discord: {bot.user} ({bot.user.id})') #type:ignore
    print('|                                |')
    
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.CustomActivity(name=bot_settings['status'])
    )
    print("Registered commands:", len(bot.tree.get_commands()))

    if not Sync_BOT_Commands.is_running():
        Sync_BOT_Commands.start()
    
# ---------------------------------------------------------------------------- #

# Run the bot
bot.run(bot_settings['token'])