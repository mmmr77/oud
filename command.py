import const


class Command:
    @staticmethod
    def get_command_response(command: str):
        command_upper = command.upper()
        if command_upper in const.__all__:
            return eval(f'const.{command_upper}')
        else:
            return const.COMMAND_NOT_FOUND
