import os.path
import syslog
import requests

def get_from_cache(cache_dir, key, url):
    file = cache_dir + '/' + key
    if os.path.isfile(file):
        syslog.syslog('Returning %s from cache' % (url,))
        return open(file, 'r').read()

    r = requests.get(url)
    html_doc = r.text
    f = open(file, 'w+')
    f.write(html_doc)
    f.close()

    return html_doc