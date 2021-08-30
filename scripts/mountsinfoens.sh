#!/bin/bash

#LG on dec 2015.
#mounting nfs lip account in a local directory (destdir)
#or sync with a particular directory of your lip's home.
#via ssh connecting on a lip machine.
#ssh $user@$machine should work.
#(apt-get install sshfs)


usersinfo="lgonnord"
sinfomachine="slsu0-07.dsi-ext"

#mount all nfs files into this local dir:
destdir="/home/laure/SinfoENS/"

#rsync one local with distant directory 
localdirtosync="/home/laure/Test"
destdirtosync="/home/lgonnord/TestSync"

usage() {
    echo `basename $0`: ERROR: $* 1>&2
    echo usage: `basename $0` 'on|off|save '
    exit 1
}

#mount all your nfs sinfo's account into $destdir
do_on () {
    nbfiles=$(ls -a "$destdir"| sed -e "/\.$/d" | wc -l)
    if [ ! "$nbfiles" -eq 0 ]
    then
	echo "hump, the directory seems to be already mounted (or there remains files)"
	exit -1
    else
	sshfs $usersinfo@$sinfomachine:/home/$usersinfo/ $destdir
    fi
}


#unmount the nfs account
do_off(){
    nbfiles=$(ls -a "$destdir"| sed -e "/\.$/d" | wc -l)
    if [ "$nbfiles" -eq 0 ]
    then  echo "hump, the directory seems to be already unmounted"
    else
	fusermount -u $destdir
    fi
}

#synchronise a local dir into a distant directory.
do_save(){
    echo "syncing with : $sinfomachine:$destdirtosync"
    rsync -avz --del --stats -e ssh $localdirtosync "$usersinfo@$sinfomachine:$destdirtosync"
    
    # --exclude-from '<local_path>/exclude.rsync' <-- if you want to exclude some files.

}

case "$1" in
    on) do_on;;
    off) echo "off!" ; do_off ;;
    save) echo "save!" ; do_save ;;
    *) usage "bad argument $1";;
esac

