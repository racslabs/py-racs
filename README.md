# py-racs

![PyPI - Version](https://img.shields.io/pypi/v/:packageName)


**py-racs** is the python client library for [RACS](https://github.com/racslabs/racs). 
It provides access to all the RACS commands through a low-level API.


## Installation

PyPi account is not yet setup. For now, installation can be done by cloning the repo and running the following in project root:
```commandline
pip install <path to project root>
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

# Create a new audio stream and open it using pipeline
res = p.create(stream_id="Beethoven Piano Sonata No.1", sample_rate=44100, channels=2, bit_depth=16) \
       .open(stream_id="Beethoven Piano Sonata No.1") \
       .execute()

# Reset pipeline
p.reset()

# // Prepare list of PCM samples (interleaved L/R, 16- or 24-bit integers)
data = [...]

# // Stream PCM data to the server
r.stream(stream_id="Beethoven Piano Sonata No.1", chunk_size=1024 * 32, pcm_data=data)

# Close the stream when finished
p.close(stream_id="Beethoven Piano Sonata No.1") \
 .execute()
```

### Extracting and Formating
The below example extracts a 30-second audio segment. It then converts the extracted PCM data into MP3 format and writes the resulting bytes to a file.

```python
from racs import Racs
from datetime import datetime, timezone,  timedelta

# Connect to the RACS server
r = Racs(host="localhost", port=6381)

# Get pipeline
p = r.pipeline()

# Extract PCM data
# Convert (format) the audio to MP3
res = p.extract(stream_id="Beethoven Piano Sonata No.1", start=0.0, duration=30.0) \
       .format(mime_type="audio/mp3", sample_rate=44100, channels=2, bit_depth=16) \
       .execute()

# Use or save the MP3 bytes
# e.g. write them to a file
with open("beethoven.mp3", "wb") as f:
    f.write(res)
```

To extract PCM data without formating, do the following instead:

```python
res = p.extract(stream_id="Beethoven Piano Sonata No.1", start=0.0, duration=30.0) \
       .execute()
```

### Querying Streams and Metadata

Stream ids stored in RACS can be queried using the ``search`` function.
``search`` takes a glob pattern and returns a list of streams ids matching the pattern.

```python
from racs import Racs

# Connect to the RACS server
r = Racs(host="localhost", port=6381, pool_size=3)

# Get pipeline
p = r.pipeline()

# Run list command matching "*" pattern
res = p.search(pattern="*").execute()

# ['Beethoven Piano Sonata No.1']
print(res)
```

Stream metadata can be queried using the ``info`` function. 
``info`` takes the stream id and metadata attribute as parameters.

```python
from racs import Racs

# Connect to the RACS server
r = Racs(host="localhost", port=6381, pool_size=3)

# Get pipeline
p = r.pipeline()

# Get sample rate attribute for stream
res = p.info(stream_id="Beethoven Piano Sonata No.1", attr="sample_rate").execute()

# Print the sample rate
print(res) # 44100
```

The supported attributes are:

| Attribute       | Description                                |
|-----------------|--------------------------------------------|
| `channels`      | Channel count of the audio stream.         |
| `sample_rate`   | Sample rate of the audio stream (Hz).      |
| `bit_depth`     | Bit depth of the audio stream.             |
| `ref`           | Reference timestamp (milliseconds UTC).    |
| `size`          | Size of audio stream in bytes.             |

### Raw Command Execution

To execute raw command strings, use the ``execute_command`` function.

```python
from racs import Racs

r = Racs(host="localhost", port=6381, pool_size=3)

res = r.execute_command("EVAL '(+ 1 2 3)'")
```

Refer to the documentation in [RACS](https://github.com/racslabs/racs) for the commands.




