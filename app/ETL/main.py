from person_pipeline import person_pipeline
from genre_pipeline import genre_pipeline
from film_work_pipeline import film_work_pipeline
from modules.storage import RedisStorage, State
import time

from datetime import datetime

from redis import Redis

red_conn = RedisStorage(Redis(host='redis'))
state = State(red_conn)

if __name__ == '__main__':


    while True:
        last_check_time = state.get_state('last_check_time')

        if not last_check_time:
            last_check_time = '1970-01-01 00:00:00.00'

        
        time.sleep(10)
        film_work_pipeline(last_check_time)
        time.sleep(10)
        genre_pipeline(last_check_time)
        time.sleep(10)
        person_pipeline(last_check_time)
        state.set_state('last_check_time', str(datetime.now()))
