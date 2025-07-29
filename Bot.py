import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Select, View
import datetime
from keep_alive import keep_alive  # For Replit 24/7 hosting

from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

GUILD_ID = 1399429188843259984
MASS_SHIFT_CHANNEL_ID = 1399512109095714967
INFRACTION_CHANNEL_ID = 1399477181138210887
PROMOTE_DEMOTE_CHANNEL_ID = 1399487526460330004
SDC_EMPLOYEE_ROLE_ID = 1399429189244944569

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="/", intents=intents)
tree = bot.tree

@bot.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"✅ Logged in as {bot.user}")

@tree.command(guild=discord.Object(id=GUILD_ID), name="host_mass_shift", description="Host a mass shift.")
@app_commands.describe(
    host="Who's hosting?",
    cohost="Who's co-hosting?",
    location="Where should employees meet?",
    description="Small description for this mass shift.",
    promotion="Is this shift promotable? (yes/no)"
)
async def host_mass_shift(interaction: discord.Interaction, host: str, cohost: str, location: str, description: str, promotion: str):
    embed = discord.Embed(
        title="🚨 Mass Shift Starting! 🚨",
        description=f"**Host:** {host}\n**Co-Host:** {cohost}\n**Location:** {location}\n**Promotion Eligible:** {promotion}\n\n**{description}**",
        color=discord.Color.red(),
        timestamp=datetime.datetime.utcnow()
    )
    embed.set_footer(text=f"Posted by: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

    channel = bot.get_channel(MASS_SHIFT_CHANNEL_ID)
    message = await channel.send(f"<@&{SDC_EMPLOYEE_ROLE_ID}>", embed=embed)
    await message.add_reaction("✅")
    await message.add_reaction("❌")

    thread = await message.create_thread(name="Mass Shift Discussion")
    await thread.send(f"**{description}**")
    await interaction.response.send_message("✅ Mass Shift announcement sent!", ephemeral=True)

@tree.command(guild=discord.Object(id=GUILD_ID), name="infract", description="Log an infraction")
@app_commands.describe(
    employee="Tag the employee.",
    reason="Reason for the infraction.",
    notes="Additional notes.",
    proof="Proof (link or description)."
)
async def infract(interaction: discord.Interaction, employee: discord.Member, reason: str, notes: str, proof: str):
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    embed = discord.Embed(
        title="❗ Infraction Log ❗",
        description=f"**Employee:** {employee.mention}\n**Reason:** {reason}\n**Date:** {now}\n**Notes:** {notes}\n**Proof:** {proof}",
        color=discord.Color.orange(),
        timestamp=datetime.datetime.utcnow()
    )
    embed.set_footer(text=f"Submitted by: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

    channel = bot.get_channel(INFRACTION_CHANNEL_ID)
    await channel.send(embed=embed)
    await interaction.response.send_message("✅ Infraction logged!", ephemeral=True)

@tree.command(guild=discord.Object(id=GUILD_ID), name="promote_demote", description="Promote or demote an employee.")
@app_commands.describe(
    member="Tag the member.",
    old_rank="Role to remove.",
    new_rank="Role to add.",
    action="Promotion or Demotion."
)
async def promote_demote(interaction: discord.Interaction, member: discord.Member, old_rank: discord.Role, new_rank: discord.Role, action: str):
    if old_rank not in member.roles:
        await interaction.response.send_message("❌ Error: The selected employee doesn't have that role.", ephemeral=True)
        return

    await member.remove_roles(old_rank)
    await member.add_roles(new_rank)

    embed = discord.Embed(
        title=f"📢 {action.capitalize()} Notice",
        description=f"**Employee:** {member.mention}\n**Action:** {action.capitalize()}\n**Old Rank:** {old_rank.mention}\n**New Rank:** {new_rank.mention}",
        color=discord.Color.green() if action.lower() == "promotion" else discord.Color.red(),
        timestamp=datetime.datetime.utcnow()
    )
    embed.set_footer(text=f"Submitted by: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

    channel = bot.get_channel(PROMOTE_DEMOTE_CHANNEL_ID)
    await channel.send(embed=embed)
    await interaction.response.send_message(f"✅ {action.capitalize()} processed!", ephemeral=True)

keep_alive()
bot.run(TOKEN)
