"""
Telegram Auto-Reply Bot
- Responds to keywords with custom replies
- Supports multiple chat modes (private, group, all)
- Logs all messages
"""

import os
import re
import logging
import json
from pathlib import Path
from typing import Optional

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# ─── Configuration ───────────────────────────────────────────────────────────

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Auto-reply rules: list of (pattern, reply, case_sensitive)
# Patterns are regex. First match wins.
DEFAULT_RULES = [
    (r"\bhi\b|\bhello\b|\bhey\b", "Hello! How can I help you?"),
    (r"\bbye\b|\bgoodbye\b", "Goodbye! Have a great day!"),
    (r"\bhelp\b", "I'm an auto-reply bot. Send me any message and I'll reply!"),
    (r"\bthanks?\b|\bthank you\b", "You're welcome!"),
    (r"\bwhat'?s? up\b", "Not much, just waiting to help you!"),
    (r"\bhow are you\b", "I'm doing great, thanks for asking!"),
    (r"\byour name\b", "I'm AutoReplyBot! Nice to meet you."),
    (r"\bwho created you\b", "I was created by a Python script!"),
]

RULES_FILE = Path("rules.json")

# ─── Logging ─────────────────────────────────────────────────────────────────

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)


# ─── Rules Management ────────────────────────────────────────────────────────

class RuleManager:
    def __init__(self, rules_file: Path = RULES_FILE):
        self.rules_file = rules_file
        self.rules = self._load()

    def _load(self) -> list:
        if self.rules_file.exists():
            try:
                with open(self.rules_file) as f:
                    data = json.load(f)
                return [(r["pattern"], r["reply"]) for r in data]
            except Exception as e:
                log.warning(f"Failed to load rules: {e}")
        return DEFAULT_RULES.copy()

    def save(self):
        data = [{"pattern": p, "reply": r} for p, r in self.rules]
        with open(self.rules_file, "w") as f:
            json.dump(data, f, indent=2)
        log.info(f"Saved {len(self.rules)} rules to {self.rules_file}")

    def add_rule(self, pattern: str, reply: str):
        self.rules.append((pattern, reply))
        self.save()

    def remove_rule(self, index: int) -> bool:
        if 0 <= index < len(self.rules):
            self.rules.pop(index)
            self.save()
            return True
        return False

    def list_rules(self) -> list:
        return self.rules

    def find_match(self, text: str) -> Optional[str]:
        for pattern, reply in self.rules:
            try:
                if re.search(pattern, text, re.IGNORECASE):
                    return reply
            except re.error:
                continue
        return None


# ─── Handlers ────────────────────────────────────────────────────────────────

rule_manager = RuleManager()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Hi {user.first_name}! I'm an auto-reply bot.\n\n"
        f"Commands:\n"
        f"/rules - Show all auto-reply rules\n"
        f"/add <pattern> | <reply> - Add a new rule\n"
        f"/remove <number> - Remove a rule by number\n"
        f"/chat_id - Show this chat's ID"
    )


async def chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    await update.message.reply_text(f"Chat ID: {chat.id}")


async def show_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rules = rule_manager.list_rules()
    if not rules:
        await update.message.reply_text("No rules configured.")
        return

    lines = ["📋 *Auto-Reply Rules:*\n"]
    for i, (pattern, reply) in enumerate(rules, 1):
        lines.append(f"{i}. `{pattern}` → _{reply}_")

    await update.message.reply_text(
        "\n".join(lines), parse_mode="Markdown"
    )


async def add_rule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text[len("/add "):].strip()
    if " | " not in text:
        await update.message.reply_text(
            "Usage: `/add <pattern> | <reply>`\n"
            "Example: `/add howdy | Howdy partner!`",
            parse_mode="Markdown",
        )
        return

    pattern, reply = text.split(" | ", 1)
    pattern = pattern.strip()
    reply = reply.strip()

    try:
        re.compile(pattern)
    except re.error as e:
        await update.message.reply_text(f"Invalid regex pattern: {e}")
        return

    rule_manager.add_rule(pattern, reply)
    await update.message.reply_text(
        f"✅ Rule added:\n`{pattern}` → _{reply}_",
        parse_mode="Markdown",
    )


async def remove_rule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        index = int(update.message.text[len("/remove "):].strip()) - 1
    except (ValueError, IndexError):
        await update.message.reply_text(
            "Usage: `/remove <number>`\n"
            "Use `/rules` to see rule numbers.",
            parse_mode="Markdown",
        )
        return

    rules = rule_manager.list_rules()
    if 0 <= index < len(rules):
        pattern, reply = rules[index]
        rule_manager.remove_rule(index)
        await update.message.reply_text(
            f"🗑️ Removed rule:\n`{pattern}` → _{reply}_",
            parse_mode="Markdown",
        )
    else:
        await update.message.reply_text("Invalid rule number. Use `/rules` to see numbers.")


async def auto_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()
    user = update.effective_user
    chat = update.effective_chat

    log.info(f"[{chat.id}] {user.first_name}: {text}")

    reply = rule_manager.find_match(text)
    if reply:
        log.info(f"  → Auto-reply: {reply}")
        await update.message.reply_text(reply)


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ Please set your TELEGRAM_BOT_TOKEN environment variable")
        print("   export TELEGRAM_BOT_TOKEN='your_bot_token'")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("chat_id", chat_id))
    app.add_handler(CommandHandler("rules", show_rules))
    app.add_handler(CommandHandler("add", add_rule))
    app.add_handler(CommandHandler("remove", remove_rule))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_reply))

    log.info("🤖 Bot started. Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
