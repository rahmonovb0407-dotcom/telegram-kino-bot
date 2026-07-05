from aiogram.fsm.state import StatesGroup, State

class ChannelStates(StatesGroup):
    # Majburiy kanal qo'shish holati
    waiting_for_channel_id = State()
    # Majburiy kanal o'chirish holati
    waiting_for_delete_channel = State()
