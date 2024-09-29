from persian_tools import digits

import const


class Util:
    @staticmethod
    def trim_search_results(results: list[tuple], offset: int) -> list:
        message = list()
        for i, result in enumerate(results):
            a = (i + 1 + offset, result[0], digits.convert_to_fa(i + 1 + offset) + '. ' + result[1] + ' - ' + result[3] + '\n' + result[2])
            if len(a[2]) + sum(map(lambda x: len(x[2]), message)) + 2 * len(message) <= 4096:
                message.append(a)
            else:
                return message
        return message

    @staticmethod
    def break_long_verses(poem_text: list[tuple]) -> list:
        new_poem_text: list = list()
        for verse in poem_text:
            if len(verse[0]) > 3800:
                separation_index = verse[0].rfind('.', 0, 3800)
                new_poem_text.append(verse[0][:separation_index+1])
                new_poem_text.append(verse[0][separation_index+1:])
            else:
                new_poem_text.append(verse[0])
        return new_poem_text

    @staticmethod
    def format_poem(poem, url, title, poet):
        return const.POEM.format(poem=poem, url=url, title=title, poet=poet)

    @staticmethod
    def break_long_poems(poem_text: list[str], poem_info) -> list:
        messages = list()
        poem_in_a_single_message = ''
        for verse in poem_text:
            message = Util.format_poem(poem_in_a_single_message + verse, poem_info[1], poem_info[0], poem_info[2])
            if len(message) > 4096:
                messages.append(Util.format_poem(poem_in_a_single_message, poem_info[1], poem_info[0], poem_info[2]))
                poem_in_a_single_message = verse
            else:
                poem_in_a_single_message += verse + '\n'
        messages.append(Util.format_poem(poem_in_a_single_message, poem_info[1], poem_info[0], poem_info[2]))
        return messages
