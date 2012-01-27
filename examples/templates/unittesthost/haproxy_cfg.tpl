global
	maxconn 4096
	#chroot /usr/share/haproxy
	user haproxy
	group haproxy
	daemon

defaults
	log	global
	mode	http
	option	dontlognull
	retries	3
	maxconn	2000
	contimeout	5000
	clitimeout	50000
	srvtimeout	50000

frontend riak_http
	mode http
	bind 127.0.0.1:8098
	default_backend riak_http_servs

backend riak_http_servs
	balance roundrobin
	option httpchk GET /ping
    {% for ipaddr in split(riak_hosts) %}
	server riak_http{{loop.index}} {{ipaddr|trim}}:8098 check
    {% endfor %}

frontend riak_protobuf
	mode tcp
	bind 127.0.0.1:8087
	default_backend riak_protobuf_servs

backend riak_protobuf_servs
        mode tcp
	balance roundrobin
	option httpchk GET /ping
    {% for ipaddr in split(riak_hosts) %}
	server riak_protobuf{{loop.index}} {{ipaddr|trim}}:8087 check addr {{ipaddr}} port 8098
    {% endfor %}
