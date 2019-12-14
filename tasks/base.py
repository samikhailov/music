from tasks import yandex, youtube


def calc_chart(chart, amount_pos):
    chart.sort(key=lambda dictionary: dictionary['position'])
    return chart[:amount_pos]


def append_music_base(music_base, chart):
    """
    Добавлений новых записей в базу из чарта
    :param music_base:
    :param chart:
    :return:
    """
    for chart_row in chart:
        for base_row in music_base:
            if chart_row["yandex_id"] == base_row["yandex_id"]:
                break
        else:
            music_base.append({})
            music_base[-1]["id"] = len(music_base)
            music_base[-1]["artist"] = chart_row["artist"]
            music_base[-1]["title"] = chart_row["title"]
            music_base[-1]["yandex_id"] = chart_row["yandex_id"]
            print(f'New record in the base. id: {music_base[-1]["id"]}')
    return music_base


def update_music_base(music_base):
    """
    Пополнение базы полями yandex_id и youtube_id по API.
    :param music_base:
    :return:
    """
    for row in music_base:
        if row.get("yandex_id") is None or row.get("yandex_id") == "":
            row["yandex_id"] = yandex.get_yandex_id(row["artist"], row["title"])

        if row.get("youtube_id") is None or row.get("youtube_id") == "":
            row["youtube_id"] = youtube.get_youtube_id(row["artist"], row["title"])

    return music_base


def update_chart(music_base, chart):
    """
    Пополнение чарта полями id и youtube_id из базы.
    :param music_base:
    :param chart:
    :return:
    """
    for chart_row in chart:
        for base_row in music_base:
            if chart_row["yandex_id"] == base_row["yandex_id"]:
                chart_row["id"] = base_row["id"]
                chart_row["youtube_id"] = base_row["youtube_id"]
    return chart
