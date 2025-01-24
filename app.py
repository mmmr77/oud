from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler, \
    CallbackQueryHandler, ConversationHandler

from admin import Admin
from command import Command
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

        recitation_data_handler = MessageHandler(filters.TEXT & filters.ChatType.CHANNEL,
                                                 Recitation.add_recitation_data_to_db)

        search_message_handler = MessageHandler(filters.TEXT, Search.search_poems)

        search_query_handler = CallbackQueryHandler(Search.search_poems, r'^search:.+:\d+$')

        recitation_audio_handler = MessageHandler(filters.AUDIO & filters.ChatType.CHANNEL,
                                                  Recitation.add_recitation_file_id_to_db)

        send_to_all_handler = ConversationHandler(entry_points=[CommandHandler('sendtoall', Command.sendtoall)],
                                                  states={0: [MessageHandler(filters.TEXT, Admin.send_to_all)]},
                                                  fallbacks=[])

        self.application.add_handlers(
            [start_handler, opinion_handler, poets_handler, poet_details_handler, category_handler, poem_handler,
             send_to_all_handler, commands_handler, recitation_data_handler, recitation_audio_handler,
             search_query_handler, search_message_handler])
