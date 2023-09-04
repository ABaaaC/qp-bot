def update_schedule_message(message: types.Message, current_page, num_pages):
    schedule = dp.storage[message.chat.id]['schedule']
    start_index = (current_page - 1) * num_items_per_page
    end_index = min(start_index + num_items_per_page, len(schedule))

    schedule_text = "\n".join([f"{i + 1 + start_index}. {item['title']} - {item['date']} at {item['time']}" for i, item in enumerate(schedule[start_index:end_index])])
    keyboard = []

    if start_index > 0:
        keyboard.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"prev_{current_page - 1}_{num_pages}"))

    keyboard.append(InlineKeyboardButton("🔙 Back", callback_data="back_to_menu"))

    if end_index < len(schedule):
        keyboard.append(InlineKeyboardButton("➡️ Next", callback_data=f"next_{current_page + 1}_{num_pages}"))

    message_text = f"Here is the schedule for your chosen city (Page {current_page}/{num_pages}):\n{schedule_text}"
    # await message.edit_text(message_text, reply_markup=InlineKeyboardMarkup([keyboard]))
    message.edit_text(message_text, reply_markup=InlineKeyboardMarkup([keyboard]))

# async def button_callback(update: Update, context: CallbackContext) -> None:
def button_callback(update: Update, context: CallbackContext) -> None:
    query = message.callback_query
    query.answer()
    num_items_per_page = dp.storage[message.chat.id].get('num_items_per_page', 5)

    if query.data.startswith("prev_") or query.data.startswith("next_"):
        action, new_page, num_pages = query.data.split("_")
        new_page = int(new_page)
        num_pages = int(num_pages)

        if 0 <= new_page <= num_pages:
            dp.storage[message.chat.id]['page'] = new_page
            current_page = new_page
            # await update_schedule_message(query.message, context, current_page, num_pages)
            update_schedule_message(query.message, context, current_page, num_pages)

    elif query.data == "schedule":
        current_page = 1  # Assuming you want to reset to the first page
        num_pages = math.ceil(len(dp.storage[message.chat.id]['schedule']) / num_items_per_page)
        # await update_schedule_message(query.message, context, current_page, num_pages)
        update_schedule_message(query.message, context, current_page, num_pages)

    elif query.data == "something":
        # await query.edit_message_text("You chose 'Something'.")
        query.edit_message_text("You chose 'Something'.")

    elif query.data == "back_to_menu":

        # await query.edit_message_text(f"Great! You chose {dp.storage[message.chat.id]['city']}.\n"
        query.edit_message_text(f"Great! You chose {dp.storage[message.chat.id]['city']}.\n"
        "Now, please choose an option from the main menu:",
        reply_markup=main_menu_keyboard())
      
def main() -> None:
    """Start the bot."""
    # dp = Dispatcher(bot, storage=MemoryStorage())
    # dispatcher = dp


    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start, run_async=True)],
        states={
            CITY_CHOICE: [MessageHandler(Filters.text & ~Filters.command, city_choice, run_async=True)],
            MAIN_MENU: [CallbackQueryHandler(main_menu, pattern='^(schedule|something)$', run_async=True),
                        CallbackQueryHandler(button_callback, run_async=True)],
        },
        fallbacks=[],
        run_async=True
        # per_message=True,
    )

    logger.info("Set conv_handler.")

    dispatcher.add_handler(conv_handler)



    # Just start the dispatcher's job queue (processes updates in the background)
    # # updater.job_queue.start()  # Check aiogram's job queue
    # # updater.idle()  # Check aiogram's way of idling
    # dp.

# if __name__ == "__main__":
#     main() #

# https://api.telegram.org/bot6521875912:AAG-a7eTLXEC_6JJupnLpQ3STTuYD-gyhME/setWebhook?url=https://curious-frequently-katydid.ngrok-free.app/webhook/6521875912:AAG-a7eTLXEC_6JJupnLpQ3STTuYD-gyhME