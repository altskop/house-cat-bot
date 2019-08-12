import logging

logging.basicConfig(format='[%(asctime)s|%(levelname)s] %(message)s', datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger('house-cat')


def get_guild_name(guild):
    if guild is None:
        return "private"
    return guild.name


def log_command(ctx, message):
    message = "[{0}|{1}] {2}".format(get_guild_name(ctx.guild), ctx.author.name + ctx.author.discriminator, message)
    logger.info(message)
