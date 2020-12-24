# music

Приложение для генерации музыкальных видео-чартов на основе чартов 4 сервисов: Яндекс Музыка, Deezer, Shazam и Spotify. Работает под Windows, Linux и MacOS.

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
 - media/mp3
 - media/mp4_full
 - media/mp4_transitions
 - media/mp4_trimmed
 - media/ts_transitions
 - media/ts_trimmed


4. Переименовать файл `.env_template` в `.env`. В нем указать данные для полученя доступов к внешним сервисам.