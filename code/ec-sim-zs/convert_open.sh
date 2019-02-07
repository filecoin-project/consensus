#!/bin/sh
dot -Tpng $1 -o chain.png && open chain.png
