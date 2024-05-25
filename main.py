import settings
import discord
from discord.ext import commands
import logging
import time

logger = settings.logging.getLogger("bot")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=",", intents=intents)

ALLOWED_CHANNEL_ID = 1242557436838281378

def channel_check():
    async def predicate(ctx):
        if ctx.channel.id != ALLOWED_CHANNEL_ID:
            await ctx.send(f"**Чтобы пользоваться командами бота, перейдите в <#{ALLOWED_CHANNEL_ID}>**", ephemeral=True)
            return False
        return True
    return commands.check(predicate)

class BalanceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_balances = {}
        self.last_daily_claim = {}

    @commands.hybrid_command(name="balance", description="Показать ваш баланс")
    @channel_check()
    async def balance(self, ctx: commands.Context):
        user_id = ctx.author.id
        user_name = ctx.author.name
        balance = self.user_balances.get(user_id, 0)
        user_avatar_url = ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url

        embed = discord.Embed(
            title=f"Баланс пользователя - {user_name}",
            color=discord.Color.gold()
        )

        embed.set_thumbnail(url=user_avatar_url)
        embed.description=f"Монеток - **{balance}**"

        logger.info(f"\"/balance\" : Пользователь {user_name} (ID: {user_id}) запросил баланс")

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="daily", description="Добавляет на ваш баланс 50 монет")
    @channel_check()
    async def daily(self, ctx: commands.Context):
        user_id = ctx.author.id
        user_name = ctx.author.name
        now = time.time()

        last_claim = self.last_daily_claim.get(user_id, 0)

        if now - last_claim >= 86400:
            self.user_balances[user_id] = self.user_balances.get(user_id, 0) + 50
            self.last_daily_claim[user_id] = now

            embed = discord.Embed(
                title="Ежедневный бонус",
                description="Вы успешно получили **50 монет** на свой баланс!",
                color=discord.Color.green()
            )

            logger.info(f"\"/daily\" : Пользователь {user_name} (ID: {user_id}) запросил ежедневку") 
        else:
            embed = discord.Embed(
                title="Ошибка",
                description="Вы уже получили свой ежедневный бонус. Его можно получать за каждые **24 часа**. Приходите потом.",
                color=discord.Color.red()
            )

            logger.info(f"\"/daily(waitException)\" : Пользователь {user_name} (ID: {user_id}) уже пытался получить ежедневный бонус")

        await ctx.send(embed=embed) 

    @commands.hybrid_command(name="clearbalance", description="Очистить баланс пользователя по его ID")
    @commands.has_permissions(administrator=True)
    @channel_check()
    async def clearbalance(self, ctx: commands.Context, user: discord.User):
        user_id = user.id
        user_name = user.name
        self.user_balances[user_id] = 0

        embed = discord.Embed(
            title="Баланс очищен",
            description=f"Баланс пользователя {user_name} (ID: {user_id}) был успешно очищен.",
            color=discord.Color.blue()
        )

        logger.info(f"\"/clearbalance\" : Пользователь {ctx.author.name} (ID: {ctx.author.id}) очистил баланс пользователя {user_name} (ID: {user_id})")

        await ctx.send(embed=embed, ephemeral=True)
    
    @commands.hybrid_command(name="addmoney", description="Добавить монеты на баланс пользователя (Admin Command)")
    @commands.has_permissions(administrator=True)
    @channel_check()
    async def addmoney(self, ctx: commands.Context, user: discord.User, money: int):
        user_id = user.id
        user_name = user.name
        if user_id in self.user_balances:
            self.user_balances[user_id] += money
        else:
            self.user_balances[user_id] = money

        embed = discord.Embed(
            title="Баланс обновлен",
            description=f"Баланс пользователя {user_name} (ID: {user_id}) был успешно пополнен на **{money}** монет.",
            color=discord.Color.blue()
        )

        logger.info(f"\"/addmoney\" : Пользователь {ctx.author.name} (ID: {ctx.author.id}) добавил {money} монет пользователю {user_name} (ID: {user_id})")

        await ctx.send(embed=embed, ephemeral=True)

    @commands.hybrid_command(name="top", description="Показать ТОП-10 пользователей по балансу")
    @channel_check()
    async def top(self, ctx: commands.Context):
        top_users = sorted(self.user_balances.items(), key=lambda item: item[1], reverse=True)[:10]
        description = ""
        for i, (user_id, balance) in enumerate(top_users, start=1):
            user = await self.bot.fetch_user(user_id)
            description += f"{i}) **{user.name}** имеет **{balance}** монет\n"

        embed = discord.Embed(
            title="Топ-10 пользователей по балансу",
            description=description,
            color=discord.Color.gold()
        )

        logger.info(f"\"/top\" : Пользователь {ctx.author.name} (ID: {ctx.author.id}) запросил топ-10 пользователей по балансу")

        await ctx.send(embed=embed)

@bot.event
async def on_ready():
    logger.info(f"Bot: {bot.user} (ID: {bot.user.id})")
    try:
        await bot.tree.sync()
        logger.info("Slash-команды успешно синхронизированы")
    except Exception as e:
        logger.error(f"Ошибка синхронизации команд: {e}")

@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("**У вас нет административных прав на использование этой команды.**", ephemeral=True)
        # logger.warning(f"\"/clearbalance(NoPerms)\" : Пользователь {ctx.author.name} (ID: {ctx.author.id}), у которого нет прав, пытался использовать команду clearbalance")
    else:
        await ctx.send("Произошла ошибка при выполнении команды.", ephemeral=True)
        logger.error(f"Ошибка команды: {error}")

async def setup():
    await bot.add_cog(BalanceCog(bot))

async def main():
    async with bot:
        await setup()
        await bot.start(settings.DISCORD_API_SECRET)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
