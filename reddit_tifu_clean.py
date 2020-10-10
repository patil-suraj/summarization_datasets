# adapted from https://github.com/ctr4si/MMN/blob/master/preprocessing/tokenizer.py

import re

_URL_RE = re.compile(r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>\"\']+))")


def reddit_clean_text(raw_sentence):
    sentence = raw_sentence.lower()

    # Delete word between "["~"]" and "("~")"
    sentence = re.sub(r"\[[^\]]+\]", "", sentence)
    sentence = re.sub(r"\([^\)]+\)", "", sentence)

    # Remove urls
    sentence = _URL_RE.sub("", sentence)

    # Incoporate /r/subredditname to subredditspecialtoken
    sentence = re.sub(r"/r/([^\s/]+)", "subredditspecialtoken", sentence)
    sentence = re.sub("subredditspecialtoken/", "subredditspecialtoken", sentence)

    # Incoporate /u/username to usernamespecialtoken
    sentence = re.sub(r"/u/([^\s/]+)", "usernamespecialtoken", sentence)
    sentence = re.sub("usernamespecialtoken/", "usernamespecialtoken", sentence)

    # Delete \n
    sentence = re.sub(r"\r\n+", " ", sentence)
    sentence = re.sub(r"\n+", " ", sentence)

    # Delete -
    sentence = re.sub(r"-", " ", sentence)
    # Incorporate ; to .
    sentence = re.sub(r";", r".", sentence)

    # Remove duplicates on . , ! ?
    sentence = re.sub(r"([!?,\.\"])\1+", r"\1", sentence)

    # Remove leading punctuation
    sentence = re.sub(r"^\W+", "", sentence)
    sentence = sentence.strip()

    # Run unidecode
    return sentence
