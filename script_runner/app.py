#!/usr/bin/env python

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
from flask import Flask, request, render_template, Markup, has_request_context, make_response
import markdown
import os.path
import logging
from flask.logging import default_handler
from logging.handlers import RotatingFileHandler
import datetime
import subprocess



# -----------------------------------------------------------------------------
# Variables
# -----------------------------------------------------------------------------
static_dir_name = 'static'
app = Flask(__name__, static_folder=static_dir_name, static_url_path='')
app_name = 'script_runner'
logging_dir = '/var/log/'
app_path = os.path.dirname(os.path.realpath(__file__))
templates_folder = os.path.join(app_path, 'templates')
index_md = os.path.join(templates_folder, 'index.md')
support_script_types = ['.sh']
script_dir_name = 'scripts'
log_dir_name = 'logs'
script_dir = os.path.join(app_name, script_dir_name)
static_dir = os.path.join(app_name, static_dir_name)
log_dir = os.path.join(app_name, log_dir_name)



# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.ip = request.remote_addr
            record.method = request.method
        else:
            record.url = None
            record.remote_addr = None

        return super().format(record)

class ContextualFilter(logging.Filter):
    def filter(self, log_record):
        # Provide some extra variables to give our logs some better info 
        log_record.utcnow = (
            datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S,%f %Z')
        )
        log_record.url = request.path
        log_record.method = request.method
        # Try to get the IP address of the user through reverse proxy
        log_record.ip = request.environ.get(
                            'HTTP_X_REAL_IP', 
                            request.remote_addr
        )
        return True

log_format = (
    "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s %(ip)s %(method)s %(url)s %(message)s"
)

formatter = RequestFormatter(log_format)

log_file = logging_dir + app_name + '/' + app_name + '.log'

handler = RotatingFileHandler(log_file, maxBytes=10000, backupCount=5)
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)

app.logger.setLevel(logging.DEBUG)
app.logger.addHandler(handler)



# -----------------------------------------------------------------------------
# Methods
# -----------------------------------------------------------------------------
@app.route("/")
def index():
    with open(index_md, 'r') as f:
        content = f.read()
    content = Markup(markdown.markdown(content))
    #app.logger.info(str(200))
    resp = make_response(content)
    return returnify(resp)



@app.route("/run", methods=['GET'])
def run():
    if not request.args:
        error_code = 401
        error_message = 'Provide script name as a parameter to run it /run?script=scriptname.ext'
        log_message = 'No parameters'
        resp = make_response(error_message, error_code)

        return returnify(resp, log_message)

    else: # there are parameters
        args = request.args
        if not args['script']: # no 'script' parameter
            error_code = 401
            error_message = 'Provide script name as a parameter to run it /run?script=scriptname.ext'
            log_message = 'No parameters'
            resp = make_response(error_message, error_code)

            return returnify(resp, log_message)

        else:
            resp, message = run_script(args['script'])
            return returnify(resp, message)



@app.route("/read", methods=['GET'])
def read():
    if not request.args:
        error_code = 401
        error_message = 'Provide log file name as a parameter to run it /read?file=filename'
        log_message = 'No parameters'
        resp = make_response(error_message, error_code)

        return returnify(resp, log_message)

    else: # there are parameters
        args = request.args
        if not args['file']: # no 'file' parameter
            error_code = 401
            error_message = 'Provide log file name as a parameter to run it /read?file=filename'
            log_message = 'No parameters'
            resp = make_response(error_message, error_code)

            return returnify(resp, log_message)

        else:
            resp, message = read_file(args['file'])
            return returnify(resp, message)



# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def returnify(response, message=''):
    resp = response

    if not message == '':
        message = ' ' + message
    
    app.logger.info(str(resp.status_code) + message)

    return resp



def run_script(script_name):
    script = os.path.join(script_dir, script_name)
    
    # make sure script is legit
    if not os.path.isfile(script): # script is not found
        error_code = 402
        error_message = 'Script name provided is invalid'
        log_message = 'Invalid script name'
        return make_response(error_message, error_code), log_message
    
    # make sure file extension is for supported script type
    file_name, file_ext = os.path.splitext(script)
    if file_ext == '.sh':
        log_path = os.path.join(log_dir, script_name + '.log')
        command_string = 'bash ' + script + ' >> ' + log_path
        subprocess.call(command_string, shell=True)
        message = 'Script running: ' + script
        return make_response(message), message
    else:
        error_code = 403
        error_message = 'Unsupported script type'
        log_message = 'Unsupported script ' + script
        return make_response(error_message, error_code), log_message



def read_file(file_name):
    file_path = os.path.join(log_dir, file_name)

    # make sure script is legit
    if not os.path.isfile(file_path): # file is not found
        error_code = 402
        error_message = 'File name provided is invalid'
        log_message = 'Invalid file name'
        return make_response(error_message, error_code), log_message
    
    # make sure file extension is for supported script type
    content = ''
    with open(file_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            print(line)
            content = content + line + '<br/>'

        log_message = 'Reading file ' + file_path
        return make_response(content), log_message



# -----------------------------------------------------------------------------
# runner
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    #app.run(host='0.0.0.0', port=80)
    app.run()