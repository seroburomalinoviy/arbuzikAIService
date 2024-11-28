from abc import ABC, abstractmethod
from pathlib import Path
import os
from pydub import AudioSegment
from uuid import uuid4
from asgiref.sync import sync_to_async

import django

from telegram.ext import ContextTypes
from telegram import Update
from telegram import Voice as TelegramVoice
from telegram import Audio as TelegramAudio
from telegram import Document as TelegramDocument

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from user.models import User


class BaseCommandHandler(ABC):
    @abstractmethod
    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        pass


class BaseConversationHandler(ABC):
    @abstractmethod
    def entrypoints(self):
        pass

    @abstractmethod
    def states(self):
        pass

    @abstractmethod
    def fallbacks(self):
        pass


class PreparedFile:
    def __init__(self, update: Update, context, user: User):
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
        if self.obj.file_size >= 20_000_000:
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

    @sync_to_async
    def calculate_duration(self):
        if isinstance(self.obj, TelegramDocument):
            sound = AudioSegment.from_file(self.path)
            self.duration = sound.duration_seconds
        elif isinstance(self.obj, TelegramAudio):
            self.duration = self.obj.duration
        elif isinstance(self.obj, TelegramVoice):
            self.duration = self.obj.duration

        if self.duration > self.user.subscription.time_voice_limit:
            obj = AudioSegment.from_file(self.path)
            obj[: self.user.subscription.time_voice_limit * 1001].export(self.path)
            self.duration = self.user.subscription.time_voice_limit

    @property
    def extension(self):
        return "." + self.obj.mime_type.split("/")[-1]

    @property
    def name(self):
        return self.context.user_data.get("slug_voice") + "_" + str(uuid4())

    @property
    def path(self):
        return Path(os.getenv("USER_VOICES") + "/" + self.name + self.extension)




