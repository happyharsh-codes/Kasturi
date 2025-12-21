from __init__ import *
import asyncio
import random
import discord
from discord.ext import commands
from discord import Embed


class Fun(commands.Cog):

    def __init__(self, client: commands.Bot):
        self.client = client
    
    @commands.hybrid_command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def joke(self, ctx):
        async with ctx.typing():
            joke = getResponse(
                "Tell me a funny joke",
                "You are a professional joke writer. Short joke only."
            )
        emoji = EMOJI[f"kelly{choice(['laugh','gigle','blush'])}"]
        await ctx.send(f"{emoji} **|** {joke}")

    @commands.hybrid_command()
    @commands.cooldown(1, 90, commands.BucketType.user)
    async def picture(self, ctx, *, prompt: str):
        async with ctx.typing():
            desc = getResponse(
                prompt,
                "Describe a beautiful image vividly in 25 words.",
                client=0
            )

        embed = Embed(
            title="🖼️ Kelly Imagined This",
            description=f"**Prompt:** `{prompt}`\n\n{desc}",
            color=Color.blurple()
        )
        embed.set_footer(text="Image generation powered by Kelly's imagination ✨")
        await ctx.send(embed=embed)

    @commands.hybrid_command()
    @commands.cooldown(1, 90, commands.BucketType.user)
    async def roast(self, ctx, user: discord.Member):
        async with ctx.typing():
            roast = getResponse(
                f"Roast {user.display_name}",
                "Savage but playful roast. No slurs. 15–20 words.",
                client=0
            )
        await ctx.send(f"🔥 {user.mention} {roast}")

    @commands.hybrid_command()
    @commands.cooldown(1, 45, commands.BucketType.user)
    async def ask(self, ctx, *, question: str):
        async with ctx.typing():
            answer = getResponse(
                question,
                "Answer smartly with sarcasm in under 20 words.",
                client=0
            )
        await ctx.reply(answer)

    @commands.hybrid_command()
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def heck(self, ctx, user: discord.Member):

        def heck_string():
            return "".join(choice("$#@*^₹&!?") for _ in range(randint(3, 8)))

        msg = await ctx.reply(
            f"{ctx.author.display_name} hecked {user.mention}: **{heck_string()}**"
        )

        for _ in range(12):
            await asyncio.sleep(0.05)
            await msg.edit(
                content=f"{ctx.author.display_name} hecked {user.mention}: **{heck_string()}**"
            )

    @commands.hybrid_command()
    @commands.cooldown(1, 90, commands.BucketType.user)
    async def meme(self, ctx):
        async with ctx.typing():
            meme = getResponse(
                "Generate a funny meme caption",
                "Internet meme style. Short and punchy.",
                client=0
            )

        embed = Embed(
            title="😂 Kelly Meme",
            description=meme,
            color=Color.orange()
        )
        embed.set_footer(text="Meme approved by Kelly ✔️")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Fun(bot))
    print("Loaded cog: Fun")
