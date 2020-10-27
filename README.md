# music

Приложение для генерации музыкальных видео-чартов на основе чартов 3 сервисов: Яндекс Музыка, Deezer и Shazam. Работает под Windows, Linux и MacOS.

## Установка

Установка показана на примере MacOS.

1. Установить ffmpeg  

```
brew install ffmpeg
``` 

2. Создать виртуальное окружение со всеми зависимостями. 

```
pip install -r requirements.txt
```

3. В корневой папке проекта создать папки:

 - content
 - content/full_videos
 - content/cut_videos
 - content/ts_cut_videos
 - content/transition_videos
 - content/ts_transition_videos
 - content/mp3_videos
 - content/logs

4. В файле `tasks/credentials_yandex.json` установить значения `login` и `password`.

5. В файле `tasks/youtube.py` установить значение токена. Подробнее на странице [Obtaining authorization credentials](https://developers.google.com/youtube/registering_an_application).
