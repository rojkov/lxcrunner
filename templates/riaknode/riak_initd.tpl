#! /bin/bash
### BEGIN INIT INFO
# Provides:          riak
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: A distributed key value store
# Description:       Basho Technologies's Riak distributed key value store
### END INIT INFO

# Original Author: Vladimir Osintsev <osintsev@gmail.com>
# Modified for Ubuntu by: Matt Heitzenroder <mheitzenroder@gmail.com>
# Modified for Riak by: Grant Schofield <grant@basho.com>

PATH=/sbin:/usr/sbin:/bin:/usr/bin
DESC="a distributed key value store"
NAME=riak
ERTS_PATH=/usr/lib/riak/erts-5.7.5/bin
DAEMON=/usr/sbin/$NAME
RUNNER_LOG_DIR=/var/log/$NAME
RUNNER_USR_DIR=/usr
DAEMON_CONFDIR=/etc/$NAME
DAEMON_BASEDIR=/var/lib/$NAME
DAEMON_SHAREDIR=/usr/share/$NAME
DAEMON_ARGS='start'
SCRIPTNAME=/etc/init.d/$NAME


# Exit if the package is not installed
#[ -x "$RUNNER_USR_DIR/sbin/$NAME" ] || exit 0

# Read configuration variable file if it is present
[ -r /etc/default/$NAME ] && . /etc/default/$NAME

# Load the VERBOSE setting and other rcS variables
. /lib/init/vars.sh
. /lib/lsb/init-functions
# Setup command to control the node
NODETOOL="$ERTS_PATH/escript $ERTS_PATH/nodetool $NAME_ARG $COOKIE_ARG"

#
# Function that starts the daemon/service
#
do_start()
{
	# Return
	#   0 if daemon has been started
	#   1 if daemon was already running
	#   2 if daemon could not be started

	RETVAL=`$DAEMON ping`
	[ "$RETVAL" = "pong" ] && return 1
	
#
#	--chuid just doesn't seem to work at all
#
#	start-stop-daemon --start \
#		--name riak \
#		--chdir /var/lib/riak \
#		--chuid riak \
#		--user riak \
#		--exec $DAEMON -- $DAEMON_ARGS \
#		|| return 2

    su - derek -c "cd /home/derek/derek && git fetch && git checkout origin/{{branch}} && make compile" || return 2
	su - riak -c "$DAEMON $DAEMON_ARGS" || return 2
    {% if ip_address != main_riak_node %}
    sleep 3
    su - riak -c "/usr/sbin/riak-admin join riak@{{main_riak_node}}"
    sleep 1
    {% endif %}
}

#
# Function that stops the daemon/service
#
do_stop()
{
	# Try to stop via "riak stop" first
	RETVAL=`su - riak -c "$DAEMON ping"`
	[ "$RETVAL" = "pong" ] && su - riak -c "$DAEMON stop"
	sleep 2
	RETVAL=`pidof $ERTS_PATH/beam.smp`
	[ "$RETVAL" = "" ] && return 0
	#
	# It didn't exit nicely, be mean.
	#
	# Return
	#   0 if daemon has been stopped
	#   1 if daemon was already stopped
	#   2 if daemon could not be stopped
	#   other if a failure occurred
	start-stop-daemon --stop \
		--quiet \
		--retry=TERM/30/KILL/5 \
		--user riak \
		--exec $ERTS_PATH/beam.smp
	return $?
}

#
# Function that graceful reload the daemon/service
#
do_reload() {
        # Restart the VM without exiting the process
        su - riak -c "$DAEMON restart" && return $? || return 2
}


case "$1" in
  start)
	[ "$VERBOSE" != no ] && log_daemon_msg "Starting $DESC" "$NAME"
	do_start
	case "$?" in
		0|1) [ "$VERBOSE" != no ] && log_end_msg 0 ;;
		2) [ "$VERBOSE" != no ] && log_end_msg 1 ;;
	esac
	;;
  stop)
	[ "$VERBOSE" != no ] && log_daemon_msg "Stopping $DESC" "$NAME"
	do_stop
	case "$?" in
		0|1) [ "$VERBOSE" != no ] && log_end_msg 0 ;;
		2) [ "$VERBOSE" != no ] && log_end_msg 1 ;;
	esac
	;;
  ping)
	# See if the VM is alive
	$DAEMON ping || exit $?
	;;
  reload|force-reload)
	log_daemon_msg "Reloading $DESC" "$NAME"
	do_reload
	log_end_msg $?
	;;
  restart)
	log_daemon_msg "Restarting $DESC" "$NAME"
	do_stop
	case "$?" in
	  0|1)
		do_start
		case "$?" in
			0) log_end_msg 0 ;;
			1) log_end_msg 1 ;; # Old process is still running
			*) log_end_msg 1 ;; # Failed to start
		esac
		;;
	  *)
	  	# Failed to stop
		log_end_msg 1
		;;
	esac
	;;
  *)
	echo "Usage: $SCRIPTNAME {start|stop|ping|restart|force-reload}" >&2
	exit 3
	;;
esac

:

