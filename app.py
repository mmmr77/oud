from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler, \
    CallbackQueryHandler, ConversationHandler

from admin import Admin
from command import Command
from favorite import Favorite
from poem import Poem
from poet import Poet
from recitation import Recitation
from search import Search


class Application:
    def __init__(self, token: str):
        self.application = ApplicationBuilder().token(token).build()
        self.add_handlers()

    def start_app(self):
        self.application.run_polling()

    def add_handlers(self):
        start_handler = CommandHandler('start', Command.start)

        opinion_handler = ConversationHandler(entry_points=[CommandHandler('opinion', Command.opinion)],
                                              states={0: [MessageHandler(filters.ALL & ~filters.Regex(r'^لغو$'),
                                                                         Command.opinion_response)]},
                                              fallbacks=[
                                                  MessageHandler(filters.Regex(r'^لغو$'), Command.opinion_cancel)])

        poets_handler = CommandHandler('poets', Poet.poets_menu)

        poet_details_handler = CallbackQueryHandler(Poet.poet_details, r'^poet:\d+:\d+$')

        category_handler = CallbackQueryHandler(Poem.category_poems, r'^category:\d+:\d+$')

        poem_handler = CallbackQueryHandler(Poem.show_poem_by_id, r'^poem:\d+$')

        commands_handler = MessageHandler(filters.COMMAND, Command.general_command)

        recitation_saver_data_handler = MessageHandler(filters.TEXT & filters.ChatType.CHANNEL,
                                                 Recitation.add_recitation_data_to_db)

        search_message_handler = MessageHandler(filters.TEXT, Search.search_poems)

        search_query_handler = CallbackQueryHandler(Search.search_poems, r'^search:.+:\d+$')

        recitation_saver_audio_handler = MessageHandler(filters.AUDIO & filters.ChatType.CHANNEL,
                                                  Recitation.add_recitation_file_id_to_db)

        recitation_handler = CallbackQueryHandler(Recitation.get_recitation_by_id, r'^recitation:\d+$')

        send_to_all_handler = ConversationHandler(entry_points=[CommandHandler('sendtoall', Command.sendtoall)],
                                                  states={0: [MessageHandler(filters.TEXT, Admin.send_to_all)]},
                                                  fallbacks=[])

        favorite_add_handler = CallbackQueryHandler(Favorite.add_to_favorites, r'^favadd:\d+$')

        favorite_remove_handler = CallbackQueryHandler(Favorite.remove_from_favorites, r'^favremove:\d+$')

        favorite_poems_handler = CommandHandler('favorites', Favorite.list_of_favorite_poems)

        favorite_poems_query_handler = CallbackQueryHandler(Favorite.list_of_favorite_poems, r'^favorites:\d+$')

        self.application.add_handlers(
            [start_handler, opinion_handler, poets_handler, poet_details_handler, category_handler, poem_handler,
             send_to_all_handler, recitation_saver_data_handler, recitation_saver_audio_handler, search_query_handler,
             recitation_handler, favorite_add_handler, favorite_remove_handler, favorite_poems_handler,
             favorite_poems_query_handler, commands_handler, search_message_handler])
