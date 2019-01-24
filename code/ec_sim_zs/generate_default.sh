#!/bin/sh
go build . && ./long_sim && dot -Tpng chain.dot -o chain.png && open chain.png
