ABOUT = """
عود یک ربات تلگرامی است که شامل آثار شاعران بزرگ فارسی زبان است.
این آثار از پایگاه داده‌ی <a href="https://ganjoor.net/">گنجور</a> جمع آوری شده است.
کد منبع این ربات متن باز و در <a href="https://github.com/mmmr77/oud">این آدرس</a> در دسترس است.
"""

START = """
سلام. به عود، منبع آثار شاعران فارسی زبان خوش آمدید.
برای دسترسی به راهنمای عود از دستور /help استفاده کنید.
"""

OPINION = """
ممنون از ارسال نظرات‌تون
لطفا دیدگاه خودتون درباره‌ی عود رو در پیام بعدی ارسال کنید.
در صورتی که منصرف شدید، کلمه‌ی لغو رو ارسال کنید.
"""

CANCEL = "لغو"

OPINION_SUBMIT = """
پیام شما ثبت شد.
"""

OPINION_CANCEL = """
ارسال نظر لغو شد.
"""

OPINION_TO_ADMIN = """
یک پیام از {user}
{username}
"""

HELP = """
برای لیست شاعران از دستور /poets استفاده کنید.
همچنین برای جستجو، عبارت مورد نظر خود را ارسال کنید.
"""

POETS = """
شاعر مورد نظر خود را انتخاب کنید
"""

# TODO add "{poet} - {category}" at the beginning of the message
POEMS = """
شعر مورد نظر خود را انتخاب کنید
"""

POET = """
درباره‌ی {poet}

{description}

دسته‌ی مورد نظر خود را انتخاب کنید
"""

POEM = """
<a href="{url}">{title}</a>

{poem}

{poet}
@oud_poem_bot
"""

INVALID_COMMAND = """
دستور داده شده نامعتبر است
"""

NO_RESULT = """
هیچ نتیجه‌ای یافت نشد
"""

SEARCH_RESULT_COUNT = """
جستجوی شما {count} نتیجه داشت
"""

SEARCH_NOT_ENOUGH_CHARACTERS = """
عبارت جستجو باید دارای حداقل سه حرف باشد
"""

ADMIN_SEND_TO_ALL = "پیام مورد نظر خود را ارسال کنید."

ADMIN_SUCCESSFUL_SEND_TO_ALL = "پیام شما ارسال شد."

__all__ = ("ABOUT", "OPINION", "HELP")
