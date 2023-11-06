user=$$(whoami)
uid=$$(id -u $(user))
gid=$$(id -g $(user))

.PHONY: caf-verilog/dev

all: caf-verilog/dev

caf-verilog/dev:
	docker build . -t $@ --build-arg developer=$(user) --build-arg uid=$(uid) --build-arg gid=$(gid)
