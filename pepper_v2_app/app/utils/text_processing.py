from .language import BASE_CURSE_PATTERNS, ONES, TENS, TEENS, SPANISH_MARKERS, ENGLISH_MARKERS

import re
import html

def detect_language(text: str) -> str:
    words = re.findall(r"\b[\wáéíóúüñ]+\b", text.lower())
    spanish_score = sum(word in SPANISH_MARKERS for word in words)
    english_score = sum(word in ENGLISH_MARKERS for word in words)
    if spanish_score > english_score:
        return "Spanish"
    return "English"

def find_filtered_term(text: str):
    for pattern in BASE_CURSE_PATTERNS:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return {
                "matched": True,
                "pattern": pattern,
                "term": match.group(0)
            }

    return {
        "matched": False,
        "pattern": None,
        "term": None
    }


def contains_filtered_term(text: str) -> bool:
    filter_pattern = re.compile("|".join(BASE_CURSE_PATTERNS), re.IGNORECASE)
    return filter_pattern.search(text) is not None

def censor_text(text: str) -> str:
    
    curse_regex = re.compile(
        r'\b(?:' + '|'.join(BASE_CURSE_PATTERNS) + r')\b',
        flags=re.IGNORECASE
    )
    
    return curse_regex.sub("*", text)

#%% Numbers to words

def two_digit_words(n: int) -> str:
    if n < 10:
        return ONES[n]

    if 10 <= n <= 19:
        return TEENS[n]

    tens = (n // 10) * 10
    ones = n % 10

    if ones == 0:
        return TENS[tens]

    return f"{TENS[tens]} {ONES[ones]}"


def number_to_words_for_tts(n: int) -> str:
    if not 0 <= n <= 9999:
        return str(n)

    if n < 100:
        return two_digit_words(n)

    if n < 1000:
        hundreds = n // 100
        remainder = n % 100

        if remainder == 0:
            return f"{ONES[hundreds]} hundred"

        return f"{ONES[hundreds]} hundred {two_digit_words(remainder)}"

    thousands = n // 1000
    remainder = n % 1000

    if remainder == 0:
        return f"{ONES[thousands]} thousand"

    return f"{ONES[thousands]} thousand {number_to_words_for_tts(remainder)}"


def year_to_words(year: int) -> str:
    if 1000 <= year <= 1999:
        first = year // 100
        last = year % 100

        if last == 0:
            return f"{two_digit_words(first)} hundred"

        if last < 10:
            return f"{two_digit_words(first)} oh {ONES[last]}"

        return f"{two_digit_words(first)} {two_digit_words(last)}"

    if 2000 <= year <= 2009:
        if year == 2000:
            return "two thousand"
        return f"two thousand {ONES[year % 10]}"

    if 2010 <= year <= 2099:
        return f"twenty {two_digit_words(year % 100)}"

    return number_to_words_for_tts(year)

def normalize_numbers_for_tts(text: str) -> str:
    pattern = re.compile(
        r"(?<![\w,])(?<!\d\.)(?:\d{1,3}(?:,\d{3})+|\d{1,4})(?![\w,]|\.\d)"
    )

    def repl(match):
        raw = match.group(0)
        has_comma = "," in raw
        cleaned = raw.replace(",", "")

        n = int(cleaned)

        if not 0 <= n <= 9999:
            return raw

        if has_comma:
            return number_to_words_for_tts(n)

        if 1000 <= n <= 2099:
            return year_to_words(n)

        return number_to_words_for_tts(n)

    return pattern.sub(repl, text)
#%% Remove Formatting
def remove_formatting(text: str) -> str:
    # HTML entities
    
    text = html.unescape(text)

    # fenced code blocks
    text = re.sub(r"```[\s\S]*?```", " ", text)

    # inline code
    text = re.sub(r"`([^`]*)`", r"\1", text)

    # markdown images: ![alt](url) -> alt
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)

    # markdown links: [label](url) -> label
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

    # bare URLs
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)

    # headings
    text = re.sub(r"^\s{0,3}#{1,6}\s*", "", text, flags=re.MULTILINE)

    # blockquotes
    text = re.sub(r"^\s{0,3}>\s?", "", text, flags=re.MULTILINE)

    # horizontal rules
    text = re.sub(r"^\s*([-*_]){3,}\s*$", " ", text, flags=re.MULTILINE)

    # unordered list markers
    text = re.sub(r"^\s*[-+*]\s+", "", text, flags=re.MULTILINE)

    # ordered list markers
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)

    # task list checkboxes
    text = re.sub(r"^\s*[-+*]?\s*\[(?: |x|X)\]\s*", "", text, flags=re.MULTILINE)

    # remove markdown emphasis markers
    text = re.sub(r"(\*\*\*|\*\*|\*|___|__|_|~~)", "", text)

    # remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)

    # remove LaTeX block math: $$...$$
    text = re.sub(r"\$\$[\s\S]*?\$\$", " ", text)

    # remove LaTeX inline math: $...$
    text = re.sub(r"(?<!\$)\$([^\$]+)\$(?!\$)", r"\1", text)

    # remove LaTeX inline delimiters \( ... \)
    text = re.sub(r"\\\((.*?)\\\)", r"\1", text)

    # remove LaTeX display delimiters \[ ... \]
    text = re.sub(r"\\\[(.*?)\\\]", r"\1", text, flags=re.DOTALL)
    
    # remove leftover backslash commands like \textbf, \mathrm, etc.
    text = re.sub(r"\\[a-zA-Z]+", " ", text)

    # make simple exponents more speakable: 2^3 -> 2 to the power of 3
    text = re.sub(r"(\w+)\s*\^\s*(\w+)", r"\1 to the power of \2", text)

    # remove curly braces often left from latex
    text = text.replace("{", " ").replace("}", " ")

    # remove standalone asterisks
    text = re.sub(r"\s*\*\s*", " ", text)

    # normalize spacing before punctuation
    text = re.sub(r"\s+([.,!?;:])", r"\1", text)

    # collapse whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)
    text = re.sub(r"\s{2,}", " ", text)

    # # convert common LaTeX commands to readable words
    # replacements = {
    #     r"\\times": " times ",
    #     r"\\cdot": " times ",
    #     r"\\div": " divided by ",
    #     r"\\frac": " fraction ",
    #     r"\\sqrt": " square root ",
    #     r"\\pi": " pi ",
    #     r"\\theta": " theta ",
    #     r"\\alpha": " alpha ",
    #     r"\\beta": " beta ",
    #     r"\\gamma": " gamma ",
    #     r"\\leq": " less than or equal to ",
    #     r"\\geq": " greater than or equal to ",
    #     r"\\neq": " not equal to ",
    #     r"\\approx": " approximately ",
    # }
    # for pattern, replacement in replacements.items():
    #     text = re.sub(pattern, replacement, text)

    return text.strip()