#!/usr/bin/env python3
import json
import argparse
import re

sorting_rules = {
    0: {'names': ['opentopo+'], 'types': ['wmts']},
    10: {'names': ['^actueel_orthohr$'], 'types': ['wmts']},
    11: {'names': ['^actueel_ortho25$'], 'types': ['wmts']},
    12: {'names': ['^actueel_ortho25ir$'], 'types': ['wmts']},
    13: {'names': ['lufolabels'], 'types': ['wmts']},
    #15: {'names': ['^\d{4}_ortho'], 'types': ['wmts']},
    #16: {'names': ['^\d{4}_ortho+IR'], 'types': ['wmts']},
    20: {'names': ['landgebied', 'provinciegebied', 'gemeentegebied'], 'types': ['wfs']},
    30: {'names': ['top+'], 'types': ['wmts']},
    32: {'names': ['^standaard$', '^grijs$', '^pastel$', '^water$'], 'types': ['wmts']}, # BRT-lagen
    34: {'names': ['bgtstandaardv2', 'bgtachtergrond'], 'types': ['wmts']},
    60: {'names': ['ahn3+'], 'types': ['wmts']},
    #90: {'names': ['aan+'], 'types': ['wmts']},
}


def get_sorting_value(layer_info):
    if not 'name' in layer_info:
        return 101
    layer_name = layer_info['name'].lower()
    for key, sorting_rule in sorting_rules.items():
        if layer_info['type'].lower() in sorting_rule['types']:
            for name in sorting_rule['names']:
                if re.search(name, layer_name) is not None:
                    return key
    if layer_info['type'].lower() == 'wmts':
        return 99 # other wmts layers
    else:
        return 100 # all other layers


def is_popular(service):
    if service['type'].lower() == 'wmts':
        return True
    return False


def main(input_fn, output_fn, max_count=0):
    with open(input_fn, 'r') as input_file:
        input_dict = json.load(input_file)

    sorted_layer_dict = {}

    service_cnt = 0
    for service in input_dict['services']:
        service_cnt += 1
        if max_count != 0 and service_cnt > max_count:
            break
        sorting_value = get_sorting_value(service)

        if sorting_value in sorted_layer_dict:
            sorted_layer_dict[sorting_value].append(service)
        else:
            sorted_layer_dict[sorting_value] = [service]

    output_dict = {'services': []}
    for key in sorted(sorted_layer_dict.keys()):
        if len(sorted_layer_dict[key]) == 0:
            print(f'No layers found for sorting rule: {sorting_rules[key]}')
        output_dict['services'] += sorted_layer_dict[key]

    '''
    # Screen output for debugging
    print('\nOUTPUT:')
    for output_layer in output_dict['services'][:50]:
            print(f'{output_layer["name"]} [{output_layer["type"]}]')
    '''

    with open(output_fn, 'w') as output_file:
        json.dump(output_dict, output_file, indent=2, separators=(',', ':'))

    print(service_cnt - 1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sort services for usage in PDOK plugin GUI")
    parser.add_argument(
        "input_file", metavar="input-file", type=str, help="JSON input file"
    )
    parser.add_argument(
        "output_file", metavar="output-file", type=str, help="JSON output file"
    )
    parser.add_argument(
        "-n",
        "--number",
        action="store",
        type=int,
        default=0,
        help="nr of services to process",
    )
    args = parser.parse_args()

    main(args.input_file, args.output_file, max_count=args.number)
