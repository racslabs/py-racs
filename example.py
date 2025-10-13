from datetime import datetime
from racs import Racs
import torchaudio
import torch

if __name__ == '__main__':

    waveform, sample_rate = torchaudio.load("chopin.wav")

    data = (waveform * 8388607) \
        .round() \
        .clamp(min=-8388608, max=8388607) \
        .int().T.ravel().tolist()
    #
    r = Racs("10.0.0.65", 6381)
    p = r.pipeline()

    # print(p.info('chopin.wav', 'ref').execute())

    # res = p.create('chopin', 44100, 2, 24).execute()
    # print(res)
    # p.reset()
    #
    # p.open('chopin')
    # res = p.execute()
    # print(res)
    # p.reset()
    #
    # p.stream({
    #     'chunk_size': 1024,
    #     'sample_rate': 44100,
    #     'bit_depth': 24,
    #     'stream_id': 'chopin',
    #     'channels': 2
    # }, data)

    frm = datetime(2023, 12, 25, 17, 30, 45, 123000)
    to = datetime(2026, 5, 26, 22, 56, 16, 123000)

    d = p.extract('chopin', frm, to).format('audio/mp3', 44100, 2, 24).execute()


    # d = p.eval("(ls \"*\")").execute()
    # print(d)
    with open("c.mp3", "wb") as f:
        f.write(d)


# EXTRACT 'chopin.wav' 2023-12-25T22:30:45.123Z 2026-05-27T02:56:16.123Z |> FORMAT 'audio/mp3' 8000 2 24