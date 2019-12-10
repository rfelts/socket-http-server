#!/usr/bin/env python3

# Russell Felts
# Assignment 3 Socket HTTP Server


import mimetypes
import os
import socket
import sys
import traceback

from pathlib import Path


def response_ok(body=b"This is a minimal response", mimetype=b"text/plain"):
    """
    returns a basic HTTP response
    Ex:
        response_ok(
            b"<html><h1>Welcome:</h1></html>",
            b"text/html"
        ) ->

        b'''
        HTTP/1.1 200 OK\r\n
        Content-Type: text/html\r\n
        \r\n
        <html><h1>Welcome:</h1></html>\r\n
        '''
    """

    return b"".join([
        b"HTTP/1.1 200 OK\r\n",
        b"Content-Type:" + mimetype + b"\r\n",
        b"\r\n",
        body
    ])


def response_method_not_allowed():
    """Returns a 405 Method Not Allowed response"""

    return b"".join([
        b"HTTP/1.1 405 Method Not Allowed\r\n",
        b"Allow: GET\r\n",
        b"\r\n"
        b"Ony GET requests are allowed"
    ])


def response_not_found():
    """Returns a 404 Not Found response"""

    return b"".join([
        b"HTTP/1.1 404 Not Found\r\n"
    ])


def parse_request(request):
    """
    Given the content of an HTTP request, returns the path of that request.

    This server only handles GET requests, so this method shall raise a
    NotImplementedError if the method of the request is not GET.
    """

    method, path, version = request.split("\r\n")[0].split(" ")

    # Verify only GET methods are being sent
    if method != "GET":
        raise NotImplementedError

    return path


def response_path(path):
    """
    This method should return appropriate content and a mime type.

    If the requested path is a directory, then the content should be a
    plain-text listing of the contents with mimetype `text/plain`.

    If the path is a file, it should return the contents of that file
    and its correct mimetype.

    If the path does not map to a real location, it should raise an
    exception that the server can catch to return a 404 response.

    Ex:
        response_path('/a_web_page.html') -> (b"<html><h1>North Carolina...",
                                            b"text/html")

        response_path('/images/sample_1.png')
                        -> (b"A12BCF...",  # contents of sample_1.png
                            b"image/png")

        response_path('/') -> (b"images/, a_web_page.html, make_type.py,...",
                             b"text/plain")

        response_path('/a_page_that_doesnt_exist.html') -> Raises a NameError

    """
    # Setting webroot to the current directory
    base_dir = os.getcwd() + "/webroot"
    current_item = base_dir + path

    # Initializing the content and mime_type variables
    content = ""
    mime_type = ""

    # print("Base Dir " + base_dir)
    # print("Current Item " + current_item)

    # Determine if the file exists and is under the webroot directory
    # Raise a NameError if the requested content is not present under webroot
    if ((Path(base_dir) in Path(current_item).parents) and (Path(current_item).exists())) or \
            (os.path.normpath(base_dir) == os.path.normpath(current_item)):

        # Return a list of the directory content
        if os.path.isdir(current_item):
            for item in os.listdir(current_item):
                content += item + '\n'
                mime_type = "text/plain"
            content = content.encode()
        else:
            # Read the contents of the file
            with open(base_dir + path, 'rb') as file:
                content = file.read()

            # Get the file's mimetype, strip off the leading / to get the file name
            mime_type = mimetypes.guess_type(path[1:])[0]

    else:
        # print("Didn't find it")
        raise NameError

    return content, mime_type


def server(log_buffer=sys.stderr):
    address = ('127.0.0.1', 10000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("making a server on {0}:{1}".format(*address), file=log_buffer)
    sock.bind(address)
    sock.listen(1)

    try:
        while True:
            print('waiting for a connection', file=log_buffer)
            conn, addr = sock.accept()  # blocking
            try:
                print('connection - {0}:{1}'.format(*addr), file=log_buffer)

                request = ''
                while True:
                    data = conn.recv(1024)
                    request += data.decode('utf8')

                    if '\r\n\r\n' in request:
                        break

                print("Request received:\n{}\n\n".format(request))

                try:
                    path = parse_request(request)
                    # Use response_path to retrieve the content and the mimetype, based on the request path.
                    try:
                        content, mimetype = response_path(path)

                        # Use the content and mimetype from response_path to build a response_ok
                        response = response_ok(
                            body=content,
                            mimetype=mimetype.encode()
                        )

                    # If response_path raised a NameError then let the response be not_found
                    except NameError:
                        response = response_not_found()

                # If parse_request raised a NotImplementedError, then let the response be method_not_allowed
                except NotImplementedError:
                    response = response_method_not_allowed()

                # print("Response " + response.decode())
                conn.sendall(response)
            except:
                traceback.print_exc()
            finally:
                conn.close()

    except KeyboardInterrupt:
        sock.close()
        return
    except:
        traceback.print_exc()


if __name__ == '__main__':
    server()
    sys.exit(0)


