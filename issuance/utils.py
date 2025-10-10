from num2words import num2words


def num_to_word_rial(value):
    try:
        number = int(value)
        return num2words(number, lang='fa') + " ریال"
    except:
        return ""
