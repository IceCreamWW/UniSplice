import re
from typing import Union
from pathlib import Path
import numpy as np
import torch
import soundfile as sf
import kaldiio

def load_audio(path: Union[Path, str])->np.ndarray:
    path = Path(path)
    if re.match(r".*\.ark:\d+", path): # kaldi ark style audio path
        sample_rate, wav = kaldiio.load_mat(path)
    else:
        wav, sample_rate = sf.read(path)
    return wav

