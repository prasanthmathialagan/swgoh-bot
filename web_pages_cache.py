import os.path
import syslog
import requests
import os


def get_from_cache(cache_dir, key, url, refresh=False):
    file = cache_dir + '/' + key
    if os.path.isfile(file):
        if refresh:
            syslog.syslog('Refreshing %s' % (url,))
            os.rename(file, file + ".bkp")
        else:
            syslog.syslog('Returning %s from cache' % (url,))
            return open(file, 'r').read()

    r = requests.get(url)
    html_doc = r.text
    f = open(file, 'w+')
    f.write(html_doc)
    f.close()

    return html_doc
