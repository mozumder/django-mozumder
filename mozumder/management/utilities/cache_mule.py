import logging
logger = logging.getLogger("cache")
from mozumder.management.utilities.invalidator import CacheInvalidator

logger.info("uWSGI CacheControl Mule Process started & listening")
CacheInvalidator.listen()

