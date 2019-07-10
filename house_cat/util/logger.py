import logging

logging.basicConfig(format='[%(asctime)s|%(levelname)s|%(guild)s|%(user)s] %(message)s', datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger('house-cat')


def get_guild_name(guild):
    if guild is None:
        return "private"
    return guild.name


def warn(ctx, message):
    logger.warning(message, extra={'guild': get_guild_name(ctx.guild), 'user': str(ctx.author.name+ctx.author.discriminator)})


def debug(ctx, message):
    logger.debug(message, extra={'guild': get_guild_name(ctx.guild), 'user': str(ctx.author.name+ctx.author.discriminator)})


def info(ctx, message):
    logger.info(message, extra={'guild': get_guild_name(ctx.guild), 'user': str(ctx.author.name+ctx.author.discriminator)})
