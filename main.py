from settings import CHART_LIMIT
from app.tracks import Chart
from app.videos import create_final_video


if __name__ == "__main__":
    chart = Chart("global", limit=CHART_LIMIT)
    create_final_video(chart)
