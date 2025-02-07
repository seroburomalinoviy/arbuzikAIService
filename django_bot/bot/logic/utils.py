from datetime import datetime
from zoneinfo import ZoneInfo
from django.conf import settings
import functools
from telegram import Update
import logging
import asyncio
from pydub import AudioSegment
from pathlib import Path
import os

from telegram import Voice as TelegramVoice
from telegram import Audio as TelegramAudio
from telegram import Document as TelegramDocument


def get_moscow_time() -> datetime:
    return datetime.now(tz=ZoneInfo(settings.TIME_ZONE))


def log_journal(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        update: Update = args[0]
        if update.message:
            _id = str(update.effective_user.id)
        elif update.callback_query:
            _id = str(update.callback_query.from_user.id)
        elif update.inline_query:
            _id = str(update.inline_query.from_user.id)
        else:
            _id = "Not found"

        logging.info(
            f"JOURNAL: A call for user,id: {_id} from {func.__name__}"
        )
        return await func(*args, **kwargs)

    return wrapper


class PreparedFile:
    def __init__(self, update: Update, context, user, uuid):
        self.uuid = uuid
        self.user = user
        self.context = context
        self.duration: float = 0.0
        if update.message.document:
            self.obj: TelegramDocument = update.message.document
        elif update.message.voice:
            self.obj: TelegramVoice = update.message.voice
        elif update.message.audio:
            self.obj: TelegramAudio = update.message.audio
        else:
            self.obj = None

    async def is_valid_size(self):
        if self.obj.file_size >= 20_000_000:  # 20МБ
            return False
        return True

    async def download(self):
        """
        download voice file to host
        :return:
        """
        q = await self.obj.get_file()
        await q.download_to_drive(
            custom_path=self.path
        )

    async def _calculate_duration_from_file(self):
        sound = AudioSegment.from_file(self.path)
        return sound.duration_seconds

    async def _trim_audio(self):
        obj = AudioSegment.from_file(self.path)
        obj[: self.user.subscription.time_voice_limit * 1001].export(self.path)
        self.duration = self.user.subscription.time_voice_limit

    async def calculate_duration(self):
        if isinstance(self.obj, TelegramDocument):
            self.duration = await asyncio.to_thread(self._calculate_duration_from_file)
        elif isinstance(self.obj, TelegramAudio):
            self.duration = self.obj.duration
        elif isinstance(self.obj, TelegramVoice):
            self.duration = self.obj.duration

        if self.duration > self.user.subscription.time_voice_limit:
            await asyncio.to_thread(self._trim_audio)

    @property
    def extension(self):
        return "." + self.obj.mime_type.split("/")[-1]

    @property
    def name(self):
        return self.context.user_data.get("slug_voice") + "_" + str(self.uuid)

    @property
    def path(self):
        return Path(os.getenv("USER_VOICES") + "/" + self.name + self.extension)
