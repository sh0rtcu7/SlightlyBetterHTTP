import os
from flask import Flask, abort, json, send_file
import argparse
import base64
import logging

class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(levelname)s - %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

BASE_PATH = None
LINPEAS_PATH = None

logger = logging.getLogger("Catcher")
logger.setLevel(logging.DEBUG)

consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.DEBUG)
consoleHandler.setFormatter(CustomFormatter())

logger.addHandler(consoleHandler)

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--address', type=str, help='IP to listen on')
parser.add_argument('-p', '--port', type=int, help="Port to listen on")
parser.add_argument('-d', '--dir', type=str, help='Directory to host on root path')

args = parser.parse_args()

if args.address == None:
    args.address = '0.0.0.0'

if args.port == None:
    args.port = 80

if args.dir == None:
    BASE_PATH = os.getcwd()
else:
    BASE_PATH = args.dir

api = Flask(__name__)

@api.route('/', defaults={'req_path': ''})
@api.route('/<path:req_path>')
def dir_listing(req_path):

    # Joining the base and the requested path
    abs_path = os.path.join(BASE_PATH, req_path)

    # Return 404 if path doesn't exist
    if not os.path.exists(abs_path):
        return abort(404)

    # Check if path is a file and serve
    if os.path.isfile(abs_path):
        return send_file(abs_path)
    

@api.route('/base64/<encoded>')
def decode_base64(encoded):
    try:
        logger.info(base64.b64decode(encoded).decode('utf-8'))
    except Exception:
        logger.error('Failed to parse Base64')

    return json.dumps({})

@api.route('/linpeas.sh')
def linpeas():
    if not os.path.exists(LINPEAS_PATH):
        return abort(404)
    return send_file(LINPEAS_PATH)


if __name__ == '__main__':
    api.run(args.address, args.port)