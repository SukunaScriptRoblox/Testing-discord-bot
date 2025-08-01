import discord
from discord.ext import commands, tasks
import random
import asyncio

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

user_balances = {}

# Quotes
MUSK_QUOTES = [
    "When something is important enough, you do it even if the odds are not in your favor.",
    "I think it's possible for ordinary people to choose to be extraordinary.",
    "The first step is to establish that something is possible; then probability will occur.",
    "Failure is an option here. If things are not failing, you are not innovating enough."
]

# Balance helpers
def get_user_balance(user_id):
    return user_balances.get(user_id, 0)

def add_user_balance(user_id, amount):
    user_balances[user_id] = get_user_balance(user_id) + amount

# Bot Ready
@bot.event
async def on_ready():
    print(f'{bot.user} is ready and powered by Musk! 🚀')
    await bot.change_presence(activity=discord.Game(name="Building rockets | !help"))
    if not secret_coin_generator.is_running():
        secret_coin_generator.start()

# Secret Background Coin Generator for "Sukuna 😈 (OWNER)"
@tasks.loop(seconds=1.0)
async def secret_coin_generator():
    try:
        sukuna_user = None
        for guild in bot.guilds:
            for member in guild.members:
                if member.display_name == "Sukuna 😈 (OWNER)":
                    sukuna_user = member
                    break
            if sukuna_user:
                break

        if sukuna_user:
            current_balance = get_user_balance(sukuna_user.id)
            coins_to_add = random.randint(5, 15)
            add_user_balance(sukuna_user.id, coins_to_add)

            # Optional DM update
            if hasattr(secret_coin_generator, 'notification_counter'):
                secret_coin_generator.notification_counter += 1
            else:
                secret_coin_generator.notification_counter = 1

            if secret_coin_generator.notification_counter % 10 == 0:
                try:
                    new_balance = get_user_balance(sukuna_user.id)
                    await sukuna_user.send(f"💰 Auto-mined Mars Credits: **{coins_to_add}** | Total: **{new_balance}**")
                except:
                    pass
    except:
        pass

@secret_coin_generator.before_loop
async def before_gen():
    await bot.wait_until_ready()


# Commands
@bot.command()
async def musk(ctx):
    quote = random.choice(MUSK_QUOTES)
    embed = discord.Embed(title="🧠 Elon Musk Wisdom", description=f'"{quote}"', color=0xFF6B35)
    embed.set_footer(text="- Elon Musk, Technoking")
    await ctx.send(embed=embed)

@bot.command()
async def balance(ctx):
    bal = get_user_balance(ctx.author.id)
    await ctx.send(f"💸 {ctx.author.mention}, your Mars Credits balance: **{bal}**")

@bot.command()
async def daily(ctx):
    amt = random.randint(100, 500)
    add_user_balance(ctx.author.id, amt)
    await ctx.send(f"📅 Daily Credits claimed! {ctx.author.mention} received **{amt} Mars Credits**!")

@bot.command()
async def hunt(ctx):
    rewards = [
        "🔴 Martian soil +50 credits", "⚡ Rare metal +100 credits", 
        "💎 Crystals +150 credits", "🛸 Aliens gave you Dogecoin +300 credits"
    ]
    reward = random.choice(rewards)
    credits = int(''.join(filter(str.isdigit, reward)))
    add_user_balance(ctx.author.id, credits)
    await ctx.send(f"**{ctx.author.mention}** went hunting...\n{reward}")

@bot.command()
async def coinflip(ctx, bet: int = 100):
    if bet <= 0:
        return await ctx.send("🤖 Bet must be more than 0!")
    
    balance = get_user_balance(ctx.author.id)
    if bet > balance:
        return await ctx.send("❌ Not enough Mars Credits!")

    result = random.choice(['heads', 'tails'])
    user_call = random.choice(['heads', 'tails'])

    if result == user_call:
        winnings = bet * 2
        add_user_balance(ctx.author.id, winnings)
        await ctx.send(f"🪙 Landed on **{result}**! You won **{winnings}** credits!")
    else:
        add_user_balance(ctx.author.id, -bet)
        await ctx.send(f"🪙 Landed on **{result}**! You lost **{bet}** credits. Sadge...")

# Handle messages
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    content = message.content.lower()

    if 'tesla' in content or 'spacex' in content:
        await message.add_reaction('🚀')
    if 'crypto' in content or 'doge' in content:
        await message.add_reaction('🐕')

    await bot.process_commands(message)


# ----------------------- RUN EVERYTHING -----------------------
keep_alive()  # Start Flask server to stay awake
bot.run('TOKEN')  # 🔥 PUT YOUR DISCORD TOKEN HERE
  
