from abc import ABC, abstractmethod

from telegram.ext import ContextTypes
from telegram import Update


class BaseCommandHandler(ABC):
    @abstractmethod
    def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        pass


class BaseConversationHandler(ABC):
    @abstractmethod
    async def entrypoints(self):
        pass

    @abstractmethod
    async def states(self):
        pass

    @abstractmethod
    async def fallbacks(self):
        pass