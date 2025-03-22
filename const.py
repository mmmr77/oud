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

OPINION_SUBMIT = "پیام شما ثبت شد."

OPINION_CANCEL = "ارسال نظر لغو شد."

OPINION_TO_ADMIN = """
یک پیام از {user}
{username}
"""

HELP = """
برای لیست شاعران از دستور /poets استفاده کنید.
برای جستجو، عبارت مورد نظر خود را ارسال کنید.
برای مشاهده‌ی فهرست آثار مورد علاقه‌ی خود، دستور /favorites را وارد کنید.
"""

POETS = "شاعر مورد نظر خود را انتخاب کنید"

# TODO add "{poet} - {category}" at the beginning of the message
POEMS = "شعر مورد نظر خود را انتخاب کنید"

POET = """
درباره‌ی {poet}

{description}
"""

POEM = """
<a href="{url}">{title}</a>

{poem}

{poet}
@oud_poem_bot
"""

INVALID_COMMAND = "دستور داده شده نامعتبر است."

SEARCH_NO_RESULT = "هیچ نتیجه‌ای یافت نشد."

SEARCH_RESULT_COUNT = "جستجوی شما {count} نتیجه داشت."

SEARCH_NOT_ENOUGH_CHARACTERS = "عبارت جستجو باید دارای حداقل سه حرف باشد."

ADMIN_SEND_TO_ALL = "پیام مورد نظر خود را ارسال کنید."

ADMIN_SUCCESSFUL_SEND_TO_ALL = "پیام شما ارسال شد."

RECITATION_COUNT = """
برای این اثر {count} خوانش موجود است. خوانش مورد نظر خود را انتخاب کنید.
خوانش‌ها به صورت کلی از دو نوع "ساده" و "همراه با تفسیر" هستند که عبارت داخل پرانتز آن را مشخص می‌کند.
"""

FAVORITE_ADD = "اضافه به علاقه‌مندی‌ها ❤️"

FAVORITE_ADDED = "به علاقه‌مندی‌ها اضافه شد."

FAVORITE_ALREADY_IN_FAVORITES = "این شعر از قبل در فهرست علاقه‌مندی‌های شما ثبت شده است."

FAVORITE_REMOVE = "حذف از علاقه‌مندی‌ها 💔"

FAVORITE_REMOVED = "از علاقه‌مندی‌ها حذف شد."

FAVORITE_NOT_IN_FAVORITES = "این شعر در فهرست علاقه‌مندی‌های شما نیست."

FAVORITE_NO_RESULT = "شما شعری را به علاقه‌مندی‌های خود اضافه نکرده‌اید."

FAVORITE_NO_MORE_ADD_ALLOWED = "خطا: حداکثر تعداد مجاز برای آثار مورد علاقه {count} عدد است."

OMEN_INTRO = """ایرانیان طبق رسوم قدیمی خود در روزهای عید ملی یا مذهبی نظیر نوروز و یا شب یلدا، با کتاب حافظ فال می‌گیرند. در میان ایرانیان این باور وجود دارد که شیخ حافظ شیرازی داننده اسرار نهان می‌باشد و هنگام مواجه شدن با مشکلات یا دو راهی‌های زندگی با گرفتن فال حافظ می‌توانند تصمیم درست را بگیرند.

توصیه می‌شود قبل از گرفتن فال حافظ، مقدمات آن را فراهم کرده و با آرامش و خلوص نیت به فال گیری اقدام کنید. فال گیرنده، ابتدا باید در دل نیت و حاجت خود را بیان کند. نیت مهم‌ترین بخش فال حافظ است. سپس برخی برای شادی روح حافظ فاتحه یا صلواتی نثار می‌کنند. آنگاه پس از ذکر عبارتی که معمولا به شکل روبرو گفته می‌شود فال خود را می‌خوانند: <b>ای حافظ شیرازی! تو محرم هر رازی! تو را به خدا و به شاخ نباتت قسم می‌دهم که هر چه صلاح و مصلحت می‌بینی برایم آشکار و آرزوی مرا برآورده سازی</b>.

مطمئنا بهترین تعبیر کننده‌ی فال حافظ برای شما خودتان هستید. تشخیص خوب و بد از محتوای غزل، بستگی به وضعیت روحی، عاطفی و باور صاحب فال دارد. در هر صورت در هر غزل حافظ بیتی وجود دارد که صاحب فال آن را مناسب آرزو و نیت خود می‌یابد و همان را به عنوان وصف الحال و جواب حافظ می‌پذیرد.
"""

OMEN_RESULT = """
تعبیر:

{interpretation}

@oud_poem_bot
"""

__all__ = ("ABOUT", "OPINION", "HELP")
