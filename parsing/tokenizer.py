import nltk


class Tokenizer:
    """
    Custom tokenizer for EurLex files.
    """
    def __init__(self, filter_stopwords: bool = True, check_is_alpha: bool = True, to_lower: bool = True):
        """
        Instantiate a Tokenizer.

        Args:
            filter_stopwords: Discard english stopwords.
            check_is_alpha: Keep only alphabetic tokens (no punct, no numbers).
            to_lower: Convert text to lower before tokenization.
        """
        self.check_is_alpha = check_is_alpha
        self.filter_stopwords = filter_stopwords
        self.to_lower = to_lower

        self.stopwords = nltk.corpus.stopwords.words('english')

    def __call__(self, raw_text: str):
        """
        Split given text into tokens.

        Args:
            raw_text: Raw text to be tokenized.

        Returns tokens: List[str]
        """
        if self.to_lower:
            raw_text = raw_text.lower()
        tokens = nltk.word_tokenize(raw_text)
        tokens[:] = [t for t in tokens if self._is_valid(t)]
        return tokens

    def _is_valid(self, token: str):
        """
        Check whether the token is valid for current Tokenizer.

        Args:
            token: Current word (token) to be evaluated.

        Returns valid: bool
        """
        valid = True
        if self.check_is_alpha and not token.isalpha():
            valid = False
        if self.filter_stopwords and token in self.stopwords:
            valid = False
        return valid
