from modules import logger
from modules.extract import (data_upload_first_stage, data_upload_second_stage,
                             data_upload_third_stage)
from modules.load import load_to_es
from modules.transform import transform


def genre_pipeline(check_time) -> None:
    """запускает пайплайн для жанров"""

    logger.info('starting ETL genre')

    table = 'genre'

    load_data = load_to_es()
    raw_data = transform(load_data)
    data = data_upload_third_stage(raw_data)
    get_m2m_data = data_upload_second_stage(data, table, check_time)
    data_upload_first_stage(get_m2m_data, table, check_time, limit=1)

    logger.info('pipleline genre end')
