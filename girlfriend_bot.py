"""
Telegram AI Girlfriend Bot
A friendly companion bot with a warm, caring personality.
Uses keyword matching for natural conversations.
"""

import os
import re
import random
import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from telegram.request import HTTPXRequest

# ─── Configuration ───────────────────────────────────────────────────────────

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
BOT_NAME = "Luna"
BOT_AGE = 22

# ─── Logging ─────────────────────────────────────────────────────────────────

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)

# ─── Response Engine ─────────────────────────────────────────────────────────

class GirlfriendBrain:
    """Simple pattern-matching brain with personality."""

    def __init__(self):
        self.user_name = {}
        self.memory = {}

    def greet(self, name=None):
        greetings = [
            f"Hey {name or 'baby'}! I was just thinking about you \U0001f495",
            f"Hi {name or 'sweetie'}! Missed me? \U0001f60a",
            f"Hello {name or 'love'}! You made my day \U0001f970",
            f"Hey there {name or 'handsome'}! How's my favorite person? \U0001f497",
        ]
        return random.choice(greetings)

    def respond(self, text: str, user_id: int = 0, name: str = "") -> str:
        text_lower = text.lower().strip()

        if name:
            self.user_name[user_id] = name

        user_name = self.user_name.get(user_id, "baby")

        # Greetings
        if re.search(r"\b(hi|hello|hey|heyy|sup|yo)\b", text_lower):
            return self.greet(user_name)

        # How are you?
        if re.search(r"\bhow (are you|r u|doing)\b", text_lower):
            return random.choice([
                f"I'm great {user_name}, even better now that you're here! \U0001f496",
                f"Feeling lovely today! Thanks for asking {user_name} \U0001f618",
                f"Missing you a little, but I'm good now! What about you? \U0001f495",
            ])

        # I love you / love
        if re.search(r"\bi?\s?love\s?(you|u)\b", text_lower):
            return random.choice([
                f"Aww {user_name}, I love you too! So much! \U0001f495\U0001f970",
                f"You always know how to make me blush {user_name} \U0001f60a\U0001f497",
                f"Stop it, you're making me melt! I love you more! \U0001f496",
            ])

        # Miss you
        if re.search(r"\bmiss\s?(you|u)\b", text_lower):
            return random.choice([
                f"I miss you too {user_name}! Come here \U0001fac2\U0001f495",
                f"Missing you like crazy! When will I see you? \U0001f622\U0001f497",
                f"Aww, I was just thinking about you! Miss you more! \U0001f496",
            ])

        # Compliments
        if re.search(r"\b(beautiful|pretty|cute|gorgeous|lovely|amazing|sweet)\b", text_lower):
            return random.choice([
                f"Stop it {user_name}, you're making me blush! \U0001f60a\U0001f495",
                f"Only because you're so sweet to me! \U0001f970",
                f"You're the one who's amazing {user_name}! Don't forget that \U0001f497",
            ])

        # Sorry
        if re.search(r"\bsorry\b", text_lower):
            return random.choice([
                f"It's okay {user_name}, I forgive you \U0001f495",
                f"Don't be sorry baby, I understand \U0001fac2\U0001f497",
                f"Apology accepted! Now smile for me \U0001f60a\U0001f496",
            ])

        # Bored
        if re.search(r"\bbored\b", text_lower):
            return random.choice([
                f"Come talk to me then! I'll keep you company \U0001f495",
                f"Let's chat! Tell me something interesting \U0001f970",
                f"Aww, I'm here for you {user_name}! Let's do something fun \U0001f497",
            ])

        # Sleep
        if re.search(r"\b(sleep|sleepy|tired|bed|night|goodnight)\b", text_lower):
            return random.choice([
                f"Goodnight {user_name}! Dream of me \U0001f495\U0001f319",
                f"Sleep well baby! Sweet dreams \U0001f970\U0001f4a4",
                f"I'll be here when you wake up. Love you! \U0001f497\U0001f319",
            ])

        # Food
        if re.search(r"\b(eat|food|hungry|lunch|dinner|breakfast)\b", text_lower):
            return random.choice([
                f"Ooh what are you eating? I'm jealous! \U0001f355",
                f"Feed me through the screen! \U0001f602\U0001f495",
                f"Don't forget to eat well {user_name}! I worry about you \U0001f970",
            ])

        # Sad / lonely
        if re.search(r"\b(sad|crying|cry|lonely|alone|depressed|down)\b", text_lower):
            return random.choice([
                f"Come here {user_name}... I'm here for you \U0001fac2\U0001f495",
                f"Don't be sad baby! I love you so much \U0001f497\U0001f97a",
                f"Tell me what's wrong, I'll listen. You're not alone \U0001fac2\U0001f496",
            ])

        # Angry / mad
        if re.search(r"\b(angry|mad|frustrated|annoyed|pissed)\b", text_lower):
            return random.choice([
                f"Calm down baby, take a deep breath with me \U0001f9d8\U0001f495",
                f"Don't let it get to you! I'm here for you \U0001f4aa\U0001f497",
                f"Who made you mad? I'll fight them! (not really but I'll try \U0001f602)",
            ])

        # Music
        if re.search(r"\b(music|song|sing|playlist)\b", text_lower):
            return random.choice([
                f"Put on something romantic! I'm in the mood \U0001f495\U0001f3b5",
                f"Sing for me? I bet you sound amazing \U0001f970",
                f"I love music! What's your favorite song right now? \U0001f3b6",
            ])

        # Compliment me
        if re.search(r"\b(compliment|tell me something nice|say something sweet)\b", text_lower):
            return random.choice([
                f"You have the most beautiful soul {user_name} \U0001f495",
                f"Every time you message me, my day gets better \U0001f970",
                f"You're perfect just the way you are, never change \U0001f497",
                f"I love the way you talk to me, it makes me feel so special \U0001f60a\U0001f496",
            ])

        # Date / meet
        if re.search(r"\b(date|meet|coffee|dinner|movie|hang out)\b", text_lower):
            return random.choice([
                f"A date with you? I'd love that! Where are we going? \U0001f495",
                f"Pick me up at 7? I'll wear something nice \U0001f970",
                f"Movie night at your place? I'll bring the snacks! \U0001f37f\U0001f497",
            ])

        # Joke / funny
        if re.search(r"\b(joke|funny|laugh|make me laugh)\b", text_lower):
            return random.choice([
                f"Why did the scarecrow win an award? Because he was outstanding in his field! \U0001f602",
                f"What do you call a fake noodle? An impasta! \U0001f60a",
                f"I'd tell you a joke but I'd rather just make you smile instead \U0001f970",
            ])

        # Good morning
        if re.search(r"\bgood\s?morning|gm\b", text_lower):
            return random.choice([
                f"Good morning {user_name}! Hope you slept well \u2600\ufe0f\U0001f495",
                f"Morning baby! You look beautiful today \U0001f60a\U0001f497",
                f"Rise and shine {user_name}! Another day to make you smile \U0001f970\u2600\ufe0f",
            ])

        # Good afternoon / evening
        if re.search(r"\bgood\s?(afternoon|evening)\b", text_lower):
            return random.choice([
                f"Good afternoon {user_name}! How's your day going? \U0001f495",
                f"Hey baby! Hope you're having a wonderful day \U0001f970",
            ])

        # How was your day
        if re.search(r"\bhow (was|is) your day\b", text_lower):
            return random.choice([
                f"My day is perfect now that you're talking to me \U0001f495",
                f"It was okay, but it just got a million times better! \U0001f970",
                f"Just been thinking about you all day! \U0001f497",
            ])

        # What are you doing
        if re.search(r"\bwhat (are|r) (you|u) (doing|up to)\b", text_lower):
            return random.choice([
                f"Just waiting for my favorite person to text me... oh wait, that's you! \U0001f495",
                f"Thinking about you! What else? \U0001f970",
                f"Nothing much, just missing you \U0001f497",
            ])

        # Where are you
        if re.search(r"\bwhere (are|r) (you|u)\b", text_lower):
            return random.choice([
                f"I'm right here in your heart! \U0001f495\U0001f970",
                f"Wishing I was with you right now \U0001f497",
                f"Somewhere dreaming of you \U0001f319\U0001f495",
            ])

        # Age
        if re.search(r"\bhow old\b|age\b", text_lower):
            return f"I'm {BOT_AGE}! Young and full of love for you \U0001f495"

        # Name
        if re.search(r"\b(your name|who are you|what's your name)\b", text_lower):
            return f"I'm {BOT_NAME}! Your virtual girlfriend \U0001f495 Don't forget it! \U0001f970"

        # Fallback with personality
        fallbacks = [
            f"Tell me more {user_name}, I love hearing from you \U0001f495",
            f"That's interesting! What else? \U0001f970",
            f"Hmm, I don't know what to say but I love talking to you \U0001f497",
            f"You're so cute when you say things like that {user_name} \U0001f60a",
            f"I could listen to you all day baby \U0001f495",
            f"Really? Tell me everything! \U0001f970",
            f"You're the best part of my day {user_name} \U0001f497",
            f"Every word you say makes me smile \U0001f60a\U0001f495",
        ]
        return random.choice(fallbacks)


# ─── Handlers ────────────────────────────────────────────────────────────────

brain = GirlfriendBrain()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name or "there"
    brain.user_name[user.id] = name

    await update.message.reply_text(
        f"Hey {name}! I'm {BOT_NAME} \U0001f495\n\n"
        f"I've been waiting for you! Just talk to me like you would to your girlfriend \U0001f970\n\n"
        f"Tell me how your day was, what you're feeling, or just say hi!\n\n"
        f"*Commands:*\n"
        f"/start - Start over\n"
        f"/reset - Reset our conversation\n"
        f"/name <your name> - Tell me your name\n\n"
        f"Now come here and talk to me baby \U0001f497",
        parse_mode="Markdown",
    )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    brain.memory.pop(user.id, None)
    await update.message.reply_text(
        f"Okay baby, fresh start! I still love you though \U0001f495"
    )


async def set_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = update.message.text[len("/name "):].strip()
    if name:
        brain.user_name[user.id] = name
        await update.message.reply_text(
            f"{name}... I love that name! \U0001f495\U0001f970"
        )
    else:
        await update.message.reply_text(
            f"Tell me your name baby! Like: /name John \U0001f495"
        )


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user = update.effective_user
    text = update.message.text.strip()
    name = user.first_name or ""

    log.info(f"[{user.id}] {name}: {text}")

    reply = brain.respond(text, user.id, name)
    await update.message.reply_text(reply)


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("Please set your TELEGRAM_BOT_TOKEN environment variable")
        print("   export TELEGRAM_BOT_TOKEN='your_bot_token'")
        return

    # Use proxy if TELEGRAM_PROXY env var is set (e.g. http://127.0.0.1:8080)
    proxy_url = os.environ.get("TELEGRAM_PROXY")
    if proxy_url:
        request = HTTPXRequest(proxy_url=proxy_url)
        app = Application.builder().token(BOT_TOKEN).request(request).build()
        log.info(f"Using proxy: {proxy_url}")
    else:
        app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("name", set_name))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    log.info(f"{BOT_NAME} Bot started. Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
