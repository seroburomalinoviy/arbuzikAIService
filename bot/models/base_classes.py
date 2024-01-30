from abc import ABC, abstractmethod

from telegram.ext import ContextTypes
from telegram import Update


class BaseCommandHandler(ABC):
    @abstractmethod
    def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        pass
