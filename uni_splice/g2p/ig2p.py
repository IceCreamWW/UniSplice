class IG2P:
    """
    The G2P interface

    """
    def __call__(self, text, **kwargs):
        """
        Arguments
        ---------
        text: str
            Raw character string
        """
        raise NotImplementedError

