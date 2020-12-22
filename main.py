import logging
import logging.config
import yaml
from app.operations import create_internat_chart, update_in_youtube_ids
from app.video import download_videos, update_chorus_time, trim_videos, create_transitions, concat_videos
from settings import CHART_LENGTH


if __name__ == "__main__":
    with open('logs.yaml', 'r') as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    logger = logging.getLogger(__name__)

    chart = create_internat_chart(chart_lenght=CHART_LENGTH)
    chart = update_in_youtube_ids(chart)
    download_videos(chart)
    chart = update_chorus_time(chart)
    trim_videos(chart)
    create_transitions(chart)
    concat_videos(chart)
