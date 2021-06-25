from time import time
from typing import Callable, Awaitable
from pyloggerhelper import log
import grpc


class TimerInterceptor(grpc.ServerInterceptor):

    def intercept_service(self,
                          continuation: Callable[[grpc.HandlerCallDetails], grpc.RpcMethodHandler],
                          handler_call_details: grpc.HandlerCallDetails) -> grpc.RpcMethodHandler:
        start = time()
        ctx = continuation(handler_call_details)
        log.info("query cost", cost=time() - start, method=handler_call_details.method)
        return ctx