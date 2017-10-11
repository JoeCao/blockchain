# coding=utf-8
import requests


def get_remote_chain(node):
    response = requests.get('http://{0}/chain'.format(node))
    if response.status_code == 200:
        yield response
    else:
        yield None
