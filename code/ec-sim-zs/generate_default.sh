#!/bin/sh
go build . && ./ec-sim-zs && dot -Tpng chain.dot -o chain.png && open chain.png
