from .sinoffice import SINOffice


async def setup(bot):
    await bot.add_cog(SINOffice(bot))
