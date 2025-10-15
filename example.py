from datetime import datetime

import torchaudio
import torch
import soundfile

from racs.client import Racs

if __name__ == '__main__':

    # waveform, sample_rate = torchaudio.load("chopin.wav")
    #
    # data = (waveform * 32767) \
    #     .round() \
    #     .clamp(min=-32768, max=32767) \
    #     .int().T.ravel().tolist()
    #
    r = Racs("10.0.0.75", 6381)
    p = r.pipeline()

    # print(p.info('chopin', 'bit_depth').execute())

    # res = p.create('chopin', 44100, 2, 16).execute()
    # print(res)
    # p.reset()
    #
    # p.open('chopin')
    # res = p.execute()
    # print(res)
    # p.reset()
    #
    # p.stream({
    #     'chunk_size': 1024 * 31,
    #     'sample_rate': 44100,
    #     'bit_depth': 16,
    #     'stream_id': 'chopin',
    #     'channels': 2
    # }, data)
    #
    # frm = datetime(2023, 12, 25, 17, 30, 45, 123000)
    # to = datetime(2026, 5, 26, 22, 56, 16, 123000)
    #
    # d = p.extract('chopin', frm, to).format('audio/wav', 44100, 2, 16).execute()
    #
    # print(len(d))
    d = p.eval("(let ((x 2) (y 4)) (* x y))").execute()
    print(d)
    # with open("c.wav", "wb") as f:
    #     f.write(d)


# EXTRACT 'chopin.wav' 2023-12-25T22:30:45.123Z 2026-05-27T02:56:16.123Z |> FORMAT 'audio/mp3' 8000 2 24