#######################################################
# ################## IMPORTS ##########################
#######################################################
# Discord Imports
import discord
from discord import Embed
from discord.ext import commands,tasks
from pymysql.err import MySQLError
Embed = Embed()
# Time Imports
from datetime import datetime
import random
import time
# Google Translate Imports
from googletrans import Translator
translator = Translator()
# Getting Crypto Data Imports
from requests import Session
import json
# Database Imports
import pymysql
# Other Imports
import math

# ############## GLOBAL CONSTANTS #####################
# Base Colors
GREEN_COLOR_CODE=0x008000
YELLOW_COLOR_CODE=0xffbf00
RED_COLOR_CODE=0xe32636
DEFAULT_COLOR_CODE=0xff8800
#
# Embed Titles
CASINO_EMBED_TITLE = "Vitalio Kazino"
MINING_POOL_EMBED_TITLE = "Vitalio Mining Pool"
VITALIS_EXCHANGE_EMBED_TITLE = "Vitalio Exchange"
#
# Copyright Variable
DEV_COPYRIGHT = "© ꜱᴛʀᴇᴄʜᴇᴅʀᴇꜱᴏʟᴜᴛɪᴏɴ"


# ######### MYSQL LOGIN & CMCAP API URL ###############
# MySQL
conn = pymysql.connect(host='eu-cdbr-west-02.cleardb.net', user='b814698b1e141b', passwd='638323b1', db='heroku_e06421f6f04ce8a')
#cursor=db.cursor(pymysql.cursors.DictCursor)

#
# CoinMarketCap
url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"


# ################ LIST DEFINITIONS ###################
# BlackJack
bjackUserIds = []
bjackNames = []
bjackDisplays = []
bjackValues = []
bjackTimes = []
bjackChannelIds = []
bjackDealerDisplays = []
bjackDealerValues = []
bjackAvatarUrl = []
bjackBetValues = []
bjackBuvo11 = []
bjackDealerBuvo11 = []
bjackMessageId = []
#
# CryptoCurrency Mining
miningChannelIds = []
miningServerId = []
miningMessageIds = []
miningUserIds = []
miningAts = []
miningAtsValue = []
miningReward = []
miningCoinName = []
miningAvatarUrl = []
miningThumbLinks = []
miningTimes = []


# Setting up discord bot variable, prefix, etc.
client = discord.Client()
intents = discord.Intents().all()
client = commands.Bot(command_prefix="vitali ", intents=intents)


# ########################################## FUNCTION BLOCK ############################################
# ############# DATABASE FUNCTIONS ####################

def database_insert_userinfo(user_server_id, user_id, user_name, user_money, user_xp, user_last_time_mined):
    connection = pymysql.connect(host='eu-cdbr-west-02.cleardb.net', user='b814698b1e141b', passwd='638323b1', db='heroku_e06421f6f04ce8a',cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()
    sql=f"""INSERT INTO `user_info`(user_server_id, user_id, user_name, user_money, user_xp, `user_last-time-mined`)
        VALUES (%s, %s, %s, %s, %s, %s)"""
    val = (user_server_id, user_id, user_name, user_money, user_xp, user_last_time_mined)
    try:
        cursor.execute(sql, val)
        connection.commit()
        connection.close()
    except pymysql.Error:
        connection.rolback()
        connection.close()
#
# Function inserts data in database's `user_info-crypto_balances` table
def database_insert_userinfocrypto(user_server_id, user_id, user_name, btc, eth, ltc, doge):
    connection = pymysql.connect(host='eu-cdbr-west-02.cleardb.net', user='b814698b1e141b', passwd='638323b1', db='heroku_e06421f6f04ce8a',cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()
    sql=f"""INSERT INTO `user_info-crypto_balances`(user_server_id, user_id, user_name, user_balance_btc, user_balance_eth, user_balance_ltc, user_balance_doge)
        VALUES (%s, %s, %s, %s, %s, %s, %s)"""
    val = (user_server_id, user_id, user_name, btc, eth, ltc, doge)
    try:
        cursor.execute(sql, val)
        connection.commit()
        connection.close()
    except pymysql.Error:
        connection.rolback()
        connection.close()
#
# Function updates data in database
def database_update(table, user_id, server_id, set_what, set_value):
    connection = pymysql.connect(host='eu-cdbr-west-02.cleardb.net', user='b814698b1e141b', passwd='638323b1', db='heroku_e06421f6f04ce8a',cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()
    sql = f"UPDATE `{table}` SET `{set_what}` = %s WHERE `user_id` = %s AND `user_server_id`=%s"
    val = (set_value, user_id, server_id)
    cursor.execute(sql, val)
    connection.commit()
    connection.close()
#
# Function returns whole specified table's information
def database_read(table):
    connection = pymysql.connect(host='eu-cdbr-west-02.cleardb.net', user='b814698b1e141b', passwd='638323b1', db='heroku_e06421f6f04ce8a',cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()

    sql = f"SELECT * FROM `{table}`"
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        connection.close()
        return results
    except MySQLError as e:
        print('Got error {!r}, errno is {}'.format(e, e.args[0]))


# ################ BOT FUNCTIONS ######################
# Function checks how much time passed since last time user mined crypto currency
def cryptoCheckTime(dbObj, user_server_id, user_id):
    time = -1
    if(len(dbObj)==0): # If database is empty, returning -1
        return -1

    for user in dbObj: # Getting every user from database
        if user['user_id'] == user_id and user['user_server_id'] == user_server_id: # Checking if user is requested user
            return user['user_last-time-mined'] # Returning last time user mined crypto currencies
    
    return time # If user not found, returning -1
#
# Function updates last time when specific user mined crypto currency
def cryptoUpdateTime(user_server_id, user_id, time):
    # Updating database's table user_info
    database_update("user_info", user_id, user_server_id, "user_last-time-mined", time)
#
# Function updates one crypto coin balance of a specific user
def update_crypto(user_server_id, user_id, cryptoname, amount):
    # Assigning column name by provided argument
    if(cryptoname=="btc"):
        set_what = "user_balance_btc"
    elif(cryptoname=="eth"):
        set_what = "user_balance_eth"
    elif(cryptoname=="ltc"):
        set_what = "user_balance_ltc"
    elif(cryptoname=="doge"):
        set_what = "user_balance_doge"


    # Updating database's table user_info-crypto_balances
    database_update("user_info-crypto_balances", user_id, user_server_id, set_what, amount)
#
# Function returns value of provided user's, one crypto coin balance
def view_crypto(dbObj, user_server_id, user_id, cryptoname):
    for user in dbObj: # Getting every user from database
        if user['user_id'] == user_id and user['user_server_id'] == user_server_id: # Checking if user is required user
            # Returning crypto balance, by provided argument
            if(cryptoname=="btc"):
                return user['user_balance_btc']
            elif(cryptoname=="eth"):
                return user['user_balance_eth']
            elif(cryptoname=="doge"):
                return user['user_balance_doge']
            elif(cryptoname=="ltc"):
                return user['user_balance_ltc']
#
# Function checks if user exists in both database's tables, and if not, fills it with zero values
def check_if_user_exists_and_fill_ifnot(dbObj, cryptoDbObj, user_server_id, user_id, username):
    # Checking with `user_info` table
    dbase = dbObj
    user_found = False # Variable, which indicates if user has been found
    for user in dbase: # Getting every user from databse
        if user['user_id'] == user_id and user['user_server_id']==user_server_id: # Checking if user is required user
            user_found = True
            break
    if(not user_found): # Checking if user hasn't been found
        database_insert_userinfo(user_server_id, user_id, username, 0.0, 0, 0.0) # Pushing data into `user_info` table, with zero values

    #time.sleep(0.1)

    # Checking with `user_info-crypto_balances` table
    dbase = cryptoDbObj
    user_found = False # Variable, which indicates if user has been found
    for user in dbase: # Getting every user from databse
        if user['user_id'] == user_id and user['user_server_id']==user_server_id: # Checking if user is required user
            user_found = True
            break
    if(not user_found): # Checking if user hasn't been found
        database_insert_userinfocrypto(user_server_id, user_id, username, 0.0, 0.0, 0.0, 0.0) # Pushing data into `user_info` table, with zero values
    
    return
#
# Function updates provided user's money balance
def update_money(user_server_id, user_id, money):
    database_update("user_info", user_id, user_server_id, "user_money", money)
    return
#
# Function returns money balance, of provided user
def view_money(dbObj, user_server_id, user_id):
    for user in dbObj: # Getting every user in `user_info` table
        if user['user_id'] == user_id and user['user_server_id'] == user_server_id: # Checking if user is required user
            return user['user_money'] # Returning that user's money balance

def view_user_xp(dbObj, user_server_id, user_id):
    for user in dbObj: # Getting every user in `user_info` table
        if user['user_id'] == user_id and user['user_server_id'] == user_server_id: # Checking if user is required user
            return user['user_xp'] # Returning that user's xp

def update_user_xp(user_server_id, user_id, xp):
    database_update("user_info", user_id, user_server_id, "user_xp", xp)
    return



# ################ OTHER FUNCTIONS ####################
# Function returns random greeting
def random_pasisveikinimas():
    variant = random.randrange(0,2)
    current_time = datetime.now().strftime("%H")
    current_time = int(current_time)

    if(variant==0):
        if(current_time>=3 and current_time<=9):
            return "Labas rytas"
        elif(current_time >= 10 and current_time <=18):
            return "Laba diena"
        else:
            return "Labas vakaras"

    return "Laba"
#
# Function returns provided string made to 40char length, filling it with empty spaces
def make40len(str):
    ilg = len(str)
    for i in range(ilg, 40):
        str = str + " "
    
    return str
#
# Function returns provided string made to 2char length, filling it with empty space
def make2len(num):
    digits = int(math.log10(num))+1
    if(digits == 1):
        num = str(num) + " "
    
    return num
#
# Function returns random mathematical problem
def random_math_problem():
    element_amount = random.randrange(5, 8)
    operation = ""

    for i in range(0, element_amount):
        num = str(random.randrange(1, 100))
        random.seed(time.time()+random.randrange(-1000, 1000))
        operator = random.randrange(0, 3)
        if(operator==0):
            operator="+"
        elif(operator==1):
            operator="-"
        elif(operator==2):
            operator="*"
        operation = f"{operation}{num}"

        if(i!=element_amount-1):
            operation = f"{operation}{operator}"
    
    return operation
#
# Function returns random math operator except '/' (*,+,-)
def random_operator():
    random.seed(time.time()+random.randrange(-1000, 1000))
    operator = random.randrange(0, 2)
    if(operator==0):
        operator="+"
    elif(operator==1):
        operator="-"

    return operator
#
# Function returns specific crypto currency price, by live market prices
def GetCryptoPrice(symbol):
    parameters = {
        'symbol':symbol.upper(),
        'convert':'EUR'
    }

    headers ={
        'Accepts':'application/json',
        'X-CMC_PRO_API_KEY':'32abd44b-d3a2-4978-85fd-4726cf4deab6'
    }

    session = Session()
    session.headers.update(headers)

    response = session.get(url, params = parameters)
    #print(symbol.upper()+": "+str(json.loads(response.text)['data'][symbol.upper()]['quote']['EUR']['price']))
    return json.loads(response.text)['data'][symbol.upper()]['quote']['EUR']['price']



# ############################################## TASKS #################################################
@tasks.loop(seconds = 1) # Task repeats every 1 second
async def bjacksys60sTikrinimas():
    
    if(len(bjackTimes) == 0):
        return
    
    poz = 0
    for laikas in bjackTimes:
        if(time.time()-laikas >=60):

            embed=discord.Embed(title=CASINO_EMBED_TITLE, description=f"Praėjus 60s. žaidėjas {bjackNames[poz].display_name.capitalize()} neatliko veiksmų, todėl žaidimas baigiamas.", color=0x000000)
            embed.set_author(name=bjackNames[poz].display_name, icon_url=bjackAvatarUrl[poz])
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/912225748977332225/913855024117989386/external-content.duckduckgo.jpg")

            embed.set_footer(text=f"Norėdamas žaisti rašyk: vitali bjack [statymo suma]\n\n{DEV_COPYRIGHT}")
            await bjackChannelIds[poz].send(embed=embed)

            bjackChannelIds.pop(poz)
            bjackUserIds.pop(poz)
            bjackNames.pop(poz)
            bjackDisplays.pop(poz)
            bjackValues.pop(poz)
            bjackTimes.pop(poz)
            bjackDealerDisplays.pop(poz)
            bjackDealerValues.pop(poz)
            bjackAvatarUrl.pop(poz)
            bjackBetValues.pop(poz)
            bjackMessageId.pop(poz)

        poz += 1
    return
#
@tasks.loop(seconds = 5) # Task repeats every 1 second
async def miningsys60sTikrinimas():
    
    if(len(miningTimes) == 0):
        return
    

    dbObject = database_read("user_info-crypto_balances")
    poz = 0
    for laikas in miningTimes:
        if(time.time()-laikas >=60):
            embed=discord.Embed(title=MINING_POOL_EMBED_TITLE, description=f"{client.get_user(miningUserIds[poz]).name.capitalize()} nespėjo išspręsti užduoties.", color=0x2beac0)
            embed.set_author(name=client.get_user(miningUserIds[poz]).name, icon_url=miningAvatarUrl[poz])
            embed.set_thumbnail(url=miningThumbLinks[poz])

            embed.add_field(name=f"Rezultatas", value=f"Užduotis **neįvykdyta** laiku.", inline=False)
            embed.add_field(name=f"Dabartinis {miningCoinName[poz].upper()} balansas:", value=f"{view_crypto(dbObject, miningServerId[poz], miningUserIds[poz], miningCoinName[poz])}", inline=False)
            embed.set_footer(text=f"Artimiausiu metu kripto valiutas galėsi kasti po 5min.\n\n{DEV_COPYRIGHT}")
            await client.get_channel(miningChannelIds[poz]).send(embed=embed)

            
            miningChannelIds.pop(poz)
            miningServerId.pop(poz)
            miningMessageIds.pop(poz)
            miningUserIds.pop(poz)
            miningAts.pop(poz)
            miningAtsValue.pop(poz)
            miningReward.pop(poz)
            miningCoinName.pop(poz)
            miningAvatarUrl.pop(poz)
            miningThumbLinks.pop(poz)
            miningTimes.pop(poz)

        poz += 1
#
#
# Setting up primary crypto currency prices, before entering loop which checks it every 10secs
btc_kaina = GetCryptoPrice('btc')
time.sleep(0.2)
eth_kaina = GetCryptoPrice('eth')
time.sleep(0.2)
doge_kaina = GetCryptoPrice('doge')
time.sleep(0.2)
ltc_kaina = GetCryptoPrice('ltc')
#
# Loop which checks live crypto currency prices every 10secs
@tasks.loop(seconds = 120) # Task repeats every 120 seconds
async def cryptorate():
    global btc_kaina, eth_kaina, doge_kaina, ltc_kaina
    btc_kaina = GetCryptoPrice('btc')
    time.sleep(0.2)
    eth_kaina = GetCryptoPrice('eth')
    time.sleep(0.2)
    doge_kaina = GetCryptoPrice('doge')
    time.sleep(0.2)
    ltc_kaina = GetCryptoPrice('ltc')
    return





# ############################################# EVENTS #################################################
# Bot event, which gets triggered, when bot gets loaded and comes online
@client.event
async def on_ready():
    # Greeting message, to make sure, that bot is online
    print(f'Logged in as {client.user}')

    # Starting tasks
    bjacksys60sTikrinimas.start()
    miningsys60sTikrinimas.start()
    cryptorate.start()
#
@client.event
async def on_message(message):
    if message.author != client.user: # Checks if message sender is not bot itself
        databaseObject = database_read("user_info")
        cryptoDatabaseObject = database_read("user_info-crypto_balances")

        user_guild_id = message.guild.id
        user_id = message.author.id
        user_xp = view_user_xp(databaseObject, user_guild_id, user_id)
        user_display_name = message.author.display_name
        user_mention = message.author.mention


        check_if_user_exists_and_fill_ifnot(databaseObject, cryptoDatabaseObject, user_guild_id, user_id, user_display_name)

        if(message.content.startswith(f"vitali ")):
            update_user_xp(user_guild_id, user_id, user_xp+20)
        else:
            update_user_xp(user_guild_id, user_id, user_xp+10)


        content_lower = message.content.lower() # Lowers whole message to make easier if statements
        if(content_lower == "sveiki"): # Checks if user greets

            await message.channel.send(f"{random_pasisveikinimas()}, {user_mention}!") # Sending random greeting
        
    await client.process_commands(message) # Function that allows use commands and on_message event at the same time
#
@client.event
async def on_reaction_add(reaction, user):
    if(len(miningMessageIds)==0 and len(bjackMessageId)==0):
        return
    

    reaction_added_on_bjack_msg = False
    reaction_added_on_mining_msg = False
    if(len(bjackMessageId)!=0):
        for msgid in bjackMessageId:
            if(msgid==reaction.message.id):
                reaction_added_on_bjack_msg=True
                break

    if(len(miningMessageIds)!=0):
        for msgid in miningMessageIds:
            if(msgid==reaction.message.id):
                reaction_added_on_mining_msg=True
                break
 

    if(reaction_added_on_bjack_msg):
        if(reaction.emoji=="🟩"):# Traukiu
            poz = 0
            message = reaction.message.id
            
            for msg in bjackMessageId:
                if(msg==message and bjackUserIds[poz]==user.id):
                    username = client.get_user(bjackUserIds[poz])
                    # ====================================== BlackJack System Starts ============================================
                    bjackTimes[poz] = time.time()
                    random.seed(time.time()+random.randrange(0,random.randrange(500,1000)))
                    new_card = random.randrange(2,12)

                    if(bjackBuvo11[poz]):
                        random.seed(time.time()+random.randrange(0,random.randrange(500,1000)))
                        new_card = random.randrange(2,11)
                    elif(not bjackBuvo11[poz] and new_card==11):
                        bjackBuvo11[poz] = True

                    if(new_card == 11 and bjackValues[poz] > 10):
                        new_card = 1
                    
                    
                    bjackValues[poz] += new_card
                    bjackDisplays[poz] = f"{bjackDisplays[poz]} {str(new_card)}"

                    if(bjackValues[poz] > 21):
                        dbObject = database_read("user_info")
                        cryptodbObject = database_read("user_info-crypto_balances")
                        embed=discord.Embed(title=CASINO_EMBED_TITLE, description=f"{username.display_name.capitalize()} ištraukė vieną kortą blackjack'e.", color=RED_COLOR_CODE)
                        embed.set_author(name=username.display_name, icon_url=username.avatar_url)
                        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/912225748977332225/913855024117989386/external-content.duckduckgo.jpg")

                        embed.add_field(name=f"{username.display_name.capitalize()} ranka:", value=f"```{make40len(bjackDisplays[poz])}[{make2len(bjackValues[poz])}]```", inline=False)
                        embed.add_field(name="Dealer'io Vitalio ranka:", value=f"```{make40len(bjackDealerDisplays[poz])}[{make2len(bjackDealerValues[poz])}]```", inline=False)

                        #embed.add_field(name="Kazkieno ranka:", value=f"```{make40len(dealer_display)}[{dealer_hand}]```", inline=False)
                        embed.add_field(name="Statymo suma:", value=f"**{bjackBetValues[poz]}** eur.", inline=False)
                        embed.add_field(name="Rezultatas:", value=f"Pralošei.", inline=False)
                        embed.add_field(name="Sąskaitos balansas:", value=f"{round(view_money(dbObject, reaction.message.guild.id, username.id),4)} eur.", inline=False)


                        embed.set_footer(text=f"Norėdamas žaisti iš naujo rašyk: vitali bjack [statymo suma]\n\n{DEV_COPYRIGHT}")
                        await reaction.message.channel.send(embed=embed)


                        bjackChannelIds.pop(poz)
                        bjackUserIds.pop(poz)
                        bjackNames.pop(poz)
                        bjackDisplays.pop(poz)
                        bjackValues.pop(poz)
                        bjackTimes.pop(poz)
                        bjackDealerDisplays.pop(poz)
                        bjackDealerValues.pop(poz)
                        bjackAvatarUrl.pop(poz)
                        bjackBetValues.pop(poz)
                        bjackMessageId.pop(poz)
                        return

                    embed=discord.Embed(title=CASINO_EMBED_TITLE, description=f"{username.display_name.capitalize()} ištraukė vieną kortą blackjack'e.", color=0x000000)
                    embed.set_author(name=username.display_name, icon_url=username.avatar_url)
                    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/912225748977332225/913855024117989386/external-content.duckduckgo.jpg")

                    embed.add_field(name=f"{username.display_name.capitalize()} ranka:", value=f"```{make40len(bjackDisplays[poz])}[{make2len(bjackValues[poz])}]```", inline=False)
                    embed.add_field(name="Dealer'io Vitalio ranka:", value=f"```{make40len(bjackDealerDisplays[poz])}[{make2len(bjackDealerValues[poz])}]```", inline=False)

                    #embed.add_field(name="Kazkieno ranka:", value=f"```{make40len(dealer_display)}[{dealer_hand}]```", inline=False)

                    embed.add_field(name="Statymo suma:", value=f"**{bjackBetValues[poz]}** eur.", inline=False)

                    embed.set_footer(text=f"Norėdamas traukti sekančią kortą, rašyk: vitali traukiu\nNenorint traukti sekančios kortos, rašyk: vitali nebetraukiu\n(Turi 60s)\n\n{DEV_COPYRIGHT}")
                    messageid = await reaction.message.channel.send(embed=embed)
                    await messageid.add_reaction("🟩") # Green button
                    await messageid.add_reaction("🟥") # Red button
                    bjackMessageId[poz] = messageid.id

                    # ====================================== BlackJack System Ends ============================================

                    break
        elif(reaction.emoji=="🟥"):# Nebetraukiu
            poz = 0
            message = reaction.message.id
            #print(reaction.message.author)
            #print(user.id)
            
            for msg in bjackMessageId:
                if(msg==message and bjackUserIds[poz]==user.id):
                    dbObject = database_read("user_info")
                    cryptodbObject = database_read("user_info-crypto_balances")
                    username = client.get_user(bjackUserIds[poz])

                    # ====================================== BlackJack System Starts ============================================
                    bjackTimes[poz] = time.time()
                    if(bjackDealerValues[poz]==bjackValues[poz]):
                        random.seed(time.time()+random.randrange(0,random.randrange(500,1000)))
                        new_card = random.randrange(2,12)
                        if(bjackDealerBuvo11[poz] and new_card==11):
                            random.seed(time.time()+random.randrange(0,random.randrange(500,1000)))
                            new_card = random.randrange(2,11)
                        elif(not bjackDealerBuvo11[poz] and new_card==11):
                            bjackDealerBuvo11[poz] = True

                        if(new_card == 11 and bjackDealerValues[poz] > 10):
                            new_card = 1

                        bjackDealerDisplays[poz] = f"{bjackDealerDisplays[poz]} {str(new_card)}"
                        bjackDealerValues[poz] += new_card

                    while(bjackValues[poz]>bjackDealerValues[poz] or bjackDealerValues[poz]<17):
                        random.seed(time.time()+random.randrange(0,random.randrange(500,1000)))
                        new_card = random.randrange(2,12)
                        if(bjackDealerBuvo11[poz] and new_card==11):
                            random.seed(time.time()+random.randrange(0,random.randrange(500,1000)))
                            new_card = random.randrange(2,11)
                        elif(not bjackDealerBuvo11[poz] and new_card==11):
                            bjackDealerBuvo11[poz] = True

                        if(new_card == 11 and bjackDealerValues[poz] > 10):
                            new_card = 1

                        bjackDealerDisplays[poz] = f"{bjackDealerDisplays[poz]} {str(new_card)}"
                        bjackDealerValues[poz] += new_card
                    

                    player_money = view_money(dbObject, reaction.message.guild.id, username.id)
                    player_new_money = player_money

                    if(bjackDealerValues[poz]>21 or bjackDealerValues[poz]<bjackValues[poz]):
                        res_msg = "Laimėjai"
                        embed_color = GREEN_COLOR_CODE
                        player_new_money = player_money+bjackBetValues[poz]*2
                    elif(bjackDealerValues[poz] == bjackValues[poz]):
                        res_msg = "Lygiosios"
                        embed_color = YELLOW_COLOR_CODE
                        player_new_money = player_money+bjackBetValues[poz]
                    else:
                        res_msg = "Pralaimėjai"
                        embed_color = RED_COLOR_CODE
                        player_new_money = player_money

                    update_money(reaction.message.guild.id, username.id, player_new_money)

                    embed=discord.Embed(title=CASINO_EMBED_TITLE, description=f"{username.display_name.capitalize()} nustojo traukti kortas.", color=embed_color)
                    embed.set_author(name=username.display_name, icon_url=username.avatar_url)
                    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/912225748977332225/913855024117989386/external-content.duckduckgo.jpg")

                    embed.add_field(name=f"{username.display_name.capitalize()} ranka:", value=f"```{make40len(bjackDisplays[poz])}[{make2len(bjackValues[poz])}]```", inline=False)
                    embed.add_field(name="Dealer'io Vitalio ranka:", value=f"```{make40len(bjackDealerDisplays[poz])}[{make2len(bjackDealerValues[poz])}]```", inline=False)


                    embed.add_field(name="Statymo suma:", value=f"**{bjackBetValues[poz]}** eur.", inline=False)
                    embed.add_field(name="Rezultatas:", value=res_msg, inline=False)
                    embed.add_field(name="Sąskaitos balansas:", value=f"{round(player_new_money,4)} eur.", inline=False)
                    embed.set_footer(text=f"Norėdamas žaisti iš naujo rašyk: vitali bjack [statymo suma]\n\n{DEV_COPYRIGHT}")
                    await reaction.message.channel.send(embed=embed)
                    
                    bjackChannelIds.pop(poz)
                    bjackNames.pop(poz)
                    bjackUserIds.pop(poz)
                    bjackDisplays.pop(poz)
                    bjackValues.pop(poz)
                    bjackTimes.pop(poz)
                    bjackDealerDisplays.pop(poz)
                    bjackDealerValues.pop(poz)
                    bjackAvatarUrl.pop(poz)
                    bjackBetValues.pop(poz)
                    bjackMessageId.pop(poz)
                    # ====================================== BlackJack System Ends ============================================
                    break
        
    elif(reaction_added_on_mining_msg):
        # Mining reaction added system
        poz = 0
        message = reaction.message.id
        #print(reaction.message.author)
        #print(user.id)

        for msg in miningMessageIds:
            if(msg==message and miningUserIds[poz]==user.id):
                dbObject = database_read("user_info")
                cryptodbObject = database_read("user_info-crypto_balances")
                if(reaction.emoji == "🇦"):
                    choice = "a"
                elif(reaction.emoji == "🇧"):
                    choice = "b"
                elif(reaction.emoji == "🇨"):
                    choice = "c"
                elif(reaction.emoji == "🇩"):
                    choice = "d"

                if(miningAts[poz]==choice):
                    check_if_user_exists_and_fill_ifnot(dbObject, cryptodbObject, reaction.message.guild.id, int(user.id), user.name)
                    current_crypto_quantity = view_crypto(cryptodbObject, reaction.message.guild.id, user.id, miningCoinName[poz])
                    update_crypto(reaction.message.guild.id, user.id, miningCoinName[poz], current_crypto_quantity+miningReward[poz])

                    # Embed message
                    embed=discord.Embed(title=MINING_POOL_EMBED_TITLE, description=f"{user.name.capitalize()} išsprendė užduotį.", color=GREEN_COLOR_CODE)
                    embed.set_author(name=user.name, icon_url=miningAvatarUrl[poz])
                    embed.set_thumbnail(url=miningThumbLinks[poz])

                    embed.add_field(name=f"Rezultatas", value=f"Užduotis įvykdyta **teisingai**", inline=False)
                    embed.add_field(name=f"Dabartinis {miningCoinName[poz].upper()} balansas:", value=f"{current_crypto_quantity+miningReward[poz]}", inline=False)

                    embed.set_footer(text=f"Artimiausiu metu kripto valiutas galėsi kasti po 5min.\n\n{DEV_COPYRIGHT}")
                    messageid = await reaction.message.channel.send(embed=embed)
                else:
                    check_if_user_exists_and_fill_ifnot(dbObject, cryptodbObject, reaction.message.guild.id, int(user.id), user.name)
                    current_crypto_quantity = view_crypto(cryptodbObject, reaction.message.guild.id, user.id, miningCoinName[poz])

                    # Embed message
                    embed=discord.Embed(title=MINING_POOL_EMBED_TITLE, description=f"{user.name.capitalize()} išsprendė užduotį.", color=RED_COLOR_CODE)
                    embed.set_author(name=user.name, icon_url=miningAvatarUrl[poz])
                    embed.set_thumbnail(url=miningThumbLinks[poz])

                    embed.add_field(name=f"Rezultatas", value=f"Užduotis įvykdyta **neteisingai**", inline=False)
                    embed.add_field(name=f"Dabartinis {miningCoinName[poz].upper()} balansas:", value=f"{current_crypto_quantity}", inline=False)

                    embed.set_footer(text=f"Artimiausiu metu kripto valiutas galėsi kasti po 5min.\n\n{DEV_COPYRIGHT}")
                    messageid = await reaction.message.channel.send(embed=embed)
                
                miningChannelIds.pop(poz)
                miningServerId.pop(poz)
                miningMessageIds.pop(poz)
                miningUserIds.pop(poz)
                miningAts.pop(poz)
                miningAtsValue.pop(poz)
                miningReward.pop(poz)
                miningCoinName.pop(poz)
                miningAvatarUrl.pop(poz)
                miningThumbLinks.pop(poz)
                miningTimes.pop(poz)

            poz += 1
    


# ############################################ COMMANDS ################################################
#
## ################ CASINO SYSTEM ######################
# Coin Flip Command
@client.command(name = "moneta", description = "Su Vitaliu meta monetą")
async def moneta(ctx, user_rez, kiek):
    dbObject = database_read("user_info")
    cryptodbObject = database_read("user_info-crypto_balances")

    # Tikriname ar user'is gerai ivede parametrus
    if(user_rez!="herbas" and user_rez!="skaicius" and not kiek.isdigit()):
        await ctx.channel.send("Blogas formatas. Gali rinktis tik tarp **skaičiaus** ir **herbo**, bei statymo suma **gali būti tik teigiamas skaičius**.")
        return
    elif(user_rez!="herbas" and user_rez!="skaicius"):
        await ctx.channel.send("Blogas formatas. Gali rinktis tik tarp **skaičiaus** ir **herbo**.")
        return
    elif(not kiek.isdigit()):
        await ctx.channel.send("Blogas formatas. Norima statymo suma **gali būti tik skaičius**.")
        return

    check_if_user_exists_and_fill_ifnot(dbObject, cryptodbObject, ctx.message.guild.id, ctx.author.id, ctx.author)
    kiek = int(kiek)
    current_money = view_money(dbObject, ctx.message.guild.id, ctx.author.id)

    # Tikriname ar user'is turi pakankamai pinigu zaisti moneta
    if(current_money<kiek):
        await ctx.channel.send(f"**Neturi** pakankamai **eurų**, kad žaistum monetą su Vitaliu. (**{current_money}**/{kiek})")
        return

    if(kiek==0):
        await ctx.channel.send("Negali žaisti monetos iš 0 eurų.")    
        return


    await ctx.message.delete()


    # Israndomise'inam iskrito herbas ar skaicius
    skaicius_herbas = random.randrange(0,2) # Generuojam 1 arba 0, 0-herbas; 1-skaicius

    # Convertinam ivesta statyma i 0 arba 1, 0-herbas; 1-skaicius
    if(user_rez == "herbas"):
        user_rez = 0
    else:
        user_rez = 1

    # Israndomise'inam Vitalis pasirinko herba ar skaiciu
    vit_rez = random.randrange(0,2) # Generuojam 1 arba 0, 0-herbas; 1-skaicius
    # Tikrinam ar vitalio pasirinkimas yra toks pats kaip userio, ir jei taip, tai pritaikom 50/50 tikimybe ar 
    # vitaliui priskirs priesinga reiksme,ar paliks lygiasias
    if(vit_rez==user_rez):
        tikimybe = random.randrange(1,11)
        if(tikimybe>2):
            # Switchinam
            if(user_rez==0):
                vit_rez=1
            else:
                vit_rez=0
    
    if(kiek==1 or kiek%10==1):
        valiuta1="euro"
        valiuta2="eurą"
    else:
        valiuta1="eurų"
        valiuta2="eurų"

    
    new_money = current_money

    
    # Tikriname rezultata ir priskiriam ji kintamajam result, bei pagal tai priskiriam embed zinutes border spalva
    if(skaicius_herbas == vit_rez and skaicius_herbas != user_rez):
        result = f"Vitaliui **pralaimėjai** {kiek} {valiuta2}."
        embed_color = RED_COLOR_CODE
        update_money(ctx.message.guild.id, ctx.author.id, current_money-kiek)
        thumb_link = "https://cdn.discordapp.com/attachments/912225748977332225/914549549543080006/litas_minus.png"
        new_money = current_money-kiek
    elif(skaicius_herbas == user_rez and skaicius_herbas != vit_rez):
        result = f"Iš Vitalio **laimėjai** {kiek} {valiuta2}."
        embed_color = GREEN_COLOR_CODE
        update_money(ctx.message.guild.id, ctx.author.id, current_money+kiek)
        thumb_link = "https://cdn.discordapp.com/attachments/912225748977332225/914549549958328370/litas_pliusas.png"
        new_money = current_money+kiek
    elif(skaicius_herbas != user_rez and skaicius_herbas != vit_rez):
        result = f"Abu pasirinkote į apačią atsivertusią pusę, todėl **niekas nelaimėjo**."
        embed_color = YELLOW_COLOR_CODE
        thumb_link = "https://cdn.discordapp.com/attachments/912225748977332225/914549549312380929/litas_lygu.png"
    else:
        result = f"Abu pasirinkote į viršų atsivertusią pusę, todėl **niekas nelaimėjo**. "
        embed_color = YELLOW_COLOR_CODE
        thumb_link = "https://cdn.discordapp.com/attachments/912225748977332225/914549549312380929/litas_lygu.png"

    # Paverciam 1-tus ir 0-lius i zodzius
    if(skaicius_herbas==0):
        skaicius_herbas = "Herbas"
    else:
        skaicius_herbas = "Skaičius"
    #--
    if(vit_rez==0):
        vit_rez = "Herbas"
    else:
        vit_rez = "Skaičius"
    #--
    if(user_rez==0):
        user_rez = "Herbas"
    else:
        user_rez = "Skaičius"
    
    
    # Isvedam rezultatus i embed zinute
    embed=discord.Embed(title=CASINO_EMBED_TITLE, description=f"{ctx.message.author.display_name.capitalize()} su Vitaliu metė monetą iš {kiek} {valiuta1}.", color=embed_color)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    embed.set_thumbnail(url=thumb_link)

    embed.add_field(name=f"{ctx.message.author.display_name.capitalize()} pozicija", value=f"{user_rez}", inline=True)
    embed.add_field(name="Vitalio pozicija", value=f"{vit_rez}", inline=True)
    embed.add_field(name="Iškrito", value=f"{skaicius_herbas}", inline=False)
    embed.add_field(name="Rezultatas", value=f"{result}", inline=False)
    #\u200b
    embed.add_field(name="\u200b", value=f"\u200b", inline=False)
    embed.add_field(name="Balansas", value=f"Sąskaitos balansas: **{round(new_money,4)}**eur.", inline=False)

    embed.set_footer(text=f"Norėdamas žaisti rašyk vitali moneta [skaicius/herbas] [statymo suma]\n\n{DEV_COPYRIGHT}")

    await ctx.channel.send(embed=embed)
@moneta.error
async def moneta(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
            await ctx.channel.send("**Klaida.** Formatas: **vitali moneta [skaicius/herbas] [statymo suma]**")
    print(error)
#
# BlackJack Command
@client.command(name="bjack", description="Su Vitaliu žaidi blackjack'ą")
async def bjack(ctx, *args):
    if(len(args) != 1):
        await ctx.channel.send("Blogas formatas. Norint žaisti blackjack'ą, rašyk: **vitali bjack [statymo suma]**")
        return
    elif(not args[0].isdigit()):
        await ctx.channel.send("Blogas formatas. Statymo suma gali būti tik **skaičiai**, kurie yra **teigiami**.")
        return

    bet = args[0]

    dbObject = database_read("user_info")
    cryptodbObject = database_read("user_info-crypto_balances")

    user_found = False
    for name in bjackNames:
        if(name == ctx.author):
            user_found = True
            break
    if(user_found):
        await ctx.channel.send("Jau žaidi blackjack'ą, norėdamas traukti/netraukti sekančios kortos rašyk: vitali traukiu/nebetraukiu.")
        return
    
    if(int(bet)==0):
        await ctx.channel.send("Negali žaisti blackjack'o iš 0 eurų.")    
        return


    bet = int(bet)
    player_money = view_money(dbObject, ctx.message.guild.id, ctx.message.author.id)
    if(bet>player_money):
        await ctx.channel.send(f"Neturi pakankamai pinigų žaisti blackjacką pas dealer'į Vitalį. (**{player_money}**/{bet})")
        return
    

    update_money(ctx.message.guild.id, ctx.author.id, player_money-int(bet))

    random.seed(time.time()+random.randrange(0,random.randrange(500,1000)))
    dhand1=random.randrange(2,12)
    random.seed(time.time()+random.randrange(0,random.randrange(500,1000)))
    dhand2=random.randrange(2,11)
    random.seed(time.time()+random.randrange(0,random.randrange(500,1000)))
    uhand1=random.randrange(2,12)
    random.seed(time.time()+random.randrange(0,random.randrange(500,1000)))
    uhand2=random.randrange(2,11)

    if(uhand1==11):
        bjackBuvo11.append(True)
    else:
        bjackBuvo11.append(False)

    if(dhand1==11):
        bjackDealerBuvo11.append(True)
    else:
        bjackDealerBuvo11.append(False)

    




    dealer_hand = dhand1 + dhand2 # Sudedam dvi pirmas dealer'io kortas (2-11)
    user_hand = uhand1 + uhand2 # Sudedam dvi pirmas user'io kortas (2-11)
    
    dealer_display = f"{dhand1} {dhand2}"
    user_display = f"{uhand1} {uhand2}"

    bjackNames.append(ctx.author)
    bjackUserIds.append(ctx.author.id)
    bjackDisplays.append(user_display)
    bjackValues.append(user_hand)
    bjackTimes.append(time.time())
    bjackChannelIds.append(ctx.channel)
    bjackAvatarUrl.append(ctx.author.avatar_url)
    bjackDealerDisplays.append(dealer_display)
    bjackDealerValues.append(dealer_hand)
    bjackBetValues.append(bet)

    #await ctx.channel.send(f"Vitalio hand: {dhand1}, {dhand2} | {dealer_hand}")
    #await ctx.channel.send(f"User'io hand: {uhand1}, {uhand2} | {user_hand}")

    embed=discord.Embed(title=CASINO_EMBED_TITLE, description=f"{ctx.message.author.display_name.capitalize()} žaidžia blackjack'ą.", color=0x000000)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/912225748977332225/913855024117989386/external-content.duckduckgo.jpg")

    embed.add_field(name=f"{ctx.message.author.display_name.capitalize()} ranka:", value=f"```{make40len(user_display)}[{make2len(user_hand)}]```", inline=False)
    embed.add_field(name="Dealer'io Vitalio ranka:", value=f"```{make40len(dealer_display)}[{make2len(dealer_hand)}]```", inline=False)

    #embed.add_field(name="Kazkieno ranka:", value=f"```{make40len(dealer_display)}[{dealer_hand}]```", inline=False)

    embed.add_field(name="Statymo suma:", value=f"**{bet}** eur.", inline=False)

    embed.set_footer(text=f"Norėdamas traukti sekančią kortą, spausk žalią mygtuką.\nNenorint traukti sekančios kortos, spausk raudoną mygtuką.\n(Turi 60s)\n\n{DEV_COPYRIGHT}")
    messageid = await ctx.channel.send(embed=embed)
    bjackMessageId.append(messageid.id)
    await messageid.add_reaction("🟩") # Green button
    await messageid.add_reaction("🟥") # Red button

    return
@bjack.error
async def bjack(ctx, error):
    await ctx.channel.send(f"**Klaida.** Formatas: *vitali bjack [statymo suma]*")
    return
#
# Rulette Command

@client.command(name="rulete", description="Su Vitaliu žaidi ruletę")
async def rulete(ctx, *args):
    
    bet_value = int(args[1])
    choice = args[0]
    juodi = [0,0,1,0,1,0,1,0,1,0,1,1,0,1,0,1,0,1,0,0,1,0,1,0,1,0,1,0,1,1,0,1,0,1,0,1,0]
    random.seed(time.time()+random.randrange(-1000,1000))
    spinned_num = random.randrange(0, 37)
    payout_multiplier = 2
    if(choice.isdigit()):
        if(int(choice) == spinned_num):
            await ctx.channel.send("Laimejai")
        else:
            await ctx.channel.send("Pralaimejai")
    if(choice == "lyginis"):
        if(spinned_num%2==0):
            await ctx.channel.send("Laimejai")
        else:
            await ctx.channel.send("Pralaimejai")
    elif(choice == "nelyginis"):
        if(spinned_num%2!=0):
            await ctx.channel.send("Laimejai")
        else:
            await ctx.channel.send("Pralaimejai")
    elif(choice == "juodas"):
        if(juodi[spinned_num]):
            await ctx.channel.send("Laimejai")
        else:
            await ctx.channel.send("Pralaimejai")
    elif(choice == "raudonas"):
        if(not juodi[spinned_num] and spinned_num != 0):
            await ctx.channel.send("Laimejai")
        else:
            await ctx.channel.send("Pralaimejai")
    elif(choice == "zalias"):
        payout_multiplier = 35
        if(spinned_num==0):
            await ctx.channel.send("Laimejai")
        else:
            await ctx.channel.send("Pralaimejai")
    
    if(juodi[spinned_num]):
        color = "juoda"
    elif(spinned_num==0):
        color = "žalia"
    elif(not juodi[spinned_num]):
        color = "raudona"
    
    payout = bet_value*payout_multiplier

    # Embed message
    embed=discord.Embed(title=CASINO_EMBED_TITLE, description=f"{ctx.author.name.capitalize()} su Vitaliu pradėjo žaisti ruletę.", color=RED_COLOR_CODE)
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/912225748977332225/916807080088842382/external-content.duckduckgo.jpg")

    embed.add_field(name=f"{ctx.author.name.capitalize()} statymas: ", value=f"{choice.capitalize()}", inline=True)
    embed.add_field(name=f"Statymo suma:", value=f"{bet_value} eur.", inline=True)
    #\u200b
    embed.add_field(name=f"\u200b", value="\u200b", inline=False)
    embed.add_field(name=f"Iškrito skaičius: ", value=f"{spinned_num}", inline=True)
    embed.add_field(name=f"Iškrito spalva", value=f"{color.capitalize()}", inline=True)

    embed.set_footer(text=f"Norėdamas žaisti ruletę rašyk: vitali rulete [statymas] [statymo suma]\n\n{DEV_COPYRIGHT}")
    await ctx.channel.send(embed=embed)
#
#
## ################## MONEY SYSTEM #####################
# Give Money As Vitalis Command
@client.command()
async def duokpinigu(ctx, username: discord.Member, kiek):
    if ctx.author.id != 446698255791816704:
        await ctx.channel.send("Neturi privilegijų šiai komandai.")
        return
    elif not kiek.isdigit():
        await ctx.channel.send("Blogas formatas. Pinigų kiekis **gali būti tik teigiamas skaičius**.")
        return
    
    kiek = int(kiek)

    dbObject = database_read("user_info")
    cryptodbObject = database_read("user_info-crypto_balances")

    check_if_user_exists_and_fill_ifnot(dbObject, cryptodbObject, ctx.message.guild.id, username.id, username)
    current_money = view_money(dbObject, ctx.message.guild.id, username.id)
    update_money(ctx.message.guild.id, username.id, current_money+kiek)

    await ctx.message.delete()
    embed=discord.Embed(title=CASINO_EMBED_TITLE, description=f"Vitalis davė pinigų vartotojui {username.mention}", color=GREEN_COLOR_CODE)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/912225748977332225/914549549958328370/litas_pliusas.png")

    embed.add_field(name=f"Buvusieji pinigai", value=f"{round(current_money,4)} eur.", inline=True)
    embed.add_field(name="Davė", value=f"{round(kiek,4)} eur.", inline=True)
    embed.add_field(name="Dabartinis balansas", value=f"{round(current_money+kiek,4)} eur.", inline=False)

    embed.set_footer(text=f"Norėdamas žaisti rašyk vitali moneta [skaicius/herbas] [statymo suma]\n\n{DEV_COPYRIGHT}")
    await ctx.channel.send(embed=embed)
@duokpinigu.error
async def atimkpinigus(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.channel.send("**Klaida**. Formatas: *vitali duokpinigu @MemberTag [kiekis]*")
        return
    elif isinstance(error, commands.MemberNotFound):
        await ctx.channel.send("**Klaida**. Vartotojas nerastas.")
        return
    print(error)
#
# Take Money As Vitalis Command
@client.command()
async def atimkpinigus(ctx, username: discord.Member, kiek):
    if ctx.author.id != 446698255791816704:
        await ctx.channel.send("Neturi privilegijų šiai komandai.")
        return
    elif not kiek.isdigit():
        await ctx.channel.send("Blogas formatas. Pinigų kiekis **gali būti tik teigiamas skaičius**.")
        return
    
    kiek = int(kiek)

    dbObject = database_read("user_info")
    cryptodbObject = database_read("user_info-crypto_balances")

    check_if_user_exists_and_fill_ifnot(dbObject, cryptodbObject, ctx.message.guild.id, username.id, username)
    current_money = view_money(dbObject, ctx.message.guild.id, username.id)
    if(current_money < kiek):
        await ctx.channel.send(f"Vartotojas neturi tiek pinigų. (**{current_money}**/{kiek})")
        return
    update_money(ctx.message.guild.id, username.id, current_money-kiek)


    await ctx.message.delete()
    embed=discord.Embed(title=CASINO_EMBED_TITLE, description=f"Vitalis atemė pinigus iš vartotojo {username.mention}", color=RED_COLOR_CODE)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/912225748977332225/914549549543080006/litas_minus.png")

    embed.add_field(name=f"Buvusieji pinigai", value=f"{round(current_money,4)} eur.", inline=True)
    embed.add_field(name="Atėmė", value=f"{round(kiek,4)} eur.", inline=True)
    embed.add_field(name="Dabartinis balansas", value=f"{round(current_money-kiek,4)} eur.", inline=False)

    embed.set_footer(text=f"Norėdamas žaisti rašyk vitali moneta [skaicius/herbas] [statymo suma]\n\n{DEV_COPYRIGHT}")
    await ctx.channel.send(embed=embed)
@atimkpinigus.error
async def atimkpinigus(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.channel.send("**Klaida**. Formatas: *vitali atimkpinigus @MemberTag [kiekis]*")
        return
    elif isinstance(error, commands.MemberNotFound):
        await ctx.channel.send("**Klaida**. Vartotojas nerastas.")
        return
    print(error)
#
# Set Money As Vitalis Command
@client.command()
async def uzsetinkpinigus(ctx, username: discord.Member, kiek):
    if ctx.author.id != 446698255791816704:
        await ctx.channel.send("Neturi privilegijų šiai komandai.")
        return
    elif not kiek.isdigit():
        await ctx.channel.send("Blogas formatas. Pinigų kiekis **gali būti tik teigiamas skaičius**.")
        return

    kiek = int(kiek)


    dbObject = database_read("user_info")
    cryptodbObject = database_read("user_info-crypto_balances")
    
    check_if_user_exists_and_fill_ifnot(dbObject, cryptodbObject, ctx.message.guild.id, username.id, username)
    current_money = view_money(dbObject, ctx.message.guild.id, username.id)
    update_money(ctx.message.guild.id, username.id, kiek)


    await ctx.message.delete()
    embed=discord.Embed(title=CASINO_EMBED_TITLE, description=f"Vitalis užset'ino vartotojo {username.mention} pinigus", color=YELLOW_COLOR_CODE)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/912225748977332225/914549549736026122/litas_nieko.png")

    embed.add_field(name=f"Buvusieji pinigai", value=f"{round(current_money,4)} eur.", inline=False)
    embed.add_field(name="Užset'intas pinigų kiekis", value=f"{round(kiek,4)} eur.", inline=False)

    embed.set_footer(text=f"Norėdamas žaisti rašyk vitali moneta [skaicius/herbas] [statymo suma]\n\n{DEV_COPYRIGHT}")
    await ctx.channel.send(embed=embed)
@uzsetinkpinigus.error
async def uzsetinkpinigus(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.channel.send("**Klaida**. Formatas: *vitali uzsetinkpinigus @MemberTag [kiekis]*")
        return
    elif isinstance(error, commands.MemberNotFound):
        await ctx.channel.send("**Klaida**. Vartotojas nerastas.")
        return
    print(error)
#
# Give Money As A Player To Another Player Command
@client.command(name = "perduok", description = "Perduoda kitam vartotojui pinigus")
async def perduok(ctx, recipient: discord.Member, amount):
    dbObject = database_read("user_info")
    cryptodbObject = database_read("user_info-crypto_balances")

    giver_money = view_money(dbObject, ctx.message.guild.id, ctx.author.id) # Paziurim davejo pinigus user_info.json file
    recipient_money = view_money(dbObject, ctx.message.guild.id, recipient.id) # Paziurim gavejo pinigus user_info.json file
    if(giver_money < int(amount)): # Jeigu davėjas turi mažiau negu duoda, išmetama klaida
        await ctx.channel.send(f"Neturi pakankamai pinigų, kad duotum juos kitam vartotojui. (**{giver_money}**/{amount})")
        return
    
    # Priskaitome pinigus gavėjui, ir nuskaitome nuo davėjo sąskaitos
    recipient_new_money = recipient_money+int(amount)
    update_money(ctx.message.guild.id, recipient.id, recipient_new_money)
    update_money(ctx.message.guild.id, ctx.author.id, giver_money-int(amount))

    # Embed zinute
    embed=discord.Embed(title=CASINO_EMBED_TITLE, description=f"{ctx.author.display_name.capitalize()} davė pinigų vartotojui {recipient.mention}", color=DEFAULT_COLOR_CODE)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/912225748977332225/914947706273804328/perduok.jpg")

    embed.add_field(name=f"Buvęs gavėjo balansas:", value=f"{round(recipient_money,4)} eur.", inline=False)
    embed.add_field(name="Dabartinis gavėjo balansas:", value=f"{round(recipient_new_money,4)} eur.", inline=False)


    embed.add_field(name=f"Buvęs davėjo balansas:", value=f"{round(giver_money,4)} eur.", inline=False)
    embed.add_field(name="Dabartinis davėjo balansas:", value=f"{round(giver_money-int(amount),4)} eur.\n\u200b", inline=False)


    embed.add_field(name="Duoti pinigai:", value=f"{round(int(amount),4)} eur.", inline=False)

    embed.set_footer(text=f"Norėdamas perduoti pinigų rašyk vitali perduok @MemberTag [suma]\n\n{DEV_COPYRIGHT}")

    await ctx.channel.send(embed=embed)
@perduok.error
async def perduok(ctx, error):
    await ctx.channel.send(f"**Klaida.** Formatas: *vitali perduok [user tag] [kiekis]*")
    return
#
# Check Money Balance Command
@client.command(name = "kiekpinigu", description = "Parodo tavo sąskaitos balansą")
async def kiekpinigu(ctx):
    dbObject = database_read("user_info")
    cryptodbObject = database_read("user_info-crypto_balances")
    # Patikriname ar vartotojas egzistuoja duombazėje, pažiūrime jo pinigus su funkcija view_money() ir output'inam rezultatą
    check_if_user_exists_and_fill_ifnot(dbObject, cryptodbObject, ctx.message.guild.id, ctx.author.id, ctx.author.name)
    user_money = view_money(dbObject, ctx.message.guild.id, ctx.author.id)
    await ctx.channel.send(f"{ctx.author.display_name.capitalize()} banko sąskaitoje yra **{round(user_money,4)}** eur.")
    return
@kiekpinigu.error
async def kiekpinigu(ctx, error):
    await ctx.channel.send(f"**Klaida.** Įvyko klaida nuskaitant duomenis. || {client.get_user(446698255791816704).mention} ||")
    return
#
# LeaderBoard Command
@client.command(name="lenta", description="Parodo daugiausiai pinigų turinčius vartotojus")
async def lenta(ctx):
    dbObject = database_read("user_info")

    all_users_info = sorted(dbObject, key=lambda d: d['user_money'], reverse=True)
    
    numeracija = 1
    res_msg = ""

    all_member_ids = []



    for member in ctx.guild.members:
        all_member_ids.append(member.id)

    for user_info in all_users_info:

        skippinti = True
        for usr_id in all_member_ids:
            if(usr_id == user_info.get("user_id")):
                skippinti = False
                break
        if ctx.message.guild.id != user_info['user_server_id']: skippinti = True
        if(skippinti): continue

        username = client.get_user(user_info['user_id']).name
        #print(f"{numeracija}. {username} {user_info['money']}")
        res_msg += f"**{numeracija}.** {username.capitalize()} | {round(user_info['user_money'],4)} eur.\n"
        numeracija += 1
        if(numeracija>10):
            break


    
    embed=discord.Embed(title=CASINO_EMBED_TITLE, color=DEFAULT_COLOR_CODE)
    embed.add_field(name = "Leaderboard", value=res_msg, inline=False)
    embed.set_footer(text=f"\u200b\n{DEV_COPYRIGHT}")
    await ctx.channel.send(embed=embed)
@lenta.error
async def lenta(ctx, error):
    #await ctx.channel.send(f"**Klaida.** Įvyko klaida nuskaitant duomenis. || {client.get_user(446698255791816704).mention} ||")
    print(error)
    return
#
#
## ################# CRYPTO SYSTEM #####################
# Crypto Mining Command
@client.command(name="cryptomine", description="Pradedi kasti kriptovaliutas")
async def cryptomine(ctx, *args):
    dbObject = database_read("user_info")
    cryptodbObject = database_read("user_info-crypto_balances")


    # Checking if any arguments were given, and if not, print a bad format message and return
    if(not len(args)==1):
        await ctx.channel.send("**Blogas formatas.** Norint mininti, rašyk: *vitali cryptomine [coin name]*")
        return
    
    # Checking which cryptocurrency was specified, and by it assigning values for further operations
    # If neither of them was specified, sending error message and returning
    if(args[0]=="btc"):
        reward = random.uniform(0.0005, 0.001)
        kripto = "BTC"
        thumb_link = "https://cdn.discordapp.com/attachments/912225748977332225/914521559811645500/btc.jpg"
        # Reward between 0.0005 and 0.001
        # Between 30eur. and 60eur.
        # Rewards in euros are calculated by BTC cryptocurrency price as 60'000eur.
    elif(args[0]=="eth"):
        reward = random.uniform(0.01, 0.025)
        kripto = "ETH"
        thumb_link = "https://cdn.discordapp.com/attachments/912225748977332225/914521560654684210/eth.png"
        # Reward between 0.01 and 0.025
        # Between 30eur. and 75eur.
        # Rewards in euros are calculated by ETH cryptocurrency price as 3'000eur.
    elif(args[0]=="doge"):
        reward = random.uniform(150, 400)
        kripto = "DOGE"
        thumb_link = "https://cdn.discordapp.com/attachments/912225748977332225/914521560302374952/doge.jpg"
        # Reward between 150 and 400
        # Between 30eur. and 80eur.
        # Rewards in euros are calculated by DOGE cryptocurrency price as 0.2eur.
    elif(args[0]=="ltc"):
        reward = random.uniform(0.2, 0.4)
        kripto = "LTC"
        thumb_link = "https://cdn.discordapp.com/attachments/912225748977332225/914521561216725012/ltc.jpg"
        # Reward between 0.2 and 0.4
        # Between 40eur and 80eur
        # Rewards in euros are calculated by LTC cryptocurrency price as 200eur.
    else:
        await ctx.channel.send("**Klaida.** Negali kasti tokios kripto valiutos.")
        return
    
    # Checking if enough time (5 mins.) passed since last crypto mine
    # If not enough time passed, printing error message and returning
    user_last_time_mined = cryptoCheckTime(dbObject, ctx.message.guild.id, ctx.author.id)
    if(time.time()-user_last_time_mined<=300):
        await ctx.channel.send(f"Dar negali kasti kriptovaliutų. Liko: **{int((300-(round(time.time()-user_last_time_mined)))/60)}**min. **{(300-(round(time.time()-user_last_time_mined)))%60}**sek.")
        return
    
    # Assigning current time value for 60 seconds check, if user pressed the button
    miningTimes.append(time.time())
    

    # Checking if user exists in database, and if not, filling it with default values, which are specified in this function
    check_if_user_exists_and_fill_ifnot(dbObject, cryptodbObject, ctx.message.guild.id, ctx.author.id, ctx.author.name)

    # Assigning current time value for 5 minutes check, if user can mine crypto again
    cryptoUpdateTime(ctx.message.guild.id, ctx.author.id, time.time())

    # Mining reaction emojis, with which bot will react later on itself message
    reactions = ["🇦", "🇧", "🇨", "🇩"]

    # Generating random math problem, and assigning answer to it
    math_problem = random_math_problem()
    ats = eval(math_problem)

    # Requesting random seed based on current time, and another random number from -1000 to 1000
    random.seed(time.time()+random.randrange(-1000, 1000))
    # Randomizing, and assinging value, of correct answer choice (A/B/C/D)
    variantas = random.randrange(1,5) # 1 - 4
    # Assigning interval start and finish based on true answer (For false answers)
    ats0=ats-abs(ats)
    ats1=ats+abs(ats)

    # Checking which choice was generated, and assigning a,b,c,d values based on it
    # Before every randomizing, requesting random seed based on current time and another random numer between 500 and 1000
    # At the end, appending correct choice to a list, for further operations
    if(variantas==1):
        a=ats
        random.seed(time.time()+random.randrange(500,1000))
        b = random.randrange(ats0,ats1)
        while(b==ats):
            b= random.randrange(ats0,ats1)
        random.seed(time.time()+random.randrange(500,1000))
        c= random.randrange(ats0,ats1)
        while(c==ats):
            c= random.randrange(ats0,ats1)
        random.seed(time.time()+random.randrange(500,1000))
        d= random.randrange(ats0,ats1)
        while(d==ats):
            d = random.randrange(ats0,ats1)
        miningAts.append("a")
    elif(variantas==2):
        random.seed(time.time()+random.randrange(500,1000))
        a= random.randrange(ats0,ats1)
        while(a==ats):
            a= random.randrange(ats0,ats1)
        b=ats
        random.seed(time.time()+random.randrange(500,1000))
        c= random.randrange(ats0,ats1)
        while(c==ats):
            c = random.randrange(ats0,ats1)
        random.seed(time.time()+random.randrange(500,1000))
        d= random.randrange(ats0,ats1)
        while(d==ats):
            d= random.randrange(ats0,ats1)
        miningAts.append("b")
    elif(variantas==3):
        random.seed(time.time()+random.randrange(500,1000))
        a= random.randrange(ats0,ats1)
        while(a==ats):
            a= random.randrange(ats0,ats1)
        random.seed(time.time()+random.randrange(500,1000))
        b= random.randrange(ats0,ats1)
        while(b==ats):
            b= random.randrange(ats0,ats1)
        c=ats
        random.seed(time.time()+random.randrange(500,1000))
        d= random.randrange(ats0,ats1)
        while(d==ats):
            d = random.randrange(ats0,ats1)
        miningAts.append("c")
    elif(variantas==4):
        random.seed(time.time()+random.randrange(500,1000))
        a= random.randrange(ats0,ats1)
        while(a==ats):
            a= random.randrange(ats0,ats1)
        random.seed(time.time()+random.randrange(500,1000))
        b= random.randrange(ats0,ats1)
        while(b==ats):
            b = random.randrange(ats0,ats1)
        random.seed(time.time()+random.randrange(500,1000))
        c= random.randrange(ats0,ats1)
        while(c==ats):
            c = random.randrange(ats0,ats1)
        d=ats
        miningAts.append("d")
    
    # Appending all required values to lists, for further operations
    miningAtsValue.append(ats)
    miningChannelIds.append(ctx.channel.id)
    miningServerId.append(ctx.message.guild.id)
    miningReward.append(reward)
    miningUserIds.append(ctx.author.id)
    miningCoinName.append(args[0])
    miningAvatarUrl.append(ctx.author.avatar_url)
    miningThumbLinks.append(thumb_link)

    # Embed Message
    embed=discord.Embed(title=MINING_POOL_EMBED_TITLE, description=f"{ctx.message.author.display_name.capitalize()} pradėjo kasti **{kripto}**.", color=DEFAULT_COLOR_CODE)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    embed.set_thumbnail(url=thumb_link)
    embed.add_field(name=f"Įvykdytos operacijos atlygis:", value=f"{reward} {kripto.lower()}.", inline=False)
    embed.add_field(name="Užduotis:", value=f"`{math_problem}`", inline=False)
    embed.add_field(name="Galimi atsakymai:", value=f"**A)** {a}\n**B)** {b}\n**C)** {c}\n**D)** {d}", inline=False)
    embed.set_footer(text=f"Norėdamas pasirinkti teisingą atsakymą, spausk A/B/C/D apačioje.\nTuri 1 minutę atsakymui pateikti.\n\n{DEV_COPYRIGHT}")
    messageid = await ctx.channel.send(embed=embed)
    miningMessageIds.append(messageid.id)
    # Going through all reactions, and adding it on sent embed message (By bot)
    for emoji in reactions:
        await messageid.add_reaction(emoji)
@cryptomine.error
async def cryptomine(ctx, error):
    await ctx.channel.send(f"**Klaida.** Formatas: *vitali cryptomine [coin name]*")
    return
#
# Check Crypto Price Command
@client.command(name="cryptokaina", description="Gali pasižiūrėti norimos kriptovaliutos kainą Vitalio keitykloje")
async def cryptokaina(ctx, *args):
    # Checking if only one argument was given
    # If not, sending error message and returning
    if(not len(args)==1):
        await ctx.channel.send("Blogas formatas. Norint tikrinti kainą, rašyk: **vitali cryptokaina [coin name]**")
        return
    
    # Checking if argument was one of the crypto names
    # And if not, sending error message and returning
    if(args[0] != "btc" and args[0] != "eth" and args[0] != "btc" and args[0] != "doge" and args[0] != "ltc"):
        await ctx.channel.send("Tokios kripto valiutos Vitalio keitykloje nėra.")
        return

    # Assigning primary result value to:
    res = f"Šiuo metu **{args[0].upper()}** kaina Vitalio exchange yra **"

    # Based oncryptocurrency, appending result string with price
    if(args[0]=="btc"):
        res = res+str(btc_kaina)
    elif(args[0]=="eth"):
        res = res+str(eth_kaina)
    elif(args[0]=="doge"):
        res = res+str(doge_kaina)
    elif(args[0]=="ltc"):
        res = res+str(ltc_kaina)
    
    # Appending result string with fiat currency name (eur)
    res = res + "** eur."

    # Sending message and returning
    await ctx.channel.send(res)
    return
@cryptokaina.error
async def cryptokaina(ctx, error):
    await ctx.channel.send(f"**Klaida.** Formatas: *vitali cryptokaina [coin name]*")
    return
#
# Check Crypto Balance Command
@client.command(name="cryptobalansas", description="Gali pasižiūrėti savo kripto valiutų saskaitos balansą")
async def cryptobalansas(ctx):
    dbObject = database_read("user_info")
    cryptodbObject = database_read("user_info-crypto_balances")


    check_if_user_exists_and_fill_ifnot(dbObject, cryptodbObject, ctx.message.guild.id, ctx.author.id, ctx.author.name)
    embed=discord.Embed(title=VITALIS_EXCHANGE_EMBED_TITLE, description=f"{ctx.message.author.display_name.capitalize()} paprašė parodyti savo kriptovaliutų balansą.", color=DEFAULT_COLOR_CODE)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/912225748977332225/915347947414225006/cryptocoins.jpg")

    embed.add_field(name=f"BTC: ", value=f"`{round(view_crypto(cryptodbObject, ctx.message.guild.id, ctx.author.id, 'btc'),4)}`", inline=False)
    embed.add_field(name="ETH:", value=f"`{round(view_crypto(cryptodbObject, ctx.message.guild.id, ctx.author.id, 'eth'),4)}`", inline=False)
    embed.add_field(name="DOGE:", value=f"`{round(view_crypto(cryptodbObject, ctx.message.guild.id, ctx.author.id, 'doge'),4)}`", inline=False)
    embed.add_field(name="LTC:", value=f"`{round(view_crypto(cryptodbObject, ctx.message.guild.id, ctx.author.id, 'ltc'),4)}`", inline=False)

    embed.set_footer(text=f"Norėdamas mininti kripto valiutas, rašyk: vitali cryptomine [coin name]\nNorint keisti kriptovaliutas, rašyk: vitali cryptotrade [iš] [į] [kiekis]\n\n{DEV_COPYRIGHT}")
    await ctx.channel.send(embed=embed)
@cryptobalansas.error
async def cryptobalansas(ctx, error):
    await ctx.channel.send(f"**Klaida.** Įvyko klaida nuskaitant duomenis. || {client.get_user(446698255791816704).mention} ||")
    return
#
# Trade CryptoCurrencies Command
@client.command(name="cryptotrade", description="Gali gali keisti kriptovaliutas į kitas kriptovaliutas, kriptovaliutas į eurus, arba atvirkščiai.")
async def cryptotrade(ctx, *args):
    if(len(args) != 3):
        await ctx.channel.send("Netinkamas formatas. Norint keisti kripto valiutas, rašyk: vitali trade [iš] [į] [kiekis]")
        return

    dbObject = database_read("user_info")
    cryptodbObject = database_read("user_info-crypto_balances")

    first_arg_is_not_currency = args[0] != "eur" and args[0] != "btc" and args[0] != "eth" and args[0] != "doge" and args[0] != "ltc"
    second_arg_is_not_currency = args[1] != "eur" and args[1] != "btc" and args[1] != "eth" and args[1] != "doge" and args[1] != "ltc"

    if(first_arg_is_not_currency and second_arg_is_not_currency):
        await ctx.channel.send(f'Negali prekiauti tokiomis valiutomis kaip **{args[0]}** ir **{args[1]}**.')
        return
    elif(first_arg_is_not_currency):
        await ctx.channel.send(f'Negali prekiauti tokia valiuta kaip **{args[0]}**.')
        return
    elif(second_arg_is_not_currency):
        await ctx.channel.send(f'Negali prekiauti tokia valiuta kaip **{args[1]}**.')
        return



    is_crypto = args[0]
    i_crypto = args[1]
    kiekis = round(float(args[2]), 10)
    current_money = view_money(dbObject, ctx.message.guild.id, ctx.author.id)

    if(is_crypto == i_crypto):
        await ctx.channel.send("Negali keisti valiutos į tokią pačią.")
        return

    if(is_crypto=="eur"):
        if(current_money<kiekis):
            await ctx.channel.send(f"Neturi pakankamai pinigų, jog galėtum juos keisti į kripto valiutas. (**{round(current_money,4)}**/{kiekis})")
            return
    elif(view_crypto(cryptodbObject, ctx.message.guild.id, ctx.author.id, is_crypto)<kiekis):
        await ctx.channel.send(f"Neturi pakankamai kriptovaliutos, jog galėtum jas iškeisti. (**{round(view_crypto(cryptodbObject, ctx.message.guild.id, ctx.author.id, is_crypto),4)}**/{kiekis})")
        return

    # Sriftai
    if(is_crypto == "btc"):
        is_crypto_bold = "𝐁𝐓𝐂"
    elif(is_crypto == "eth"):
        is_crypto_bold = "𝐄𝐓𝐇"
    elif(is_crypto == "doge"):
        is_crypto_bold = "𝐃𝐎𝐆𝐄"
    elif(is_crypto == "ltc"):
        is_crypto_bold = "𝐋𝐓𝐂"
    elif(is_crypto == "eur"):
        is_crypto_bold = "𝐄𝐔𝐑"

    if(i_crypto == "btc"):
        i_crypto_bold = "𝐁𝐓𝐂"
    elif(i_crypto == "eth"):
        i_crypto_bold = "𝐄𝐓𝐇"
    elif(i_crypto == "doge"):
        i_crypto_bold = "𝐃𝐎𝐆𝐄"
    elif(i_crypto == "ltc"):
        i_crypto_bold = "𝐋𝐓𝐂"
    elif(i_crypto == "eur"):
        i_crypto_bold = "𝐄𝐔𝐑"
    
    
    if(is_crypto=="eur"):
        current_money = view_money(dbObject, ctx.message.guild.id, ctx.author.id)

        current_crypto = view_crypto(cryptodbObject, ctx.message.guild.id, ctx.author.id, i_crypto)


        #timestamp = int(datetime.datetime(2021, 1, 1, 15, 14).timestamp())
        #crypto_unit_price = retriever.get_closest_price(i_crypto.upper(), 'EUR', timestamp)
        crypto_unit_price = GetCryptoPrice(i_crypto)

        kiek_iseis_crypto = kiekis/crypto_unit_price
        priskaityta = kiek_iseis_crypto # For output

        update_money(ctx.message.guild.id, ctx.author.id, current_money-kiekis)

        update_crypto(ctx.message.guild.id, ctx.author.id, i_crypto, current_crypto+kiek_iseis_crypto)

        is_balansas = current_money-kiekis # For output
        i_balansas = current_crypto+kiek_iseis_crypto # For output
        #print(f"Buve eur: {current_money}\nDabartiniai eur: {view_money(ctx.author.id)}\nBuves crypto balansas: {current_crypto}\nDabartinis crypto balansas: {view_crypto(ctx.author.id, i_crypto)}")
    elif(i_crypto=="eur"):
        current_money = view_money(dbObject, ctx.message.guild.id, ctx.author.id)

        current_crypto = view_crypto(cryptodbObject, ctx.message.guild.id, ctx.author.id, is_crypto)

        #timestamp = int(datetime.datetime(2021, 1, 1, 15, 14).timestamp())
        #crypto_unit_price = retriever.get_closest_price(is_crypto.upper(), 'EUR', timestamp)

        crypto_unit_price = GetCryptoPrice(is_crypto)

        kiek_iseis_eur = kiekis*crypto_unit_price
        priskaityta = kiek_iseis_eur # For output

        update_money(ctx.message.guild.id, ctx.author.id, current_money+kiek_iseis_eur)

        update_crypto(ctx.message.guild.id, ctx.author.id, is_crypto, current_crypto-kiekis)

        i_balansas = current_money+kiek_iseis_eur # For output
        is_balansas = current_crypto-kiekis # For output
    else:
        current_crypto_is = view_crypto(cryptodbObject, ctx.message.guild.id, ctx.author.id, is_crypto)

        current_crypto_i = view_crypto(cryptodbObject, ctx.message.guild.id, ctx.author.id, i_crypto)


        #crypto_unit_price_is = retriever.get_closest_price(is_crypto.upper(), 'EUR', timestamp)
        crypto_unit_price_is = GetCryptoPrice(is_crypto)
    
        #crypto_unit_price_i = retriever.get_closest_price(i_crypto.upper(), 'EUR', timestamp)
        crypto_unit_price_i = GetCryptoPrice(i_crypto)

        kiek_iseis_crypto = (kiekis*crypto_unit_price_is)/crypto_unit_price_i

        priskaityta = kiek_iseis_crypto # For output


        update_crypto(ctx.message.guild.id, ctx.author.id, is_crypto, current_crypto_is-kiekis)
        update_crypto(ctx.message.guild.id, ctx.author.id, i_crypto, current_crypto_i+kiek_iseis_crypto)


        i_balansas = current_crypto_i+kiek_iseis_crypto # For output
        is_balansas = current_crypto_is-kiekis # For output




    embed=discord.Embed(title=VITALIS_EXCHANGE_EMBED_TITLE, description=f"{ctx.message.author.display_name.capitalize()} iškeitė valiutas.", color=DEFAULT_COLOR_CODE)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/912225748977332225/915655913598246953/external-content.duckduckgo.jpg")

    res = f"𝐈𝐬̌: {is_crypto.upper()}\n𝐈̨: {i_crypto.upper()}\n\n𝐍𝐮𝐬𝐤𝐚𝐢𝐭𝐲𝐭𝐚: {round(kiekis,4)} {is_crypto.lower()}.\n𝐏𝐫𝐢𝐬𝐤𝐚𝐢𝐭𝐲𝐭𝐚: {round(priskaityta,4)} {i_crypto.lower()}.\n\n𝐃𝐚𝐛𝐚𝐫𝐭𝐢𝐧𝐢𝐬 {is_crypto_bold} 𝐛𝐚𝐥𝐚𝐧𝐬𝐚𝐬: {round(is_balansas,4)}\n𝐃𝐚𝐛𝐚𝐫𝐭𝐢𝐧𝐢𝐬 {i_crypto_bold} 𝐛𝐚𝐥𝐚𝐧𝐬𝐚𝐬: {round(i_balansas,2)}"

    embed.add_field(name=f"\u200b", value=f"```{res}```", inline=False)
    embed.set_footer(text=f"\u200b\n{DEV_COPYRIGHT}")

    

    await ctx.channel.send(embed=embed)
    return
@cryptotrade.error
async def cryptotrade(ctx, error):
    await ctx.channel.send(f"**Klaida.** Formatas: *vitali cryptotrade [iš] [į] [kiekis]*")
    print(error)
    return
#
# LeaderBoard By Crypto Assets Command
@client.command(name="cryptolenta", description="Parodo vartotojus, kurie turi daugiausiai kriptovaliutų. (Pagal EUR vertę)")
async def cryptolenta(ctx):
    current_guild_id = ctx.message.guild.id
    res = ""
    users_by_value = []
    cryptodbObject = database_read("user_info-crypto_balances")
    #dbObject = database_read("user_info")
    all_member_ids = []

    for user in cryptodbObject:
        if user['user_server_id'] == current_guild_id:
            value = 0
            value += user['user_balance_btc']*btc_kaina
            value += user['user_balance_eth']*eth_kaina
            value += user['user_balance_doge']*doge_kaina
            value += user['user_balance_ltc']*ltc_kaina

            users_by_value.append({'user_id':user['user_id'], 'value':value})

    users_sorted = sorted(users_by_value, key=lambda d: d['value'], reverse=True)

    numeracija = 1
    for user in users_sorted:
        username = client.get_user(user.get("user_id"))
        btc_value = view_crypto(cryptodbObject, current_guild_id, user['user_id'], "btc")
        eth_value = view_crypto(cryptodbObject, current_guild_id, user['user_id'], "eth")
        doge_value = view_crypto(cryptodbObject, current_guild_id, user['user_id'], "doge")
        ltc_value = view_crypto(cryptodbObject, current_guild_id, user['user_id'], "ltc")
        res = f"{res}**{numeracija}. **{username}\n`BTC: {round(btc_value,4)}\nETH: {round(eth_value,4)}\nDOGE: {round(doge_value,4)}\nLTC: {round(ltc_value,4)}`\n\n"
        numeracija += 1
        if(numeracija>10):
            break
    
    embed=discord.Embed(title=VITALIS_EXCHANGE_EMBED_TITLE, color=DEFAULT_COLOR_CODE)
    embed.add_field(name = "Crypto Leaderboard", value=res, inline=False)
    embed.set_footer(text=f"\u200b\n{DEV_COPYRIGHT}")
    await ctx.channel.send(embed=embed)
@cryptolenta.error
async def cryptolenta(ctx, error):
    await ctx.channel.send(f"**Klaida.** Įvyko klaida nuskaitant duomenis. || {client.get_user(446698255791816704).mention} ||")
    print(error)
    return
#
#
## #################### XP SYSTEM ######################
#
@client.command(name="kiekxp")
async def kiekxp(ctx):
    databaseObject = database_read("user_info")
    CryptoDatabaseObject = database_read("user_info-crypto_balances")

    check_if_user_exists_and_fill_ifnot(databaseObject, CryptoDatabaseObject, ctx.message.guild.id, ctx.message.author.id, ctx.message.author.display_name)
    await ctx.message.channel.send(f"{ctx.message.author.display_name.capitalize()} patirties kiekis: **{view_user_xp(databaseObject, ctx.message.guild.id, ctx.message.author.id)}xp.**")
#
@client.command(name="xplenta")
async def xplenta(ctx):
    dbObject = database_read("user_info")

    all_users_info = sorted(dbObject, key=lambda d: d['user_xp'], reverse=True)
    
    numeracija = 1
    res_msg = ""

    all_member_ids = []



    for member in ctx.guild.members:
        all_member_ids.append(member.id)

    for user_info in all_users_info:

        skippinti = True
        for usr_id in all_member_ids:
            if(usr_id == user_info.get("user_id")):
                skippinti = False
                break
        if ctx.message.guild.id != user_info['user_server_id']: skippinti = True
        if(skippinti): continue

        username = client.get_user(user_info['user_id']).name
        #print(f"{numeracija}. {username} {user_info['money']}")
        res_msg += f"**{numeracija}.** {username.capitalize()} | {round(user_info['user_xp'],4)} xp.\n"
        numeracija += 1
        if(numeracija>10):
            break


    
    embed=discord.Embed(title="Vitalio Draugai", color=DEFAULT_COLOR_CODE)
    embed.add_field(name = "XP Leaderboard", value=res_msg, inline=False)
    embed.set_footer(text=f"\u200b\n{DEV_COPYRIGHT}")
    await ctx.channel.send(embed=embed)
#
@client.command(name="setxp")
async def setxp(ctx, user: discord.Member, amount):
    if ctx.author.id != 446698255791816704:
        await ctx.channel.send("Neturi privilegijų šiai komandai.")
        return

    databaseObject = database_read("user_info")
    CryptoDatabaseObject = database_read("user_info-crypto_balances")
    check_if_user_exists_and_fill_ifnot(databaseObject, CryptoDatabaseObject, ctx.message.guild.id, user.id, user.display_name)
    update_user_xp(ctx.message.guild.id, user.id, int(amount))

    

#
## ################# OTHER SYSTEMS #####################
# Translate Command
@client.command(pass_context=True, name="isversk", description="Išverčia tekstą iš vienos kalbos į kitą")
async def isversk(ctx, *argv):
  kalba1 = argv[0]
  kalba2 = argv[1]
  tekstas1 = ' '.join(argv[2:])
  tekstas2 = translator.translate(tekstas1, src=kalba1, dest=kalba2).text
  await ctx.channel.send(tekstas2)
@isversk.error
async def isversk(ctx, error):
    await ctx.channel.send("**Klaida.** Formatas: *vitali isversk [iš] [į] [tekstas]*")
    return
#
# Deleting Messages By Amount Command
@client.command(name = "valyk", description = "Išvalo nurodytą kiekį žinučių")
async def valyk(ctx, kiek):
    if ctx.author.id != 446698255791816704:
        await ctx.channel.send("Neturi privilegijų šiai komandai.")
        return
    # Paverčiam duotą kiekį į int, nustatom laiką, kas kurį trinti žinutes ir jeigu yra 4 ir mažiau žinučių, nustatome, jog laikas yra 0, nes
    # Discord'o anti spam sistema veikia tiki iki 5 žinučių.
    kiek  = int(kiek)
    if(kiek>=100):
        await ctx.channel.send("**Klaida.** Per didelis norimų ištrinti žinučių kiekis.")
        return
    current = 0
    laikas = 0.4
    if kiek <= 4:
        laikas = 0

    # Triname žinutes, kol esamų pratrintų žinučių kiekis nepasiekia reikiamo
    while current <= kiek:
        await ctx.channel.purge(limit=1)
        time.sleep(laikas)
        current = current + 1
    current = 0

    # Tikriname kaip suformatuoti žodį "žinutė", ir output'inam.
    if(kiek==1):
        zin = "žinutę"
    elif(kiek%10==0):
        zin = "žinučių"
    else:
        zin = "žinutes"
    await ctx.channel.send(f"Išvaliau {kiek} {zin}.")
@valyk.error
async def valyk(ctx, error):
    await ctx.channel.send(f"**Klaida.** Formatas: *vitali valyk [žinučių kiekis]*")
    return
#
# Help Command
@client.command(name="padek", description="Parašo visas Vitalio komandas")
async def padek(ctx):
    # Nunulinam pradinį tekstą, į kurį vesim duomenis
    helptext = ""
    # Su loop'u einam per visas komandas, ir tikriname jei komandos nėra nepageidaujamos (Dažniausiai admin komandos, arba kurios laikinai neveikia)
    for command in ctx.bot.commands:
        if(str(command) != "duokpinigu" and str(command) != "atimkpinigus" and str(command) != "uzsetinkpinigus" and str(command) != "help" and str(command) != "valyk" and str(command) != "isversk" and str(command) != "rulete" and str(command) != "testcmd"):
            helptext+=f"**{command}** - {command.description}.\n"
    
    # Embed message
    embed=discord.Embed(title=CASINO_EMBED_TITLE, description=f"{ctx.message.author.display_name.capitalize()} paprašė Vitalio pagalbos.", color=DEFAULT_COLOR_CODE)
    embed.add_field(name=f"Komandos", value=f"{helptext}", inline=False)
    embed.set_footer(text=f"\u200b\n{DEV_COPYRIGHT}")
    await ctx.channel.send(embed=embed)
@padek.error
async def padek(ctx, error):
    await ctx.channel.send(f"**Klaida.** Įvyko klaida nuskaitant duomenis. || {client.get_user(446698255791816704).mention} ||")
    return




client.run('OTExNjc2NzI4NzQ3ODg0NjA0.YZk3Hg.45CwmbCy15n3EZV3kjv3wUw7BVM')