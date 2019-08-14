import logging
from logging import getLogger

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def debug_requests(f):
    """ Декоратор для отладки событий от телеграма
    """
    def inner(*args, **kwars):
        try:
            logger.info('Обращение в функцию {}'.format(f.__name__))
            return f(*args, **kwars)
        except Exception:
            logger.exception('Ошибка в обработчике {}'.format(f.__name__))
            raise

    return inner