import discord
import requests
from discord.ext import commands
import fonction as f
import sqlite3
from Trade import Trade

token = "MTA0MTcxNTk3MzI1MTY2NjAwMg.GFmON8.UOOZ8K-6pW0oTQXVhaVw8jUaKLfkQ_MQ8MTrsY"
intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix="/", intents=intents)
cards = f.open_json("cardName.json")["data"]
con  = f.connect_to_db("bot_db.db")
cur = f.get_cursor(con)
tree = bot.tree

@bot.event
async def on_ready():
    await tree.sync()
    f.create_db_tables(cur,con)
    print("bot started")


async def get_user_name(user_id: int):
    user = await bot.fetch_user(user_id)
    return user.name


@tree.command(name="test_fetch_username")
async def fetch_user_name(inte: discord.Interaction):
    user_id = inte.user.id
    user = await bot.fetch_user(user_id)
    await inte.response.send_message(user.name)


# la fonction d'update du fichier cardname est une solution temporaire avant que je fasse tourner le bot
# sur un serveur par la suite je lui ferais faire l'update tout seul tout les X temps

@tree.command(name="update_cardname")
async def update_cardName(inte: discord.Interaction):
    await inte.response.defer()
    if inte.user.id == 443471145149399069:

        responseScry = requests.get(
            "https://api.scryfall.com/catalog/card-names")

        if responseScry.status_code == 200:
            dico = responseScry.json()
            l = len(dico["data"])
            for x in range(len(dico["data"])):
                dico["data"][x] = dico["data"][x].lower()
                # print(dico["data"][x])

            f.dump_json("cardName.json", dico)
        await inte.followup.send("update done")
    else:
        await inte.followup.send("Only the owner can do this !")



@tree.command(name="add_card")
@discord.app_commands.choices(
    searching=[
        discord.app_commands.Choice(name="yes", value=1),
        discord.app_commands.Choice(name="no", value=0)
    ]
)
async def add_card(inte: discord.Interaction, searching: discord.app_commands.Choice[int], card: str, nb: int = 1):
    user_id = str(inte.user.id)
    message : str
    x = f.add_card(card, nb, user_id, searching.value,con,cur)
    
    searching_state : str
    if searching:
        searching_state = "searched"
    else:
        searching_state = "owned"
    
    if x == 0:
        message = f'{nb} {card} have been sucessfuly added to your collection as {searching_state} '
    else:
        print("error while inserting card")
        message = "error while inserting card"
        
    await inte.response.send_message(message)
    
    
@add_card.autocomplete('card')
async def cards_autocomplete(inte: discord.Interaction, current: str) -> list[discord.app_commands.Choice[str]]:
    user_id = str(inte.user.id)
    cardList = f.open_json("cardName.json")["data"]
    matching_cards = [card for card in cardList if current in card]
    first_25_cards = matching_cards[:25]
    return [discord.app_commands.Choice(name=card, value=card) for card in first_25_cards]



@tree.command(name="remove_card")
async def remove_card(inte: discord.Interaction, card: str, nb : int = 1 ):
    uid = str(inte.user.id)
    return_code : int 

    try:
        x = f.remove_card(uid,card,nb,con,cur)
        if x == 0:
            message = f' {nb} {card} have been successfully removed from your binder'
        else:
            message = f' {nb} {card} have been successfully removed from your binder'
    except:
        message = f'an error occured while trying to delete {card}'
            
    await inte.response.send_message(message)


@remove_card.autocomplete('card')
async def cards_autocomplete(inte: discord.Interaction, current: str) -> list[discord.app_commands.Choice[str]]:
    uid= str(inte.user.id)
    default_cards = []
    
    t = "SELECT card from binder WHERE uid = ?"
    key_list = f.request_to_list(t,(uid,),cur)
    
    if len(key_list) > 25:
        default_cards = key_list[:24]
    else:
        default_cards = key_list

    if current == "":
        cards = default_cards
    else:
        cards = key_list

    return [discord.app_commands.Choice(name=card, value=card) for card in cards if current in card][:25]


@tree.command(name="show_binder")
async def show_binder(inte: discord.Interaction):
    await inte.response.defer()
    uid = str(inte.user.id)
   
    binder = f.get_binder(uid,cur)
    searching = list(binder["searching"])
    owned = list(binder["owned"])

    r = "**you have the following cards in your binder** : \n - cards you are searching for : "

    for x in searching:
        r += f'\n - {x[1]} : {x[0]}'
    r += " \n\n - cards you own :"
    for x in owned:
        r += f'\n - {x[1]} : {x[0]}'

    if len(r) > 1999:
        filename = f'{inte.user.name}Binder.txt'
        with open(filename, "w", encoding="utf-8") as file:
            file.write(r)
        fileDiscord = discord.File(filename, filename=filename)

        await inte.followup.send("Your binder is to big so we had to convert it into a file")
        await inte.followup.send(file=fileDiscord)
    else:
        await inte.response.send_message(r)


@tree.command(name="get_binder")
async def get_binder(inte: discord.Interaction):
    await inte.response.defer()
    uid = str(inte.user.id) 
    binder = f.get_binder(uid,cur)

    searching = list(binder["searching"])
    owned = list(binder["owned"])
    
    filename = f'{inte.user.name}Binder.txt'
    
    with open(filename, "w") as file:
        file.write("/searching/")
        for x in searching:
            file.write(f'\n{x[1]} : {x[0]}')
        file.write("\n\n/owned/")
        for x in owned:
            file.write(f'\n{x[1]} : {x[0]}')

    fileDiscord = discord.File(filename, filename=filename)
    await inte.followup.send("Here is your binder")
    await inte.followup.send(file=fileDiscord)


@tree.command(name="look_for_trades")
async def look_for_trades(inte: discord.Interaction):
    await inte.response.defer()
    uid = str(inte.user.id)
    r = "here are the results\n"
   
    trades : [Trade] = f.look_for_trades(uid,cur)
    for trade in trades:
        print(trade.trader_uid)
        trade_member : discord.Member = inte.guild.get_member(trade.trader_uid)
        r += trade.get_trade_info(inte.user.name,trade_member.name)
        r += "\n\n" 
    
    if len(r) > 1999:
        filename = f'{inte.user.name}Trades.txt'
        with open(filename, "w", encoding="utf-8") as file:
            file.write(r)
        fileDiscord = discord.File(filename, filename=filename)

        await inte.followup.send("Your trades info were to big so we had to convert them into a file")
        await inte.followup.send(file=fileDiscord)
    else:
        await inte.followup.send(r)


@tree.command(name="overwrite_list", description="overwrite your binder by inserting a text file")
@discord.app_commands.choices(
    searching=[
        discord.app_commands.Choice(name="yes", value=1),
        discord.app_commands.Choice(name="no", value=0)
    ]
)
async def overwrite_list(inte: discord.Interaction, file: discord.Attachment, searching: discord.app_commands.Choice[int]):
    await inte.response.defer()
    if ("text/plain" == file.content_type.split(";")[0]):
        uid = str(inte.user.id)
        f.clear_binder_by_category(uid,searching.value,con,cur)
        filename = f"{uid}_cardListInput"
        await file.save(filename)
        listToAdd = open(filename, 'r')
        List = listToAdd.readlines()
        r = f.add_list(List,uid,searching.value,con,cur)
        await inte.followup.send(r)
    else:
        await inte.followup.send("file must be plain text file !")


@tree.command(name="clear", description="overwrite your binder by inserting a text file")
@discord.app_commands.choices(
    searching=[
        discord.app_commands.Choice(name="yes", value=1),
        discord.app_commands.Choice(name="no", value=0)
    ]
)
async def clear(inte: discord.Interaction, searching: discord.app_commands.Choice[int]):
    await inte.response.defer()
    uid = str(inte.user.id)
    if searching:
        message = f'sucessfuly cleared your binder of searched cards'
    else:
        message = f'sucessfuly cleared your binder of owned cards'
        
    x = f.clear_binder_by_category(uid,searching.value,con,cur)
    
    if x == -1:
        message = "error trying to clear your binder"
    await inte.followup.send(message)


@tree.command(name="add_list", description="add cards to your binder by inserting a text file")
@discord.app_commands.choices(
    searching=[
        discord.app_commands.Choice(name="yes", value=1),
        discord.app_commands.Choice(name="no", value=0)
    ]
)
async def add_list(inte: discord.Interaction, file: discord.Attachment, searching: discord.app_commands.Choice[int]):
    await inte.response.defer()
    if ("text/plain" == file.content_type.split(";")[0]):
        uid = str(inte.user.id)
        filename = f"{inte.user.id}_cardListInput"
        await file.save(filename)
        listToAdd = open(filename, 'r')
        List = listToAdd.readlines()
        r = f.add_list(List,uid,searching.value,con,cur)
        await inte.followup.send(r)
    else:
        await inte.followup.send("file must be plain text file !")




@tree.command(name="help", description="Show available commands and usage")
async def help(inte: discord.Interaction):
    embed = discord.Embed(
        title="Trade Wizard",
        description="These are the available commands for Trade Wizard Bot  ",
        color=discord.Color.blurple()
    )

   
    # Commands and descriptions
    commands = [
        ("`/add_card`", "add a single card to your binder."),
        ("`/remove_card`", "Remove a single card from your binder."),
        ("`/add_list`", "Add cards to your current list from a text file."),
        ("`/overwrite_list`", "Overwrite your current list with a new list from a text file."),
        ("`/clear`", "Clear all the cards in your binder."),
        ("`/look_for_trades`", "Look for trades with other users."),
        ("`/show_binder`", "Send you a message of your binder."),
        ("`/get_binder`", "Export your current binder as a file.")
    ]

    for name, value in commands:
        embed.add_field(name=name, value=value, inline=False)

    await inte.response.send_message(embed=embed)

@tree.command(name="lower_binder", description="if somehow he cards in your binder aren't lowered use that")
async def lower_binder(inte : discord.Interaction):
    await inte.response.defer()
    message : str 
    uid = str(inte.user.id)
    x = f.lower_binder(uid,con,cur)
    if x == 0:
        message = "succesfuly lowered your binder"
    else:
        message = "something wrong append ..."
    await inte.followup.send(message)
    


bot.run(token)
