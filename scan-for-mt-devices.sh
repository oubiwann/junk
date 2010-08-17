#!/bin/bash
#
# This script reports the MT-capable devices present in your system
#

pushd . > /dev/null

cd /sys/class/input
typeset -i nbit=64
typeset -i nhex=$nbit/4

for d in event*; do
    dev=/dev/input/$d
    name=`cat $d/device/name`
    abs=`cat $d/device/capabilities/abs`
    hex=`printf %${nhex}s $abs`
    typeset -i i=0
    while [ $i -lt $nhex ]; do
	typeset -i word=$nhex-1-$i
	valS=${hex:$word:1}
	val10=$[0x$valS]
	if [ "X$val10" = "X" ]; then
	    valBS="0000"
	else
	    valBS=`echo "ibase=10; obase=2; $val10" | bc`
	fi	    
	valB=`printf %4s "$valBS"`
	typeset -i j=0
	while [ $j -lt 4 ]; do
	    typeset -i bit=4*$i+$j
	    typeset -i mask[$bit]=${valB:$j:1}
	    j=$j+1
	done
	i=$i+1
    done
    has_mt=${mask[0x35]}
    if [ $has_mt = 1 ]; then
	if [ "X$dev_detected" = "X" ]; then
		dev_detected = 1
		echo "Found device(s):" >&2
	fi
	echo $name: $dev
    fi
done
if [ "X$dev_detected" = "X" ]; then
	echo "No MT-capable device found..." >&2
fi

popd > /dev/null
