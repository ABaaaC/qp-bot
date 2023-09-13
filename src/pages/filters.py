from src.consts import GameType, ConversationStates, logger
from src.pages.utils import get_filter_button_builder, main_menu_message, filter_apply
# from src.bot import form_router

from aiogram import types, Router 

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

filter_router = Router()


@filter_router.callback_query(ConversationStates.FILTER)
async def process_filters(query: types.CallbackQuery, state: FSMContext):
    logger.info("city_choice STARTED")
    state_data = await state.get_data()

    if query.data == 'save':
        
        await filter_apply(state)

        city = state_data.get('city')
        await main_menu_message(query, city)
    
        await state.set_state(ConversationStates.MAIN_MENU)

    elif query.data in GameType.__members__:
        name = query.data
        game_type = getattr(GameType, name)
        filter_game_flags = state_data.get('filter_game_flags')
        filter_game_flags[game_type] = not filter_game_flags[game_type]
        await state.update_data({'filter_game_flags' : filter_game_flags})
        builder = get_filter_button_builder(filter_game_flags)
        await query.message.edit_reply_markup(reply_markup=builder.as_markup())

async def filter_game(message: Message, state: FSMContext):
    state_data = await state.get_data()
    filter_game_flags = state_data.get('filter_game_flags')
    builder = get_filter_button_builder(filter_game_flags)
    # await message.edit_text(text = 'Choose interesting games:', reply_markup=builder.as_markup())
    await message.edit_text(text = 'Какие игры оставить?', reply_markup=builder.as_markup())