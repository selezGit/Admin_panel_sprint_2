from modules import logger
from modules.extract import data_upload_first_stage, data_upload_third_stage
from modules.load import load_to_es
from modules.transform import transform


def film_work_pipeline(check_time) -> None:
    """запускает пайплайн для фильмов"""

    logger.info('starting ETL film_work')

    table = 'film_work'

    load_data = load_to_es()
    raw_data = transform(load_data)
    data = data_upload_third_stage(raw_data)
    data_upload_first_stage(data, table, check_time)

    logger.info('pipleline film_work end')