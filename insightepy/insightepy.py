# -*- coding: utf-8 -*-
import sys, traceback
from urllib3 import HTTPConnectionPool
import json
import resources as rs
import os
import codecs
import requests
import time
import tarfile


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
        r = self.pool.request(method, rs.route_prefix + url, fields=fields)
        try:
            return json.loads(r.data)
        except:
            return r.data

    def post_file(self, url, fields):
        urlfull = 'http://' + rs.HOST_ADDR + ':' + rs.HOST_PORT + rs.route_prefix + url
        r = requests.post(rs.route_prefix + urlfull, files=fields)
        try:
            return json.loads(r.content)
        except:
            return r.content

    def single_extract(self,
                       verbatim, lang,
                       ifterm=True, ifkeyword=True, ifconcept=True,
                       ifpos=True, ifemotion=True, ifsentiment=True, ifNER=True,
                       ifHashTags=True, ifMentions=True, ifUrl=True
                       ):

        # make request
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

    def _post_verbatim_file(self, filepath):
        # check if exist file
        if not os.path.exists(filepath):
            raise Exception("File not found : " + filepath)
        try:
            # post file
            _file = codecs.open(filepath, mode='rb', encoding='utf-8')
            filedata = {'file': (_file.name, open(filepath, 'rb'))}
            return self.post_file('/batch/extract', filedata)
        except:
            e = sys.exc_info()[0]
            print ("ERROR %s", e)
            traceback.print_exc(file=sys.stdout)
            raise Exception("Encoding Error : File was not found to be utf8 encoded")

    def batch_extract(self,
                      filepath, lang, dest_dir,
                      ifterm=True, ifkeyword=True, ifconcept=False,
                      ifpos=True, ifemotion=True, ifsentiment=True, ifNER=True,
                      ifHashTags=True, ifMentions=True, ifUrl=True
                      ):
        """
        Post verbatim file
        Make batch extraction request
        Wait for success
        """
        r = self._post_verbatim_file(filepath)
        if r['s'] and 'filename' in r:
            # make schedule request
            r1 = self.make_request('GET', '/batch/extract', {
                'action': 'schedule',
                'file': filepath,
                'filepath': r['filename'],
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
            if r1['s']:
                ifdone = False
                r2 = None
                while not ifdone:
                    r2 = self.make_request('GET', '/batch/extract', {
                        'action': 'check_if_done',
                        'file': filepath,
                        'filepath': r['filename'],
                    })
                    if r2['s']:
                        ifdone = True
                    else:
                        time.sleep(5)

                _dir_curr = os.getcwd() + '/'
                dir_new = r2['compressed_file'].replace('.tar', '') + '/'
                compressed_file = r2['compressed_file']

                if not os.path.exists(dest_dir):
                    os.mkdir(dest_dir)
                if not os.path.exists(dest_dir + dir_new):
                    os.mkdir(dest_dir + dir_new)

                # download compressed file
                tmp_compressed_file_path = self._get_resource('compressed_file', compressed_file, dest_dir)

                # move compressed file into new directory
                os.rename(tmp_compressed_file_path, dest_dir + dir_new + compressed_file)
                os.chdir(dest_dir + dir_new)

                # extract tar
                tar = tarfile.open(compressed_file)
                tar.extractall()

                # remove tar
                os.remove(compressed_file)
                os.chdir(_dir_curr)

                # build response
                return {'s': True, 'results_location': dest_dir + dir_new}
        else:
            return r

    def _get_resource(self, _type, name, dest_dir):
        url = '/resources/get/' + _type + '/' + name
        r = self.make_request('GET', url, {})
        with open(dest_dir + name, 'w') as new_file:
            new_file.write(r)
        new_file.close()

        # return filename
        return dest_dir + name
