import sys
from typing import Sequence
from google.protobuf.json_format import MessageToDict
from pyloggerhelper import log
from schema_entry import EntryPoint
from echo_pb.echo_pb2 import Message
from .sdk import sdk, Client


class Test(EntryPoint):
    """grpc的服务端启动入口."""
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "required": ["address"],
        "properties": {
            "address": {
                "type": "string",
                "title": "a",
                "description": "服务启动地址",
                "default": "localhost:5000"
            }
        }
    }

    def do_main(self) -> None:
        url = self.config["address"]
        log.initialize_for_app(app_name="sdk", log_level="DEBUG")
        # req-res
        with sdk.initialize_from_url(url) as conn:
            res, call = conn.Square.with_call(Message(Message=2.0), metadata=(("a", "1"), ("b", "2")))
            header = call.initial_metadata()
            trailing = call.trailing_metadata()
            log.info("Square get result", res=MessageToDict(res), header=header, trailing=trailing)
        # req-stream
        with Client(url=url) as conn:
            res_stream = conn.RangeSquare(Message(Message=4.0))
            for res in res_stream:
                log.info("RangeSquare get msg", res=MessageToDict(res))
        # stream-res
        sdk.initialize_from_url(url)
        with sdk:
            res = sdk.SumSquare((Message(Message=float(i)) for i in range(4)))
            log.info("SumSquare get result", res=MessageToDict(res))
        # stream-stream
        with sdk:
            res_stream = sdk.StreamrangeSquare((Message(Message=float(i)) for i in range(4)), metadata=(("a", "1"), ("b", "2")))
            header = res_stream.initial_metadata()
            for res in res_stream:
                log.info("StreamrangeSquare get msg", res=MessageToDict(res))
            trailing = res_stream.trailing_metadata()
            log.info("StreamrangeSquare done", header=header, trailing=trailing)


def main(argv: Sequence[str]) -> None:
    test_node = Test(name="echo_serv_test")
    test_node(argv)


if __name__ == "__main__":
    main(sys.argv[1:])
