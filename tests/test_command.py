from command import Command


def test_parse_command_name_works_without_a_mention():
    assert Command.parse_command_name("/about", "oud_bot") == "about"


def test_parse_command_name_strips_the_bot_mention():
    # Group clients append "@bot_username" to commands; private chats don't.
    assert Command.parse_command_name("/about@oud_bot", "oud_bot") == "about"


def test_parse_command_name_is_case_insensitive_about_the_mention():
    assert Command.parse_command_name("/about@Oud_Bot", "oud_bot") == "about"


def test_parse_command_name_ignores_trailing_arguments():
    assert Command.parse_command_name("/about extra text", "oud_bot") == "about"


def test_parse_command_name_returns_none_for_a_different_bots_command():
    assert Command.parse_command_name("/roll@dice_bot", "oud_bot") is None
