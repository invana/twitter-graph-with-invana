# Twitter usecase PlayGround

## Requirements
- python 3.7 (any 3x should work)
- invana graph explorer - start explorer server
- janusgraph - start janusgraph server 
- install requirements.txt

```shell script

export CONSUMER_KEY="xxxx"
export CONSUMER_SECRET="xxxx"
export ACCESS_TOKEN="xxxx"
export ACCESS_TOKEN_SECRET="xxxx"

python3 twitter_stream.py
```

## Gremlin Query

```shell 


// get last 10 vertices of TwitterProfile label
node= g.V().hasLabel("TwitterProfile").order().by("entry_created_at",decr).limit(10).toList(); 



node= g.V().order().by("entry_created_at",decr).limit(10).toList(); 
edges = g.V().order().by("entry_created_at",decr).limit(10).outE().dedup().toList(); 
other_nodes = g.V().order().by("entry_created_at",decr).limit(10).outE().otherV().dedup().toList();
[other_nodes,edges,node]
```

