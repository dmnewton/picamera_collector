
import logging
logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger(__name__)

class TriggerEvent(object):
    "use this dummy trigger when you wish a remote pi to send trigger picture"
    def __init__(self,cf):
        logger.info("dummy trigger")