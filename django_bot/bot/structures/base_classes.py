from abc import ABC, abstractmethod

from telegram.ext import ContextTypes
from telegram import Update


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







