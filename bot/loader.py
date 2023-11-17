from .utils import create_dispatcher
from .settings import TOKEN

assert TOKEN, "TELEGRAM_BOT_TOKEN not found in environment"

dp = create_dispatcher(TOKEN)