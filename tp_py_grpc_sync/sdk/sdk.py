from typing import Any, Optional, Dict
import grpc
from pyproxypattern import Proxy
from echo_pb.echo_pb2_grpc import ECHOStub
from .interceptor.timer import TimerInterceptor


class Client(Proxy):
    __slots__ = ("url", "options", "channel", "tls", "credentials", 'instance', 'compression', '_callbacks', '_instance_check')
    url: Optional[str]
    options: Dict[str, Any]
    channel: Optional[grpc.Channel]
    instance: Optional[ECHOStub]

    def __init__(self, *,
                 url: Optional[str] = None,
                 tls: bool = False,
                 credentials: Optional[grpc.ChannelCredentials] = None,
                 compression: Optional[Any] = None,
                 **options: Any) -> None:
        super().__init__()
        self.channel = None
        self.instance = None
        self.tls = tls
        self.credentials = credentials
        self.compression = compression
        if options:
            self.options = options
        else:
            self.options = {}
        if url:
            self.url = url
            self.new_instance()
        else:
            self.url = None

    def new_instance(self) -> None:
        if not self.url:
            raise AttributeError("need url!")
        if self.options:
            options = [(k, v) for k, v in self.options.items()]
            if self.tls:
                channel = grpc.secure_channel(self.url, self.credentials, compression=self.compression, options=options)
            else:
                channel = grpc.insecure_channel(self.url, compression=self.compression, options=options)
        else:
            if self.tls:
                channel = grpc.secure_channel(self.url, self.credentials, compression=self.compression)
            else:
                channel = grpc.insecure_channel(self.url, compression=self.compression)
        # self.channel = channel
        # 注册拦截器
        self.channel = grpc.intercept_channel(channel, TimerInterceptor())
        client = ECHOStub(self.channel)
        self.initialize(client)

    def initialize_from_url(self, url: str, *,
                            tls: bool = False,
                            credentials: Optional[grpc.ChannelCredentials] = None,
                            compression: Optional[Any] = None,
                            **options: Any) -> "Client":
        self.url = url
        if options:
            self.options.update(options)
        if tls:
            self.tls = tls
        if credentials:
            self.credentials = credentials
        if compression:
            self.compression = compression
        self.new_instance()
        return self

    def close(self) -> None:
        if self.channel:
            self.channel.close()
            self.channel = None
            self.instance = None

    def __enter__(self) -> "Client":
        if not self.instance:
            self.new_instance()
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.close()


sdk = Client()