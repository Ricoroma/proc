# -*- coding: utf-8 -*-
import requests


def get_course():
    r = requests.get(f'https://garantex.org/api/v2/depth?market=btcrub')
    return float(r.json()['asks'][0]['price'])
