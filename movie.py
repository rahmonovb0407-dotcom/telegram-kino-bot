from aiogram.fsm.state import StatesGroup, State

class MovieStates(StatesGroup):
    # Kino qidirish holati
    waiting_for_search_code = State()
    
    # Kino qo'shish bosqichlari
    waiting_for_add_code = State()
    waiting_for_add_title = State()
    waiting_for_add_desc = State()
    waiting_for_add_video = State()
    
    # Kino o'chirish bosqichi
    waiting_for_delete_code = State()
