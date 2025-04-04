#!/usr/bin/env python3

import os
import json
import argparse


def write_detector(params):
    detector = params.get('detector')

    # Extract wavelength directly from the JSON structure
    x = detector['wavelength']  # This is directly an array now

    # Iterate over plot data groups
    for groupkey, plot in detector['plots'].items():
        for serieskey, y in plot.items():
            writefile(params, groupkey, serieskey, x, y)


def writefile(params, groupkey, serieskey, x, y):
    prefix = params.get('prefix')
    detector = params.get('detector')
    output_dir = params.get('output_dir')
    ordername = params.get('ordername')
    sep = params.get('separator')
    labelsep = params.get('labelseparator')

    outputfilename = prefix + (sep + "order" + labelsep + ordername if ordername else "") \
                     + sep + "det" + labelsep + detector['name'] + sep + groupkey + sep + serieskey + ".ascii"

    outputfilepath = os.path.join(output_dir, outputfilename)

    with open(outputfilepath, 'w') as of:
        for xx, yy in zip(x, y):
            of.write(f"{xx} {yy}\n")
        if params.get('verbose'):
            print(outputfilepath)


def main():
    parser = argparse.ArgumentParser(
        description='Extract data from a given JSON file which is the output from an ETC execution.\n'
                    'Write the wavelength and data into columns in an ASCII file.\n'
                    'Output files names are prefixed with the input file name by default, but can be\nchanged with the -p option.',
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('inputfilename', help="Input JSON file, which is output from an ETC")
    parser.add_argument('-p', '--prefix', dest='prefix', help='output file name prefix to use instead of the default\nwhich is the input file name')
    parser.add_argument('-s', '--separator', dest='separator', default='_', help='separator string in the constructed output file name')
    parser.add_argument('-l', '--labelseparator', dest='labelseparator', default=':', help='separator string between labels (ordername/detectorname)\n' + 'and their values in the file names, e.g. "det-1" instead of default "det:1"')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='print the output file names')
    parser.add_argument('-d', '--directory', dest='directory', default=None, help='Directory for the output files')

    args = parser.parse_args()

    prefix = args.prefix if args.prefix else args.inputfilename
    output_dir = args.directory if args.directory else os.getcwd()

    with open(args.inputfilename) as f:
        data = json.load(f)
        if 'orders' in data['data'].keys():
            for order in data['data']['orders']:
                for detector in order['detectors']:
                    write_detector({
                        'prefix': prefix,
                        'ordername': order['order'],
                        'detector': detector,
                        'verbose': args.verbose,
                        'separator': args.separator,
                        'labelseparator': args.labelseparator,
                        'output_dir': output_dir
                    })
        else:
            for detector in data['data']['detectors']:
                write_detector({
                    'prefix': prefix,
                    'detector': detector,
                    'verbose': args.verbose,
                    'separator': args.separator,
                    'labelseparator': args.labelseparator,
                    'output_dir': output_dir
                })


if __name__ == '__main__':
    main()
