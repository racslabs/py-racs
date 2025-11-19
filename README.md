# py-racs

[![crates.io](https://img.shields.io/crates/v/racs.svg)](https://crates.io/crates/racs)

**py-racs** is the python client library for [RACS](https://github.com/racslabs/racs). 
It provides access to all the RACS commands through a low-level API.


## Installation

## Basic Operations

To open a connection, simply create a client using ``open``. 

```python
from racs import Racs

r = Racs(host="localhost", port=6381, pool_size=3)
```

### Streaming

The ``pipeline`` function is used to chain together multiple RACS commands and execute them sequentially.
In the below example, a new audio stream is created and opened. Then PCM data is chunked into frames 
and streamed to the RACS server.

```python
from racs import Racs

# Connect to the RACS server
r = Racs(host="localhost", port=6381, pool_size=3)

# Get pipeline
p = r.pipeline()

# Create a new audio stream and open it using pipeline
res = p.create(stream_id="chopin", sample_rate=44100, channels=2, bit_depth=16) \
       .open(stream_id="chopin") \
       .execute()

# Reset pipeline
p.reset()

# // Prepare list of PCM samples (interleaved L/R, 16- or 24-bit integers)
data = [...]

# // Stream PCM data to the server
r.stream(stream_id="chopin", chunk_size=1024 * 32, pcm_data=data)

# Close the stream when finished
p.close(stream_id="chopin") \
 .execute()
```

### Extracting and Formating
The below example retrieves a reference timestamp, and uses it to extract an audio segment based on the given range. 
It then converts the extracted PCM data into MP3 format and writes the resulting bytes to a file.

```python
from racs import Racs
from datetime import datetime, timezone,  timedelta

# Connect to the RACS server
r = Racs(host="localhost", port=6381, pool_size=3)

# Get pipeline
p = r.pipeline()

# Get the reference timestamp (in milliseconds)
ref = p.info(stream_id="chopin", attr="ref") \
       .execute()

# Convert milliseconds to datetime
frm = datetime.fromtimestamp(ref / 1000, tz=timezone.utc)
# Compute end time by adding one day
to = frm + timedelta(days=1)

# Extract PCM data between `frm` and `to`
# Convert (format) the audio to MP3
res = p.extract(stream_id="chopin", frm=frm, to=to) \
       .format(mime_type="audio/mp3", sample_rate=44100, channels=2, bit_depth=16) \
       .execute()

# Use or save the MP3 bytes
# e.g. write them to a file
with open("chopin.mp3", "wb") as f:
    f.write(res)
```

To extract PCM data without formating, do the following instead:

```python
res = p.extract(stream_id="chopin", frm=frm, to=to) \
       .execute()
```

### Querying Streams and Metadata

Stream ids stored in RACS can be queried using the ``list`` function.
``list`` takes a glob pattern and returns a list of streams ids matching the pattern.

```python
from racs import Racs

# Connect to the RACS server
r = Racs(host="localhost", port=6381, pool_size=3)

# Get pipeline
p = r.pipeline()

# Run list command matching "*" pattern
res = p.list(pattern="*").execute()

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
res = p.info(stream_id="chopin", attr="sample_rate").execute()

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




