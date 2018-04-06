from flask import Flask,jsonify, request

app = Flask(__name__)
metro_test_port = 0
metro_test_host = 'localhost'


port_with_error = 15


@app.route('/api/v1/metro', methods=['POST'])
def success_metro_response():
    response = dict()
    response['username'] = 'test'
    response['password'] = 'abc123'
    response['original_host'] = 'originalhost.com'
    response['original_port'] = 2222
    response['metro_host'] = metro_test_host if request.json['original_host'] == metro_test_host else 'aodjeodeide.com'
    response['metro_port'] = metro_test_port if request.json['original_port'] == 2222 else port_with_error

    return jsonify(response), 201


def start_metro_server(port, metro_host, metro_port, incorrect_port=15):
    global port_with_error

    port_with_error = incorrect_port

    print('Starting fake metro server on port %d' % port)
    global metro_test_host, metro_test_port
    metro_test_host = metro_host
    metro_test_port = metro_port

    app.run(debug=False, port=port, host='localhost')
