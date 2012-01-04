## Name of the riak node
-name riak@{{ip_address}}

## Cookie for distributed erlang.  All nodes in the same cluster
## should use the same cookie or they will not be able to communicate.
-setcookie riak

## Heartbeat management; auto-restarts VM if it dies or becomes unresponsive
## (Disabled by default..use with caution!)
##-heart

## Enable kernel poll and a few async threads
+K true
+A 64

## Treat error_logger warnings as warnings
+W w

## Increase number of concurrent ports/sockets
-env ERL_MAX_PORTS 4096

## Tweak GC to run more often 
-env ERL_FULLSWEEP_AFTER 0

## Set the location of crash dumps
-env ERL_CRASH_DUMP /var/log/riak/erl_crash.dump

## Begin SSL distribution items, DO NOT DELETE OR EDIT THIS COMMENT

## To enable SSL encryption of the Erlang intra-cluster communication,
## un-comment the three lines below and make certain that the paths
## point to correct PEM data files.  See docs TODO for details.

## -proto_dist inet_ssl
## -ssl_dist_opt client_certfile "/etc/riak/erlclient.pem"
## -ssl_dist_opt server_certfile "/etc/riak/erlserver.pem"

## End SSL distribution items, DO NOT DELETE OR EDIT THIS COMMENT

