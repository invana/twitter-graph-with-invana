"""

"""


def convert_dict_to_vertex(data, label, id_field):
    """
    data: dict object
    id_field:

    """
    entity_object = {'label': label, 'type': 'g:Vertex', 'properties': {}}
    for k, v in data.items():
        print("=====++", k, type(v), v )
        if k == id_field:
            if v:
                entity_object['id'] = v
            else:
                raise Exception("property key id_field doesn't have value in the data")
            if v == "id":
                entity_object["properties"][k] = v
        elif type(v) is list:
            pass
            print("===== this is list")
        else:
            entity_object["properties"][k] = v
    return entity_object


def convert_dict_to_edge(data, label, inv_id, inv_label, outv_id, outv_label):
    pass
