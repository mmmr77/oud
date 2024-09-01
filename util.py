from persian_tools import digits


class Util:
    @staticmethod
    def classify_search_results(results: list[tuple]) -> list:
        messages = list()
        message = list()
        for i, result in enumerate(results):
            a = (i + 1, result[0], digits.convert_to_fa(i + 1) + '. ' + result[1] + ' - ' + result[3] + '\n' + result[2])
            if len(a[2]) + sum(map(lambda x: len(x[2]), message)) < 3950:
                message.append(a)
            else:
                messages.append(message)
                message = [a]
        messages.append(message)
        return messages
