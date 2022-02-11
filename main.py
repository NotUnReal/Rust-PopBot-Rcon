from multiprocessing import AuthenticationError
from discord import Game
from discord.ext import commands, tasks
from websockets.exceptions import ConnectionClosedError,InvalidMessage
from websockets import connect
from json import dumps,loads

# -----------------------------------------------------
#-------------------- START CONFIG --------------------
# -----------------------------------------------------

discordBotToken = "" #type: str
ip = ""              #type: str
port = ""            #type: str
password = ""        #type: str

# -----------------------------------------------------
#--------------------- END CONFIG ---------------------
# -----------------------------------------------------

client = commands.Bot(command_prefix="-",help_command=None)
con = None
rconURL = f"ws://{ip}:{port}/{password}"

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandNotFound):
        pass

@client.event
async def on_ready():
    await startCon()
    print(f"Bot successfully started\n")

@tasks.loop(seconds=10)
async def change_status():
    await client.wait_until_ready()

    try:
        await con.send(dumps({'Identifier':"1239832",'Message':"serverinfo",'Name':"PopBot"}))
    except (ConnectionClosedError,AttributeError):
        print("Connection was closed (Ignore on startup)")
        await startCon()
    else:
        preData = await con.recv()
        basicData = loads(preData)
        if basicData['Identifier'] == 1239832 and basicData['Type'] == 'Generic':
            data = loads(basicData['Message'])

            if data['Queued'] > 0:
                await client.change_presence(activity=Game(f"{data['Players']}/{data['MaxPlayers']} Queue {data['Queued']}"))
            else:
                await client.change_presence(activity=Game(f"{data['Players']}/{data['MaxPlayers']} Joining {data['Joining']}"))

async def startCon():
    global con
    try:
        con = await connect(rconURL,ping_interval=None)
    except ConnectionRefusedError:
        raise(ConnectionError("Unable to connect to server"))
    except InvalidMessage:
        raise(AuthenticationError("Check the password"))
    return con
    
change_status.start()
client.run(discordBotToken)