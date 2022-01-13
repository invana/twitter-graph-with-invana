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

**NOTE:** Start an instance of [JanusGraph](https://github.com/JanusGraph/janusgraph-docker) before you start `read_stream.py`

## License

[MIT License](LICENSE)
