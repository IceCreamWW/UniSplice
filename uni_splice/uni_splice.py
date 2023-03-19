import numpy as np

from g2p import AbsG2P
from p2s import P2S


class UniSplice:
    """
    UniSplice implements the UniSplice Framework
    """

    def __init__(self, g2p: BaseG2P, p2s: BaseP2S):
        """
        Args:
            g2p: Grapheme to Phoneme converter
            p2s: Phoneme to Speech converter
        """
        self.g2p = g2p
        self.p2s = p2s

    def text2speech(self, text: str) -> np.ndarray:
        phonemes = self.g2p.text2phonemes(text)
        speech = self.p2s.phonemes2speech(phonemes)
        return speech


if __name__ == "__main__":
    g2p = AbsG2P()
    p2s = AbsP2S()
    uni_splice = UniSplice(g2p, p2s)
