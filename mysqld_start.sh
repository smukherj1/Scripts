
MYSQL_HOME=/home/suvanjan/apps/mysql-5.7.13
./bin/mysqld --basedir=$MYSQL_HOME\
	--character-sets-dir $MYSQL_HOME/etc/share/charsets\
	--datadir=$MYSQL_HOME/data\
	--general-log-file=$MYSQL_HOME/data/suvanjan-centos.log\
	--language=$MYSQL_HOME/etc/share\
	--lc-messages-dir=$MYSQL_HOME/share\
	--pid-file=$MYSQL_HOME/etc/suvanjan-centos.pid\
	--plugin-dir=$MYSQL_HOME/etc/lib/plugin\
	--slave-load-tmpdir=$MYSQL_HOME/etc/tmp\
	--slow-query-log-file=$MYSQL_HOM/etc/Esuvanjan-centos-slow.log\
	--bind-address=0.0.0.0\
	--socket=$MYSQL_HOME/etc/mysql.sock\
	--tmpdir=$MYSQL_HOME/etc/tmp\
