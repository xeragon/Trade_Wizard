import discord
import requests
from discord.ext import commands
import fonction as f


token = "MTA0MTcxNTk3MzI1MTY2NjAwMg.GFmON8.UOOZ8K-6pW0oTQXVhaVw8jUaKLfkQ_MQ8MTrsY"
intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix="/", intents=intents)
tree = bot.tree
cards = f.open_json("cardName.json")["data"]


@bot.event
async def on_ready():

    await tree.sync()
    print("bot started")


async def get_user_name(user_id: int):
    user = await bot.fetch_user(user_id)
    return user.name


# la fonction d'update du fichier cardname est une solution temporaire avant que je fasse tourner le bot
# sur un serveur par la suite je lui ferais faire l'update tout seul tout les X temps

@tree.command(name="test_fetch_username")
async def fetch_user_name(inte: discord.Interaction):
    user_id = inte.user.id
    user = await bot.fetch_user(user_id)
    await inte.response.send_message(user.name)


@tree.command(name="update_cardname")
async def update_cardName(inte: discord.Interaction):
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
        await inte.response.send_message("update done")
    else:
        await inte.response.send_message("Only the owner can do this !")


@tree.command(name="get_binder")
async def get_binder(inte: discord.Interaction):
    binder = f.open_json("data.json")[str(inte.user.id)]

    wishKeys = list(binder["wish"])
    haveKeys = list(binder["have"])
    filename = f'{inte.user.name}Binder'
    with open(filename, "w") as file:
        file.write("/wish/")
        for x in wishKeys:
            file.write(f'\n{x}')
        file.write("\n\n/have/")
        for x in haveKeys:
            file.write(f'\n{x}')

    fileDiscord = discord.File(filename, filename="file.txt")
    user = await inte.user.create_dm()
    await user.send(file=fileDiscord)
    await inte.response.send_message("check your dm for the file")


@tree.command(name="look_for_trades")
async def look_for_trades(inte: discord.Interaction):
    dico = f.open_json("data.json")
    uid = str(inte.user.id)

    user_wishes = list(dico[user_id]["wish"])
    user_haves = list(dico[user_id]["have"])
    r = "here are the results \n"

    for x in dico:

        WishesFound = []
        HavesFound = []
        if x != user_id:
            current_have = list(dico[x]["have"])
            current_wish = list(dico[x]["wish"])
            for a in user_wishes:
                if a in current_have:
                    WishesFound.append(a)
                    for b in current_wish:
                        if b in user_haves:
                            HavesFound.append(b)

        print(f'{WishesFound}\n{HavesFound}')

        if len(WishesFound) != 0 and len(HavesFound) != 0:
            current_username = await get_user_name(int(x))
            r += f'\nyou can trade the following card(s) with {current_username} : '
            r += f'\n /you have/\n'
            r += ",".join(HavesFound)
            r += f'\n/{current_username} have/\n'
            r += ",".join(WishesFound)

    user = await inte.user.create_dm()
    await user.send(r)
    await inte.response.send_message("the trades option have been sent in your dm's")


@tree.command(name="overwrite_list", description="overwrite your binder by inserting a text file")
@discord.app_commands.choices(
    wish_or_have=[
        discord.app_commands.Choice(name="have", value="have"),
        discord.app_commands.Choice(name="wish", value="wish")
    ]
)
async def overwrite_list(inte: discord.Interaction, file: discord.Attachment, wish_or_have: discord.app_commands.Choice[str]):
    if ("text/plain" == file.content_type.split(";")[0]):
        filename = f"{inte.user.id}_cardListInput"
        await file.save(filename)
        cardName = f.open_json("cardName.json")["data"]
        listToAdd = open(filename, 'r')
        List = listToAdd.readlines()
        unknown_cards = []
        didRegister = False
        for line in List:

            if line[0] in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
                nb_card = int(line.split(" ", 1)[0])

                card_name = line.split(" ", 1)[1]
                card_name = card_name[0:len(card_name)-1]

                if card_name.lower() in cardName:

                    f.overwrite_data(card_name, nb_card,
                                  str(inte.user.id), wish_or_have.value)
                    didRegister = True
                else:
                    unknown_cards.append(card_name)

        if didRegister and len(unknown_cards) == 0:
            r = "all cards have been sucsesfully registered"
        elif didRegister:
            r = "cards have been sucsesfully registered but the following ones could not be found -> "
            r += ",".join(unknown_cards)
        else:
            r = "couldn't recognize any cards !"

        print(r)
        await inte.response.send_message(r)

    else:
        await inte.response.send_message("file must be plain text file !")


@tree.command(name="clear", description="overwrite your binder by inserting a text file")
@discord.app_commands.choices(
    wish_or_have=[
        discord.app_commands.Choice(name="have", value="have"),
        discord.app_commands.Choice(name="wish", value="wish")
    ]
)
async def clear(inte: discord.Interaction, wish_or_have: discord.app_commands.Choice[str]):
   dico = f.open_json("data.json")
   user_id = str(inte.user.id)
   dico[user_id][wish_or_have.value].clear()
   f.dump_json("data.json", dico)
   await inte.response.send_message("sucessfuly cleared your binder")



@tree.command(name="add_list", description="add cards to your binder by inserting a text file")
@discord.app_commands.choices(
    wish_or_have=[
        discord.app_commands.Choice(name="have", value="have"),
        discord.app_commands.Choice(name="wish", value="wish")
    ]
)
async def add_list(inte: discord.Interaction, file: discord.Attachment, wish_or_have: discord.app_commands.Choice[str]):
    if ("text/plain" == file.content_type.split(";")[0]):
        filename = f"{inte.user.id}_cardListInput"
        await file.save(filename)
        cardName = f.open_json("cardName.json")["data"]
        listToAdd = open(filename, 'r')
        List = listToAdd.readlines()
        unknown_cards = []
        didRegister = False
        for line in List:

            if line[0] in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
                nb_card = int(line.split(" ", 1)[0])

                card_name = line.split(" ", 1)[1]
                card_name = card_name[0:len(card_name)-1]

                if card_name.lower() in cardName:

                    f.insert_data(card_name, nb_card,
                                  str(inte.user.id), wish_or_have.value)
                    didRegister = True
                else:
                    unknown_cards.append(card_name)

        if didRegister and len(unknown_cards) == 0:
            r = "all cards have been sucsesfully registered"
        elif didRegister:
            r = "cards have been sucsesfully registered but the following ones could not be found -> "
            r += ",".join(unknown_cards)
        else:
            r = "couldn't recognize any cards !"

        print(r)
        await inte.response.send_message(r)

    else:
        await inte.response.send_message("file must be plain text file !")


@tree.command(name="remove_card")
@discord.app_commands.choices(
    wish_or_have=[
        discord.app_commands.Choice(name="have", value="have"),
        discord.app_commands.Choice(name="wish", value="wish")
    ]
)
async def remove_card(inte: discord.Interaction,  wish_or_have: discord.app_commands.Choice[str], card: str):
    user_id = str(inte.user.id)
    dico = f.open_json("data.json")
    if dico[user_id][wish_or_have.value][card]["nbr"] == 1:
        del dico[user_id][wish_or_have.value][card]
    else:
        dico[user_id][wish_or_have.value][card]["nbr"] -= 1

    f.dump_json("data.json", dico)

    await inte.response.send_message(f'{card} has been successfully removed from your wishlist')


@remove_card.autocomplete('card')
async def cards_autocomplete(inte: discord.Interaction, current: str) -> list[discord.app_commands.Choice[str]]:
    user_id = str(inte.user.id)
    default_cards = []
    key_list = list(f.open_json("data.json")[
                    user_id][inte.data["options"][0]["value"]])
    if len(key_list) > 25:
        default_cards = key_list[:24]
    else:
        default_cards = key_list

    if current == "":
        cards = default_cards
    else:
        cards = f.open_json("data.json")[
            user_id][inte.data["options"][0]["value"]]

    return [discord.app_commands.Choice(name=card, value=card) for card in cards if current in card][:25]


@tree.command(name="insert_card")
@discord.app_commands.choices(
    wish_or_have=[
        discord.app_commands.Choice(name="have", value="have"),
        discord.app_commands.Choice(name="wish", value="wish")
    ]
)
async def insert_card(inte: discord.Interaction, wish_or_have: discord.app_commands.Choice[str], card: str, nb: int):
    user_id = str(inte.user.id)

    f.insert_data(card, nb, user_id, wish_or_have.value)

    await inte.response.send_message(f'{card} has been sucessfuly added to your collection')


@insert_card.autocomplete('card')
async def cards_autocomplete(inte: discord.Interaction, current: str) -> list[discord.app_commands.Choice[str]]:
    user_id = str(inte.user.id)
    cardList = f.open_json("cardName.json")["data"]
    matching_cards = [card for card in cardList if current in card]
    first_25_cards = matching_cards[:25]
    return [discord.app_commands.Choice(name=card, value=card) for card in first_25_cards]


@tree.command(name="show_binder")
async def show_binder(inte: discord.Interaction):
    user_id = str(inte.user.id)
    wishCards = f.open_json("data.json")[user_id]["wish"]
    haveCards = f.open_json("data.json")[user_id]["have"]

    r = "you have the following cards in your binder : \n\n wanted cards : "

    for x in wishCards:
        r += f'\n - {x} : {wishCards[x]["nbr"]}'
    r += " \n\n cards you own :"
    for x in haveCards:
        r += f'\n - {x} : {haveCards[x]["nbr"]}'

    if len(r) > 1999:
        with open("binder.txt", "w", encoding="utf-8") as file:
            file.write(r)
        file = discord.File("binder.txt")
        user = await inte.user.create_dm()
        await user.send(file=file)
        await inte.response.send_message("Your binder has been sent to you via DM.")
    else:
        await inte.response.send_message(r)

@tree.command(name="help", description="Show available commands and usage")
async def help(inte: discord.Interaction):
    embed = discord.Embed(
        title="Trade Wizard",
        description="These are the available commands for Trade Wizard Bot  ",
        color=discord.Color.blurple()
    )

   

    # Commands and descriptions
    commands = [
        ("`/get_binder`", "Export your current binder as a file."),
        ("`/look_for_trades`", "Look for trades with other users."),
        ("`/overwrite_list`", "Overwrite your current list with a new list from a text file."),
        ("`/add_list`", "Add cards to your current list from a text file."),
        ("`/clear`", "Clear all the cards in your binder."),
        ("`/remove_card`", "Remove a single card from your binder."),
        ("`/show_binder`", "Send you a message of your binder."),
    ]

    for name, value in commands:
        embed.add_field(name=name, value=value, inline=False)

    await inte.response.send_message(embed=embed)

bot.run(token)
