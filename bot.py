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
        "title": "Время на работу",
        "text": (
            "📝 *Вопрос 1 из 14*\n\n"
            "Сколько часов в день ты готов уделять работе?\n\n"
            "1 — Меньше 2 часов\n"
            "2 — 2–4 часа\n"
            "3 — 4–6 часов\n"
            "4 — 6+ часов\n\n"
            "_Напиши цифру или свой ответ_ 👇"
        )
    },
    {
        "num": 2,
        "title": "Следование инструкциям",
        "text": (
            "📝 *Вопрос 2 из 14*\n\n"
            "Если тебе дали чёткую инструкцию — ты будешь следовать ей или делать по-своему?\n\n"
            "1 — Строго по инструкции\n"
            "2 — В основном по инструкции, но иногда добавлю своё\n"
            "3 — Буду делать как считаю нужным\n\n"
            "_Напиши цифру или свой ответ_ 👇"
        )
    },
    {
        "num": 3,
        "title": "Скорость ответа",
        "text": (
            "📝 *Вопрос 3 из 14*\n\n"
            "Как быстро ты отвечаешь на сообщения когда работаешь?\n\n"
            "1 — Моментально, всегда на связи\n"
            "2 — В течение 5–10 минут\n"
            "3 — Когда удобно, могу задержаться\n\n"
            "_Напиши цифру или свой ответ_ 👇"
        )
    },
    {
        "num": 4,
        "title": "Опыт работы",
        "text": (
            "📝 *Вопрос 4 из 14*\n\n"
            "Был ли у тебя опыт работы чатером или в переписках с клиентами?\n\n"
            "1 — Да, есть опыт\n"
            "2 — Нет, но быстро учусь\n"
            "3 — Нет и не уверен что справлюсь\n\n"
            "_Напиши цифру или свой ответ_ 👇"
        )
    },
    {
        "num": 5,
        "title": "Непонятная задача",
        "text": (
            "📝 *Вопрос 5 из 14*\n\n"
            "Что ты сделаешь если не понимаешь задачу?\n\n"
            "1 — Спрошу у руководителя\n"
            "2 — Попробую разобраться сам\n"
            "3 — Сделаю как понял и не буду беспокоить\n\n"
            "_Напиши цифру или свой ответ_ 👇"
        )
    },
    {
        "num": 6,
        "title": "Скучная задача",
        "text": (
            "📝 *Вопрос 6 из 14*\n\n"
            "Тебе дали задание. Ты начал делать и понял что это скучно и однообразно. Что сделаешь?\n\n"
            "1 — Доделаю, работа есть работа\n"
            "2 — Скажу что мне неинтересно\n"
            "3 — Брошу или начну халтурить\n\n"
            "_Напиши цифру или свой ответ_ 👇"
        )
    },
    {
        "num": 7,
        "title": "Холодный старт",
        "text": (
            "📝 *Вопрос 7 из 14 — Практика*\n\n"
            "Представь: тебе нужно прямо сейчас начать общаться с незнакомым человеком в переписке. "
            "Он ещё ничего не написал — ты пишешь первым.\n\n"
            "*Напиши своё первое сообщение* 👇"
        )
    },
    {
        "num": 8,
        "title": "Продолжение диалога",
        "text": (
            "📝 *Вопрос 8 из 14 — Практика*\n\n"
            "Человек ответил тебе коротко и сухо: *«Ну и что?»*\n\n"
            "*Как продолжишь разговор? Напиши ответ* 👇"
        )
    },
    {
        "num": 9,
        "title": "Голосовые сообщения",
        "text": (
            "📝 *Вопрос 9 из 14*\n\n"
            "Не боишься ли ты записывать голосовые сообщения?\n\n"
            "1 — Нет, всё окей, записываю легко\n"
            "2 — Немного стесняюсь, но могу\n"
            "3 — Да, некомфортно\n\n"
            "_Напиши цифру или свой ответ_ 👇"
        )
    },
    {
        "num": 10,
        "title": "Личные границы",
        "text": (
            "📝 *Вопрос 10 из 14*\n\n"
            "Работа чатера иногда требует входить в личное пространство человека — "
            "задавать личные вопросы, обсуждать чувства, быть ближе чем в обычном общении. "
            "Как ты к этому относишься?\n\n"
            "1 — Нормально, готов к этому\n"
            "2 — Зависит от ситуации\n"
            "3 — Некомфортно, это не моё\n\n"
            "_Напиши цифру или свой ответ_ 👇"
        )
    },
    {
        "num": 11,
        "title": "Выплаты",
        "text": (
            "📝 *Вопрос 11 из 14*\n\n"
            "Как быстро ты хочешь получать выплату после депозита?\n\n"
            "1 — В день депозита\n"
            "2 — В течение 1–3 дней\n"
            "3 — Раз в неделю\n"
            "4 — Гибко, как договоримся\n\n"
            "_Напиши цифру или свой ответ_ 👇"
        )
    },
    {
        "num": 12,
        "title": "Реферальная программа",
        "text": (
            "📝 *Вопрос 12 из 14*\n\n"
            "Готов ли ты принять участие в реферальной программе "
            "(приводить новых сотрудников и получать за это бонус)?\n\n"
            "1 — Да, с удовольствием\n"
            "2 — Возможно, расскажите подробнее\n"
            "3 — Нет, не интересует\n\n"
            "_Напиши цифру или свой ответ_ 👇"
        )
    },
    {
        "num": 13,
        "title": "Нейросети",
        "text": (
            "📝 *Вопрос 13 из 14*\n\n"
            "Умеешь ли ты пользоваться нейросетями (ChatGPT, Claude и подобные)?\n\n"
            "1 — Да, использую регулярно\n"
            "2 — Пробовал, но не очень разбираюсь\n"
            "3 — Нет, никогда не использовал\n\n"
            "_Напиши цифру или свой ответ_ 👇"
        )
    },
    {
        "num": 14,
        "title": "Срок сотрудничества",
        "text": (
            "📝 *Вопрос 14 из 14*\n\n"
            "На какой срок ты планируешь сотрудничать в нашем коллективе?\n\n"
            "1 — Попробую, посмотрю как пойдёт\n"
            "2 — Минимум 3–6 месяцев\n"
            "3 — Долгосрочно, планирую остаться надолго\n\n"
            "_Напиши цифру или свой ответ_ 👇"
        )
    },
]

ASK_NAME, DOING_TASKS, DONE = range(3)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "👋 Привет! Это вступительный опрос.\n\n"
        "Всего *14 вопросов* — отвечай честно и своими словами.\n\n"
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
        f"Отлично, *{name}*! Начинаем 🚀",
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
            f"📝 Вопрос {step + 1}: {TASKS[step]['title']}\n\n"
            f"{answer}"
        ),
        parse_mode="Markdown"
    )

    context.user_data["step"] += 1
    next_step = context.user_data["step"]

    if next_step < len(TASKS):
        await update.message.reply_text("✅ Принято! Следующий вопрос:")
        return await send_task(update, context)
    else:
        return await finish(update, context)


async def finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = context.user_data["name"]
    answers = context.user_data["answers"]

    report = f"🏁 *Кандидат {name} завершил опрос*\n\n"
    for i, a in enumerate(answers):
        report += f"*Вопрос {i+1}: {a['task']}*\n{a['answer']}\n\n"

    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=report,
        parse_mode="Markdown"
    )

    await update.message.reply_text(
        f"🎉 *{name}, ты прошёл опрос!*\n\n"
        "Ответы отправлены на проверку. Мы свяжемся с тобой в ближайшее время. Спасибо! 🙌",
        parse_mode="Markdown"
    )
    return DONE


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Опрос отменён. Напиши /start чтобы начать заново.")
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
