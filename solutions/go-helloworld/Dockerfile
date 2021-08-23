FROM balenalib/raspberry-pi-alpine-golang:latest

WORKDIR /go/src/app

ADD . .

RUN go mod init
RUN go build -o helloworld
RUN go mod tidy

EXPOSE 6112

CMD ["./helloworld"]

