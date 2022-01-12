# Invana Twitter

Reference implementation to build twitter graph with Invana.

## Usage

```bash
pip install -r requirements.txt

# set twitter credentials 
export CONSUMER_KEY="xxxx"
export CONSUMER_SECRET="xxxx"
export ACCESS_TOKEN="xxxx"
export ACCESS_TOKEN_SECRET="xxxx"

# read stream
python3 read_stream.py
```

## Start a gremlin support graph db

Start an instance of [JanusGraph](https://github.com/JanusGraph/janusgraph-docker/tree/master/0.6)

## License

[MIT License](LICENSE)