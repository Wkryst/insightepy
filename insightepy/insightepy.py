# -*- coding: utf-8 -*-
import sys, traceback
from urllib3 import HTTPConnectionPool
import json
import resources as rs


class API(object):
    def __init__(self, clientid, clientsecret, authtoken):
        self._cid = clientid
        self._csecret = clientsecret
        self._authtoken = authtoken
        self.pool = HTTPConnectionPool(rs.HOST_ADDR + ':' + rs.HOST_PORT)

    def make_request(self, method, url, fields):
        # adding user information to field

        fields['cid'] = self._cid
        fields['csecret'] = self._csecret
        fields['authtoken'] = self._authtoken
        r = self.pool.request(method, url, fields=fields)
        try:
            return json.loads(r.data)
        except:
            return r.data

    def single_extract(self,
                       verbatim, lang,
                       ifterm=True, ifkeyword=True, ifconcept=True,
                       ifpos=True, ifemotion=True, ifsentiment=True, ifNER=True,
                       ifHashTags=True, ifMentions=True, ifUrl=True
                       ):

        # make request to REST_API
        r = self.make_request('GET', '/extract', {
            'verbatim': verbatim,
            'lang': lang,
            'ifterm': ifterm,
            'ifkeyword': ifkeyword,
            'ifconcept': ifconcept,
            'ifpos': ifpos,
            'ifemotion': ifemotion,
            'ifsentiment': ifsentiment,
            'ifner': ifNER,
            'ifhashtags': ifHashTags,
            'ifmention': ifMentions,
            'ifurl': ifUrl,
        })
        return r

    def batch_extract(self,
                      filepath,
                      ifterm=True, ifkeyword=True, ifconcept=False,
                      ifpos=True, ifemotion=True, ifsentiment=True, ifNER=True,
                      ifHashTags=True, ifMentions=True, ifUrl=True
                      ):
        pass
