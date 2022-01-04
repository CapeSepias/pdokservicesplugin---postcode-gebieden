import json

import time




class LayerRegistry():

    def __init__(self):
        self.layers = []


    def __str__(self):
        return f'LayerRegistry[len: {len(self.layers)}]'


    def load_layer_json(self, fn):
        with open(fn, 'r', encoding='utf-8') as in_file:
            layers_dict = json.load(in_file)
            self.layers = layers_dict['services']


    def query(self, q, max_results=100):
        text_strings = []
        type_strings = []
        for part in q.split():
            if part.lower() in ['wms', 'wfs', 'wmts', 'wcs']:
                type_strings.append(part.lower())
            else:
                if len(part) > 1:
                    text_strings.append(part)
        #print(text_strings)
        #print(type_strings)

        if len(text_strings) == 0:
            return self.layers

        result = []
        for layer in self.layers:
            score = 0
            #print(layer)

            search_configs = [
                {'key': 'name', 'multiplier': 1.5},
                {'key': 'title', 'multiplier': 3},
                {'key': 'servicetitle', 'multiplier': 2},
                {'key': 'abstract', 'multiplier': 1},
            ]

            for search_config in search_configs:
                source = layer.get(search_config['key'])
                #print(source)
                if source is not None:
                    score += self.find_strings(text_strings, source) * search_config['multiplier']

            if len(type_strings) > 0:
                if layer.get('type', '') not in type_strings:
                    continue

            if score > 5:
                layer['score'] = score
                result.append(layer)
                result.sort(key=lambda item: -item.get("score"))
        return result[:max_results]


    def find_strings(self, text_strings, source):
        score = 0
        for text in text_strings:
            if text in source:
                score += 1
        return score


def print_layer(layer):
    result = ''
    name = layer.get('name', '')
    title = layer.get('title', '')
    service_type = layer.get('type')
    score = layer.get('score')
    print(f'{title}, {service_type} ({score})')


if __name__ == '__main__':
    lreg = LayerRegistry()
    #lreg.load_layer_json('pdok_short.json')
    lreg.load_layer_json('pdok.json')
    print(lreg)

    t0 = time.time()
    #result = lreg.query('wmts wcs top10 10nl wfs wms')
    result = lreg.query('')
    print('\n')
    print(len(result))
    #print(result)
    for layer in result:
        print_layer(layer)
    print(time.time() - t0)
