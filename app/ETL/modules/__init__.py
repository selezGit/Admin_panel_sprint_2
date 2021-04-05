import logging

logger = logging.getLogger()
logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', level=logging.INFO)
logging.getLogger("elasticsearch").setLevel(logging.CRITICAL)
