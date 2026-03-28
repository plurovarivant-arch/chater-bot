import logging
import os
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]
ADMIN_CHAT_ID = int(os.environ["ADMIN_CHAT_ID"])

TASKS = [
    {
        "num": 1,
        "title": "Холодный старт",
        "text": (
            "📝 *Задание 1 из 5 — Холодный старт*\n\n"
            "Ты ведёшь аккаунт блогера в Instagram. Новый подписчик написал просто: *«Привет»*\n\n"
            "Напиши ответ, который завяжет разговор и мягко поведёт его к покупке "
            "(платная подписка / курс / услуга — выбери сам что продаёшь).\n\n"
            "_Напиши свой ответ ниже_ 👇"
        )
    },
    {
        "num": 2,
        "title": "Работа с возражением",
        "text": (
            "📝 *Задание 2 из 5 — Работа с возражением*\n\n"
            "Пользователь говорит: *«Дорого, не буду покупать»*\n\n"
            "Напиши *2 варианта* ответа:\n"
            "1️⃣ Мягкий\n"
            "2️⃣ Более настойчивый\n\n"
            "_Напиши оба варианта ниже_ 👇"
        )
    },
    {
        "num": 3,
        "title": "Дожим",
        "text": (
            "📝 *Задание 3 из 5 — Дожим*\n\n"
            "Человек неделю назад интересовался продуктом, потом пропал.\n\n"
            "Напиши ему сообщение, которое *вернёт интерес* и подтолкнёт к покупке. "
            "Без спама и давления — мягко, но убедительно.\n\n"
            "_Напиши своё сообщение ниже_ 👇"
        )
    },
    {
        "num": 4,
        "title": "Tone of voice",
        "text": (
            "📝 *Задание 4 из 5 — Tone of voice*\n\n"
            "Описание аккаунта:\n"
            "_Молодая девушка, 23 года, лайфстайл блог, продаёт курс по уходу за собой. "
            "Тон — дружеский, немного дерзкий._\n\n"
            "Напиши *3 разных сообщения* подписчику в этом стиле.\n\n"
            "_Напиши все три ниже_ 👇"
        )
    },
    {
        "num": 5,
        "title": "Сложный пользователь",
        "text": (
            "📝 *Задание 5 из 5 — Сложный пользователь*\n\n"
            "Человек пишет: *«Слушай, ты скучная, надоела уже»*\n\n"
            "Напиши ответ — не потеряй человека, не уходи в оборону, "
            "постарайся перевернуть ситуацию.\n\n"
            "_Напиши свой ответ ниже_ 👇"
        )
    },
]

ASK_NAME, DOING_TASKS, DONE = range(3)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "👋 Привет! Это вступительный тест для чатеров.\n\n"
        "Тебя ждёт *5 заданий* — отвечай честно и своими словами, "
        "шаблонные ответы сразу видно 😉\n\n"
        "Как тебя зовут?",
        parse_mode="Markdown"
    )
    return ASK_NAME


async def got_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    context.user_data["name"] = name
    context.user_data["step"] = 0
    context.user_data["answers"] = []

    await update.message.reply_text(
        f"Отлично, *{name}*! Начинаем 🚀\n\n"
        "Читай задание внимательно и отвечай развёрнуто. Удачи!",
        parse_mode="Markdown"
    )
    return await send_task(update, context)


async def send_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data["step"]
    task = TASKS[step]
    await update.message.reply_text(task["text"], parse_mode="Markdown")
    return DOING_TASKS


async def got_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data["step"]
    name = context.user_data["name"]
    answer = update.message.text.strip()

    context.user_data["answers"].append({
        "task": TASKS[step]["title"],
        "answer": answer
    })

    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=(
            f"📬 *Новый ответ*\n"
            f"👤 Кандидат: *{name}*\n"
            f"📝 Задание {step + 1}: {TASKS[step]['title']}\n\n"
            f"{answer}"
        ),
        parse_mode="Markdown"
    )

    context.user_data["step"] += 1
    next_step = context.user_data["step"]

    if next_step < len(TASKS):
        await update.message.reply_text("✅ Принято! Следующее задание:")
        return await send_task(update, context)
    else:
        return await finish(update, context)


async def finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = context.user_data["name"]
    answers = context.user_data["answers"]

    report = f"🏁 *Кандидат {name} завершил тест*\n\n"
    for i, a in enumerate(answers):
        report += f"*Задание {i+1}: {a['task']}*\n{a['answer']}\n\n"

    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=report,
        parse_mode="Markdown"
    )

    await update.message.reply_text(
        f"🎉 *{name}, ты прошёл тест!*\n\n"
        "Все ответы отправлены на проверку. Мы свяжемся с тобой в ближайшее время. Спасибо! 🙌",
        parse_mode="Markdown"
    )
    return DONE


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Тест отменён. Напиши /start чтобы начать заново.")
    return ConversationHandler.END


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, got_name)],
            DOING_TASKS: [MessageHandler(filters.TEXT & ~filters.COMMAND, got_answer)],
            DONE: [CommandHandler("start", start)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
