import discord
import importlib
import inspect
import os
import wget
from git import repo
from dotenv import dotenv_values
from discord.ext import commands


CLONED_REPOS = []
config = dotenv_values("env_var")

client = commands.Bot(command_prefix=config["PREFIX"])

if not os.path.isdir(config["COGS_FOLDER_PATH"]):
    print("Creating folder for Cogs...")
    os.makedirs(config["COGS_FOLDER_PATH"])

##########################################################################
##########################################################################
##########################################################################
##########################################################################


@client.event
async def on_ready():
    print("Bot Ready!")

@client.command()
async def ping(ctx):
    await ctx.send(f"pong! {round(client.latency * 1000)}ms")

@client.command()
async def load_repo(ctx: commands.Context, repo_name:str, file_name: str, *which_cogs):
    await ctx.send("```digesting...```", delete_after=10)
    repo_name = repo_name.replace("-", "_")
    
    if not os.path.exists(f"{config['COGS_FOLDER_PATH']}/{repo_name}"):
        await ctx.send(f"```{repo_name} has not cloned yet``", delete_after=10)
        return

    if not os.path.exists(f"{config['COGS_FOLDER_PATH']}/{repo_name}/{file_name}.py"):
        await ctx.send(f"```file with name {file_name} is not exist```", delete_after=10)
        return

    # read classes who inherit commands.Gog
    cogs_path = f"{config['COGS_FOLDER_PATH']}.{repo_name}.{file_name}"
    cogs_module = importlib.import_module(cogs_path)

    available_cogs = [obj for name, obj in inspect.getmembers(cogs_module) if inspect.isclass(obj)]
    await ctx.send(available_cogs)
    for obj in available_cogs:
        await ctx.send(obj.__mro__)
    if available_cogs:
        for name in available_cogs:
            try:
                client.add_cog(cogs_module.Koran(name))
                await ctx.send(f"Succesfully loaded cog: {name}")
            except commands.errors.CommandRegistrationError:
                await ctx.send(f"Error when loading cog {name}")
    else:
        await ctx.send("File is empty or the file doesn't have suitable cogs to import!")
    
@client.command()
async def load_file(ctx: commands.Context, file_name: str, *which_cogs):
    await ctx.send("```digesting...```", delete_after=10)
    

    if not os.path.exists(f"{config['COGS_FOLDER_PATH']}/{file_name}.py"):
        await ctx.send(f"```file with name {file_name} is not exist```", delete_after=10)
        return

    # read classes who inherit commands.Gog
    cogs_path = f"{config['COGS_FOLDER_PATH']}.{file_name}"
    cogs_module = importlib.import_module(cogs_path)

    available_cogs = [obj for name, obj in inspect.getmembers(cogs_module) if inspect.isclass(obj) and issubclass(obj, commands.cog.Cog)]

    if available_cogs:
        for name in available_cogs:
            try:
                client.add_cog(cogs_module.Koran(name))
                await ctx.send(f"Succesfully loaded cog: {name}")
            except commands.errors.CommandRegistrationError:
                await ctx.send(f"Error when loading cog {name}")
    else:
        await ctx.send("File is empty or the file doesn't have suitable cogs to import!")
    

@client.command()
async def check_cog(cts: commands.Context, cog):
    pass

@client.command()
async def clone(ctx: commands.Context, repo_link: str):
    """
    Clone git repo
    """
    try:
        repo_name = repo_link.split('.git')[0].split('/')[-1].replace("-", "_")
        cloned_repo = repo.Repo.clone_from(repo_link, f"{config['COGS_FOLDER_PATH']}/{repo_name}")
        # for repo name https://stackoverflow.com/a/63352532/14052716
        await ctx.send(f"Succesfuly cloned repo {repo_name}")
        CLONED_REPOS.append(repo_name)
    except Exception as e:
        await ctx.send(f"Failed to clone repo...")
        await ctx.send(e)

@client.command()
async def fetch(ctx: commands.Context, url: str):
    """
    Download a single file given link
    """
    try:
        file_name = wget.download(url, out=config["COGS_FOLDER_PATH"])
        await ctx.send(f"Succesfuly fetch {file_name}")
    except Exception as e:
        await ctx.send(f"Failed to fetch file...", delete_after=10)
        await ctx.send(e)


@client.command()
async def unload(ctx: commands.Context):
    pass

    

client.run(config["TOKEN"])