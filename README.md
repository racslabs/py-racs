# py-racs

[![PyPI - Version](https://img.shields.io/pypi/v/racs)](https://pypi.org/project/racs/)

**py-racs** is the python client library for [RACS](https://github.com/racslabs/racs).

## Installation

To install py-racs run:

```bash
pip install racs
```

## Basic Operations

To open a connection, simply create a new ``Racs`` instance and provide the host and port.

```python
from racs import Racs

r = Racs(host="localhost", port=6381)
```

### Streaming

The ``pipeline`` function is used to chain together multiple RACS commands and execute them sequentially.
In the below example, a new audio stream is created and opened. Then PCM data is chunked into frames 
and streamed to the RACS server.

```python
from racs import Racs

# Connect to the RACS server
r = Racs(host="localhost", port=6381)

# Get pipeline
p = r.pipeline()

# Create a new audio stream using pipeline
p.create(stream_id="vocals", sample_rate=44100, channels=2, bit_depth=16).execute() 

# Reset pipeline
p.reset()

# // Prepare list of PCM samples (interleaved L/R, 16- or 24-bit integers)
data = [...]

# // Stream PCM data to the server
r.stream("vocals") \
    .chunk_size(1024 * 32) \ 
    .batch_size(50) \
    .compression(True) \
    .compression_level(8) \
    .execute(data)
```
If `chunk_size`, `batch_size`, `compression` and `compression_level` are not provided, the default values will be used.

```python
# // Stream PCM data to the server
r.stream("vocals").execute(data)
```

Stream ids stored in RACS can be queried using the ``list`` command. ``list`` takes a glob pattern and returns a list of streams ids matching the pattern.

```python
from racs import Racs

# Connect to the RACS server
r = Racs(host="localhost", port=6381)

# Get pipeline
p = r.pipeline()

# Run list command matching "*" pattern
res = p.list(pattern="*").execute()

# ['vocals']
print(res)
```

### Extracting Audio
The below example extracts a 30-second PCM audio segment using the ``range`` command. It then encodes the data to MP3 and writes the resulting bytes to a file.

```python
from racs import Racs

# Connect to the RACS server
r = Racs(host="localhost", port=6381)

# Get pipeline
p = r.pipeline()

# Extract PCM data
# Encode the audio to MP3
res = p.range(stream_id="vocals", start=0.0, duration=30.0) \
       .encode(mime_type="audio/mp3") \
       .execute()

# Write to a file
with open("vocals.mp3", "wb") as f:
    f.write(res)
```

### Metadata

Stream metadata can be retrieved using the ``meta`` command. ``meta`` takes the stream id and metadata attribute as parameters.

```python
from racs import Racs

# Connect to the RACS server
r = Racs(host="localhost", port=6381)

# Get pipeline
p = r.pipeline()

# Get sample rate attribute for stream
res = p.meta(stream_id="vocals", attr="sample_rate").execute()

# Print the sample rate
print(res) # 44100
```

The supported metadata attributes are:

| Attribute     | Description                                     |
|---------------|-------------------------------------------------|
| `channels`    | Channel count of the audio stream.              |
| `sample_rate` | Sample rate of the audio stream (Hz).           |
| `bit_depth`   | Bit depth of the audio stream.                  |
| `ref`         | Reference timestamp (milliseconds UTC).         |
| `size`        | Size of the uncompressed audio stream in bytes. |

### Raw Command Execution

To execute raw command strings, use the ``execute_command`` function.

```python
from racs import Racs

r = Racs(host="localhost", port=6381)

res = r.execute_command("EVAL '(+ 1 2 3)'")
```

Refer to the documentation in [RACS](https://github.com/racslabs/racs) for the commands.




