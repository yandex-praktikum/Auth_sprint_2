import logging 
import backoff


def backoff_hdlr(details):
    logging.info(f"backoff_hdlr, {details}")


backoff_exception = backoff.on_exception(
    backoff.expo, (BaseException,), max_value=10, on_backoff=backoff_hdlr
)