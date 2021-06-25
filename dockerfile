FROM --platform=$TARGETPLATFORM python:3.9-slim-buster as install_requirements
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list
RUN apt update -y && apt install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*
COPY pip.conf /etc/pip.conf
RUN pip --no-cache-dir install --upgrade pip
WORKDIR /code
RUN mkdir /code/tp_py_grpc_sync
COPY requirements.txt /code/requirements.txt
RUN python -m pip --no-cache-dir install -r requirements.txt --target tp_py_grpc_sync

FROM --platform=$TARGETPLATFORM golang:buster as build_grpc-health-probe
ENV GO111MODULE=on
ENV GOPROXY=https://goproxy.io
# 停用cgo
ENV CGO_ENABLED=0
# 安装grpc-health-probe
RUN go get github.com/grpc-ecosystem/grpc-health-probe

FROM --platform=$TARGETPLATFORM python:3.9-slim-buster as build_img
# 打包镜像
COPY --from=build_grpc-health-probe /go/bin/grpc-health-probe /code/
RUN chmod +x /code/grpc-health-probe
COPY --from=install_requirements /code/tp_py_grpc_sync /code/tp_py_grpc_sync/
# 复制源文件
COPY tp_py_grpc_sync /code/tp_py_grpc_sync/
WORKDIR /code
EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD [ "./grpc-health-probe","-addr=:5000" ]
ENTRYPOINT ["python", "tp_py_grpc_sync", "serv"]