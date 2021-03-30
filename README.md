# music

Приложение для генерации музыкальных видео-чартов на основе чартов 3 сервисов: Deezer, Shazam и Spotify. Работает под Windows, Linux и MacOS.

## Установка

Установка показана на примере MacOS.

1. Установить ffmpeg  

```
brew install ffmpeg
``` 

2. Создать виртуальное окружение со всеми зависимостями. 

```
python -m venv venv
pip install -r requirements.txt
```

3. В корневой папке проекта создать папки:

 - media
 - media/full_tracks
 - media/cut_tracks
 - media/transitions


4. Переименовать файл `.env_template` в `.env`. В нем указать данные для полученя доступов к внешним сервисам.