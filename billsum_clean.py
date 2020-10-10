# Adapted from https://github.com/FiscalNote/BillSum/blob/master/billsum/data_prep/clean_text.py
import re

USC_re = re.compile(r"[Uu]\.*[Ss]\.*[Cc]\.]+")
PAREN_re = re.compile(r"\([^(]+\ [^\(]+\)")
BAD_PUNCT_RE = re.compile(r"([%s])" % re.escape(r'"#%&\*\+/<=>@[\]^{|}~_'), re.UNICODE)
BULLET_RE = re.compile(r"\n[\ \t]*`*\([a-zA-Z0-9]*\)")
DASH_RE = re.compile(r"--+")
WHITESPACE_RE = re.compile(r"\s+")
EMPTY_SENT_RE = re.compile(r"[,\.]\ *[\.,]")
FIX_START_RE = re.compile(r"^[^A-Za-z]*")
FIX_PERIOD = re.compile(r"\.([A-Za-z])")
SECTION_HEADER_RE = re.compile(r"SECTION [0-9]{1,2}\.|\nSEC\.* [0-9]{1,2}\.|Sec\.* [0-9]{1,2}\.")

FIX_PERIOD = re.compile(r"\.([A-Za-z])")

SECTION_HEADER_RE = re.compile(r"SECTION [0-9]{1,2}\.|\nSEC\.* [0-9]{1,2}\.|Sec\.* [0-9]{1,2}\.")


def replace_semicolon(text, threshold=10):
    """
    Get rid of semicolons.
    First split text into fragments between the semicolons. If the fragment
    is longer than the threshold, turn the semicolon into a period. O.w treat
    it as a comma.
    Returns new text
    """
    new_text = ""
    for subset in re.split(";", text):
        subset = subset.strip()  # Clear off spaces
        # Check word count
        if len(subset.split()) > threshold:
            # Turn first char into uppercase
            new_text += ". " + subset[0].upper() + subset[1:]
        else:
            # Just append with a comma
            new_text += ", " + subset

    return new_text


def billsum_clean_text(text):
    """
    Borrowed from the FNDS text processing with additional logic added in.
    Note: we do not take care of token breaking - assume SPACY's tokenizer
    will handle this for us.
    """

    # Indicate section headers, we need them for features
    text = SECTION_HEADER_RE.sub("SECTION-HEADER", text)
    # For simplicity later, remove '.' from most common acronym
    text = text.replace("U.S.", "US")
    text = text.replace("SEC.", "Section")
    text = text.replace("Sec.", "Section")
    text = USC_re.sub("USC", text)

    # Remove parantheticals because they are almost always references to laws
    # We could add a special tag, but we just remove for now
    # Note we dont get rid of nested parens because that is a complex re
    # text = PAREN_re.sub('LAWREF', text)
    text = PAREN_re.sub("", text)

    # Get rid of enums as bullets or ` as bullets
    text = BULLET_RE.sub(" ", text)

    # Clean html
    text = text.replace("&lt;all&gt;", "")

    # Remove annoying punctuation, that's not relevant
    text = BAD_PUNCT_RE.sub("", text)

    # Get rid of long sequences of dashes - these are formating
    text = DASH_RE.sub(" ", text)

    # removing newlines, tabs, and extra spaces.
    text = WHITESPACE_RE.sub(" ", text)

    # If we ended up with "empty" sentences - get rid of them.
    text = EMPTY_SENT_RE.sub(".", text)

    # Attempt to create sentences from bullets
    text = replace_semicolon(text)

    # Fix weird period issues + start of text weirdness
    # text = re.sub('\.(?=[A-Z])', '  . ', text)
    # Get rid of anything thats not a word from the start of the text
    text = FIX_START_RE.sub("", text)
    # Sometimes periods get formatted weird, make sure there is a space between periods and start of sent
    text = FIX_PERIOD.sub(". \g<1>", text)

    # Fix quotes
    text = text.replace("``", '"')
    text = text.replace("''", '"')

    # Add special punct back in
    text = text.replace("SECTION-HEADER", "<SECTION-HEADER>")

    return text
