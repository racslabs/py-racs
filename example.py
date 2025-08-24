from datetime import datetime

from racs import Racs

if __name__ == '__main__':
    import torchaudio


    waveform, sample_rate = torchaudio.load("chopin.wav")
    data = (waveform * 32768).clamp(min=-32768, max=32767).short().T.ravel().tolist()


    r = Racs("localhost", 8080)
    p = r.pipeline()

    res = p.create('chopin.wav', 44100, 2).execute_pipeline()
    print(res)
    p.reset()

    p.open('chopin.wav')
    res = p.execute_pipeline()
    print(res)
    p.reset()

    p.stream({
        'chunk_size': 16384,
        'sample_rate': 44100,
        'stream_id': 'chopin.wav',
        'channels': 2
    }, data)

    frm = datetime(2023, 12, 25, 17, 30, 45, 123000)
    to = datetime(2026, 5, 26, 22, 56, 16, 123000)

    d = p.extract('chopin.wav', frm, to).format('audio/ogg', 2, 44100).execute_pipeline()

    with open("chopin.ogg", "wb") as f:
        f.write(d)
