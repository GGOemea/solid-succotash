#!/bin/sh

set -e

dest="$1"
tmp=$(mktemp -d)
trap "rm -rf '$tmp'" EXIT

cd $tmp
if [ -d /etc/ssl/ca-global ]; then
	wgetopts=--ca-directory=/etc/ssl/ca-global
fi
wget $wgetopts -q https://api.fastly.com/public-ip-list
if cmp public-ip-list "$dest" >/dev/null; then
	exit 0
fi
chmod --reference="$dest" public-ip-list
mv public-ip-list "$dest"
