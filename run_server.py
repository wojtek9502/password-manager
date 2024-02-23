import argparse

import uvicorn


def run_server(port: int):
    uvicorn.run("src:app", host='0.0.0.0', port=port)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', required=False, default=8080)
    args = parser.parse_args()

    run_server(port=int(args.port))
