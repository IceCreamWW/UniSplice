import numpy as np

from g2p import IG2P, SoundChoiceG2P
from p2s import P2S


class UniSplice:
    """
    UniSplice implements the UniSplice Framework
    """

    def __init__(self, g2p: IG2P, p2s: P2S):
        """
        Args:
            g2p: Grapheme to Phoneme converter
            p2s: Phoneme to Speech converter
        """
        self.g2p = g2p
        self.p2s = p2s

    def text2speech(self, text: str) -> np.ndarray:
        phonemes = self.g2p(text)
        speech = self.p2s(phonemes)
        return speech

    def uttid2speech(self, uttid: str) -> np.ndarray:
        speech = self.p2s.uttid2speech(uttid)
        return speech


if __name__ == "__main__":
    g2p = SoundChoiceG2P()
    p2s = P2S()
    uni_splice = UniSplice(g2p, p2s)
