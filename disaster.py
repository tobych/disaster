# Read disaster preparedness data from Google Docs spreadsheet
# and format ready for PDF/Word distribution
#
# Toby Champion and Tobias Eigen

import re, urllib, urllib2
from flask import Flask
import jinja
import getpass
import csv

# API access avoiding gdata dependency is from
# http://stackoverflow.com/a/9006155/76452

class Spreadsheet(object):
    def __init__(self, key):
        super(Spreadsheet, self).__init__()
        self.key = key

class Client(object):
    def __init__(self, email, password):
        super(Client, self).__init__()
        self.email = email
        self.password = password

    def _get_auth_token(self, email, password, source, service):
        url = "https://www.google.com/accounts/ClientLogin"
        params = {
            "Email": email, "Passwd": password,
            "service": service,
            "accountType": "HOSTED_OR_GOOGLE",
            "source": source
        }
        req = urllib2.Request(url, urllib.urlencode(params))
        return re.findall(r"Auth=(.*)", urllib2.urlopen(req).read())[0]

    def get_auth_token(self):
        source = type(self).__name__
        return self._get_auth_token(self.email, self.password, source, service="wise")

    def download(self, spreadsheet, gid=0, format="csv"):
        url_format = "https://spreadsheets.google.com/feeds/download/spreadsheets/Export?key=%s&exportFormat=%s&gid=%i"
        headers = {
            "Authorization": "GoogleLogin auth=" + self.get_auth_token(),
            "GData-Version": "3.0"
        }
        req = urllib2.Request(url_format % (spreadsheet.key, format, gid), headers=headers)
        return urllib2.urlopen(req)

# Now for the templating (jinja2) and HTTP server (flask)

def get_rows():
    csv_file = gs.download(ss)
    rows = csv.DictReader(csv_file)
    # TODO: deal better with missing data
    # TODO: sort here by last name
    # TODO: group by north/center/south
    # return [row for row in rows if row['Disaster Response Team'] == 'CENTER']
    return rows

def nl2br(value): 
    # Doesn't work yet (I'm new to jinja2)
    return value.replace('\n', '<br>\n')

def template():
    # TODO: Use proper integration of flask and jinja2
    env = jinja.Environment()
    env.loader = jinja.FileSystemLoader(".")
    # TODO: deal with line breaks better
    # env.filters['nl2br'] = nl2br
    return env.get_template("disaster.html")


if __name__ == "__main__":
    email = ''  # YOURS
    password = ''  # YOURS
    spreadsheet_id = ''  # YOURS

    # Create client and spreadsheet objects
    gs = Client(email, password)
    ss = Spreadsheet(spreadsheet_id)

    # Set this to False to write to stdout instead
    SERVE = True
    if SERVE:
        app = Flask(__name__)
        @app.route('/')
        def hello_world():
            return template().render(rows=get_rows())
        app.run(host='0.0.0.0')
    else:
        print template().render(rows=get_rows())
