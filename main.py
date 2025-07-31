# app.py

import discord
from discord.ext import commands
import asyncio
import os
import threading
from flask import Flask

# ---------------------- FLASK WEB SERVER ----------------------
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Emergency Bot is live!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

threading.Thread(target=run_web).start()

# ---------------------- EMERGENCY DISCORD BOT ----------------------
MONITORED_USER = "漢•Sukunaヅ {ADMIN}"
ADMIN_ROLE_NAME = "admin"
CHECK_INTERVAL = 30

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'🤖 Emergency Bot is online! Logged in as {bot.user}')
    bot.loop.create_task(monitor_user_admin_status())

async def monitor_user_admin_status():
    await bot.wait_until_ready()
    while not bot.is_closed():
        try:
            for guild in bot.guilds:
                monitored_member = next(
                    (m for m in guild.members if m.display_name == MONITORED_USER or m.name == MONITORED_USER),
                    None
                )
                if monitored_member:
                    has_admin = any(r.name == ADMIN_ROLE_NAME or r.permissions.administrator for r in monitored_member.roles)
                    if not has_admin:
                        print(f'🚨 ALERT: {MONITORED_USER} lost admin in {guild.name}')
                        await restore_admin_role(guild, monitored_member)
                    else:
                        print(f'✅ {MONITORED_USER} still has admin in {guild.name}')
        except Exception as e:
            print(f'❌ Error during monitoring: {e}')
        await asyncio.sleep(CHECK_INTERVAL)

async def restore_admin_role(guild, member):
    try:
        admin_role = next((r for r in guild.roles if r.name == ADMIN_ROLE_NAME or r.permissions.administrator), None)
        if admin_role:
            await member.add_roles(admin_role)
            print(f'🛡️ RESTORED: Admin role to {member.display_name} in {guild.name}')
            for channel in guild.text_channels:
                if channel.name in ['general', 'alerts', 'admin']:
                    try:
                        await channel.send(f'🚨 Auto-restored admin to {member.mention}')
                        break
                    except: continue
        else:
            print(f'❌ Admin role not found in {guild.name}')
    except discord.Forbidden:
        print(f'❌ Bot lacks permission in {guild.name}')
    except Exception as e:
        print(f'❌ Restore error: {e}')

# Just one command to verify bot status
@bot.command()
async def status(ctx):
    await ctx.send("✅ Bot is alive and monitoring!")

# ---------------------- RUN BOT ----------------------
if __name__ == "__main__":
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        print("❌ DISCORD_BOT_TOKEN not set!")
    else:
        print("🚀 Launching Emergency Bot + Web...")
        bot.run(token)
