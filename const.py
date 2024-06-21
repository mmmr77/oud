ABOUT = """
عود یک ربات تلگرامی است که شامل آثار شاعران بزرگ فارسی زبان است.
این آثار از پایگاه داده‌ی <a href="https://ganjoor.net/">گنجور</a> جمع آوری شده است.
کد منبع این ربات متن باز و در <a href="https://github.com/mmmr77/oud">این آدرس</a> در دسترس است.
"""

START = """
سلام. من عود هستم. منبع آثار شاعران فارسی زبان
برای دسترسی به راهنمای عود از دستور /help استفاده کنید
"""

# TODO maybe i have to add a conversation handler for this?
OPINION = """
ممنون از ارسال نظرات‌تون
لطفا دیدگاه خودتون درباره‌ی عود رو در پیام بعدی ارسال کنید
"""

HELP = """
برای لیست شاعران از دستور /poets استفاده کنید
"""

WHY_OUD = """
عود هم یک ساز موسیقیه هم یک چوب خوشبو
"""

POETS = """
شاعر مورد نظر خود را انتخاب کنید
"""

POEMS = """
شعر مورد نظر خود را انتخاب کنید
"""

POET = """
درباره‌ی {poet}

{description}

دسته‌ی مورد نظر خود را انتخاب کنید
"""

# TODO if a poem does not have a url // add poet at the end of the poem
POEM = """
<a href="{url}">{title}</a>

{poem}


@oud_poem_bot
"""

COMMAND_NOT_FOUND = """
دستور داده شده نامعتبر است
"""

__all__ = ("ABOUT", "START", "OPINION", "HELP", "WHY_OUD")
