import logging

logging.basicConfig(format='[%(asctime)s|%(levelname)s|%(guild)s|%(user)s] %(message)s', datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger('house-cat')


def warn(ctx, message):
    logger.warning(message, extra={'guild': ctx.guild.name, 'user': str(ctx.author.name+ctx.author.discriminator)})


def debug(ctx, message):
    logger.debug(message, extra={'guild': ctx.guild.name, 'user': str(ctx.author.name+ctx.author.discriminator)})


def info(ctx, message):
    logger.info(message, extra={'guild': ctx.guild.name, 'user': str(ctx.author.name+ctx.author.discriminator)})
