#!/bin/bash

source ~/overcloudrc.v3

ALARM_ID=$(aodh alarm list | awk '/ Bono_1 / {print $2}')

if [[ $ALARM_ID != '' ]]; then
	aodh alarm delete $ALARM_ID
fi

INSTANCE_ID=$(nova list | awk '/ Bono_1 / {print $2}')

if [[ $INSTANCE_ID != '' ]]; then
	aodh alarm create --name Bono_1 \
	--description 'VM failure' --enabled True \
	--alarm-action 'http://192.168.11.254:6000/switch/False' \
	--repeat-actions True --severity moderate \
	--type event --event-type 'compute.instance.update' \
	--query "traits.instance_id=string::$INSTANCE_ID;traits.state=string::error"

	aodh alarm list
fi

