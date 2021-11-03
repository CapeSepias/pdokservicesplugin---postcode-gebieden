#!/usr/bin/env python3
import json
import argparse


def is_popular(service):
    if service['type'].lower() == 'wmts':
        return True
    return False


def main(input_fn, output_fn, max_count=0):
    with open(input_fn, 'r') as input_file:
        input_dict = json.load(input_file)

    popular_services = []
    other_services = []

    service_cnt = 0
    for service in input_dict['services']:
        service_cnt += 1
        if max_count != 0 and service_cnt > max_count:
            break
        if is_popular(service):
            popular_services.append(service)
        else:
            other_services.append(service)

    print(f'pop: {len(popular_services)} | other: {len(other_services)}')

    output_dict = {'services': popular_services + other_services}

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
