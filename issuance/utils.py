import jdatetime
from num2words import num2words


def num_to_word_rial(value):
    try:
        number = int(value)
        return num2words(number, lang='fa') + " ریال"
    except:
        return ""


def persian_to_english_numbers(input_str):
    """
    تبدیل اعداد فارسی به انگلیسی
    مثال: '۱۴۰۳/۰۶/۰۱' → '1403/06/01'
    """
    if not input_str:
        return ''
    persian_nums = '۰۱۲۳۴۵۶۷۸۹'
    english_nums = '0123456789'
    translation_table = str.maketrans(''.join(persian_nums), ''.join(english_nums))
    return input_str.translate(translation_table)


def persian_to_gregorian(jalali_str):
    """
    تبدیل رشته Jalali به datetime.date میلادی
    ورودی: '۱۴۰۳/۰۶/۰۱'
    خروجی: datetime.date
    """
    if not jalali_str:
        return None
    jalali_str = persian_to_english_numbers(jalali_str)
    try:
        year, month, day = map(int, jalali_str.split('/'))
        g_date = jdatetime.date(year, month, day).togregorian()
        return g_date
    except ValueError:
        return None


def gregorian_to_persian(g_date):
    """
    تبدیل datetime.date یا datetime.datetime میلادی به رشته Jalali 'YYYY/MM/DD'
    ورودی: datetime.date یا datetime.datetime
    خروجی: '۱۴۰۳/۰۶/۰۱'
    """
    if not g_date:
        return ''
    j_date = jdatetime.date.fromgregorian(date=g_date)
    return f"{j_date.year:04}/{j_date.month:02}/{j_date.day:02}"
