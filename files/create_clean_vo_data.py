#!/bin/env python

import json
import requests
from ruamel import yaml
import jsbeautifier

def get_data():
    vars = yaml.safe_load(open('../defaults/main.yml'))
    url = vars['lavoisier']['base_url'] + vars['lavoisier']['vo_id_card_endpoint']
    try:
        data = requests.get(url).json()
    except UserWarning as e:
        print e
    return data


def filter_data(data):
    """
    Filter the json from Lavoisier, by excluding VOs which do not have a VOMS server.
    This method takes the raw json from Lavoisier and loops over the entries in it,
    extracting the relevant information for the VO.
    The result is an object (data) with an array of dicts containing:
        VO name
        voms server hostname
        voms port
        VOMS Server cert DN
        CA DN of the issueing CA
        :param data=vo: the json object to parse
    """
    cleaned_data = {"data": []}
    for i, vo in enumerate(data['voVoms']):
        for k, vomses in enumerate(vo['Vo']):
            try:
                clean_vo = {
                    'name': None,
                    'voms': {
                        'DN': None,
                        'CA_DN': None,
                        'hostname': None,
                    }
                }
                clean_vo['name'] = vo['name']
                clean_vo['voms']['DN'] = vo['Vo'][k]['VoVomsServer'][0]['VoVomsServer'][2]['X509Cert'][0]['DN'][0]
                clean_vo['voms']['CA_DN'] = vo['Vo'][k]['VoVomsServer'][0]['VoVomsServer'][2]['X509Cert'][1]['CA_DN'][0]
                clean_vo['voms']['hostname'] = vo['Vo'][k]['VoVomsServer'][0]['VoVomsServer'][2]['host']
                clean_vo['voms']['port'] = vo['Vo'][k]['VoVomsServer'][0]['vomses_port']
                cleaned_data['data'].append(clean_vo)
            except IndexError:
                print "VO " + vo['name'] + " is bad"
    print str(i) + " vos configured"

    # write it to a file
    with open('data.yml', 'w') as file:
        yaml.dump(cleaned_data,file,Dumper=yaml.RoundTripDumper)
    return 0


if __name__ == "__main__":
    opts = jsbeautifier.default_options()
    opts.indent_size = 2
    opts.space_in_empty_paren = True
    data = get_data()
    filter_data(get_data())