#!/bin/sh
trap : TERM INT
/root/emqx/bin/emqx start
tail -f /dev/null & wait