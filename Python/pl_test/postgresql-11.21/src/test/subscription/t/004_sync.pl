# Tests for logical replication table syncing
use strict;
use warnings;
use PostgresNode;
use TestLib;
use Test::More tests => 7;

# Initialize publisher node
my $node_publisher = get_new_node('publisher');
$node_publisher->init(allows_streaming => 'logical');
$node_publisher->start;

# Create subscriber node
my $node_subscriber = get_new_node('subscriber');
$node_subscriber->init(allows_streaming => 'logical');
$node_subscriber->append_conf('postgresql.conf',
	"wal_retrieve_retry_interval = 1ms");
$node_subscriber->start;

# Create some preexisting content on publisher
$node_publisher->safe_psql('postgres',
	"CREATE TABLE tab_rep (a int primary key)");
$node_publisher->safe_psql('postgres',
	"INSERT INTO tab_rep SELECT generate_series(1,10)");

# Setup structure on subscriber
$node_subscriber->safe_psql('postgres',
	"CREATE TABLE tab_rep (a int primary key)");

# Setup logical replication
my $publisher_connstr = $node_publisher->connstr . ' dbname=postgres';
$node_publisher->safe_psql('postgres',
	"CREATE PUBLICATION tap_pub FOR ALL TABLES");

my $appname = 'tap_sub';
$node_subscriber->safe_psql('postgres',
	"CREATE SUBSCRIPTION tap_sub CONNECTION '$publisher_connstr application_name=$appname' PUBLICATION tap_pub"
);

# Wait for initial table sync to finish
$node_subscriber->wait_for_subscription_sync($node_publisher, $appname);

my $result =
  $node_subscriber->safe_psql('postgres', "SELECT count(*) FROM tab_rep");
is($result, qq(10), 'initial data synced for first sub');

# drop subscription so that there is unreplicated data
$node_subscriber->safe_psql('postgres', "DROP SUBSCRIPTION tap_sub");

$node_publisher->safe_psql('postgres',
	"INSERT INTO tab_rep SELECT generate_series(11,20)");

# recreate the subscription, it will try to do initial copy
$node_subscriber->safe_psql('postgres',
	"CREATE SUBSCRIPTION tap_sub CONNECTION '$publisher_connstr application_name=$appname' PUBLICATION tap_pub"
);

# but it will be stuck on data copy as it will fail on constraint
my $started_query = "SELECT srsubstate = 'd' FROM pg_subscription_rel;";
$node_subscriber->poll_query_until('postgres', $started_query)
  or die "Timed out while waiting for subscriber to start sync";

# remove the conflicting data
$node_subscriber->safe_psql('postgres', "DELETE FROM tab_rep;");

# wait for sync to finish this time
$node_subscriber->wait_for_subscription_sync;

# check that all data is synced
$result =
  $node_subscriber->safe_psql('postgres', "SELECT count(*) FROM tab_rep");
is($result, qq(20), 'initial data synced for second sub');

# now check another subscription for the same node pair
$node_subscriber->safe_psql('postgres',
	"CREATE SUBSCRIPTION tap_sub2 CONNECTION '$publisher_connstr application_name=$appname' PUBLICATION tap_pub WITH (copy_data = false)"
);

# wait for it to start
$node_subscriber->poll_query_until('postgres',
	"SELECT pid IS NOT NULL FROM pg_stat_subscription WHERE subname = 'tap_sub2' AND relid IS NULL"
) or die "Timed out while waiting for subscriber to start";

# and drop both subscriptions
$node_subscriber->safe_psql('postgres', "DROP SUBSCRIPTION tap_sub");
$node_subscriber->safe_psql('postgres', "DROP SUBSCRIPTION tap_sub2");

# check subscriptions are removed
$result = $node_subscriber->safe_psql('postgres',
	"SELECT count(*) FROM pg_subscription");
is($result, qq(0), 'second and third sub are dropped');

# remove the conflicting data
$node_subscriber->safe_psql('postgres', "DELETE FROM tab_rep;");

# recreate the subscription again
$node_subscriber->safe_psql('postgres',
	"CREATE SUBSCRIPTION tap_sub CONNECTION '$publisher_connstr application_name=$appname' PUBLICATION tap_pub"
);

# and wait for data sync to finish again
$node_subscriber->wait_for_subscription_sync;

# check that all data is synced
$result =
  $node_subscriber->safe_psql('postgres', "SELECT count(*) FROM tab_rep");
is($result, qq(20), 'initial data synced for fourth sub');

# add new table on subscriber
$node_subscriber->safe_psql('postgres', "CREATE TABLE tab_rep_next (a int)");

# setup structure with existing data on pubisher
$node_publisher->safe_psql('postgres',
	"CREATE TABLE tab_rep_next (a) AS SELECT generate_series(1,10)");

$node_publisher->wait_for_catchup($appname);

$result = $node_subscriber->safe_psql('postgres',
	"SELECT count(*) FROM tab_rep_next");
is($result, qq(0), 'no data for table added after subscription initialized');

# ask for data sync
$node_subscriber->safe_psql('postgres',
	"ALTER SUBSCRIPTION tap_sub REFRESH PUBLICATION");

# wait for sync to finish
$node_subscriber->wait_for_subscription_sync;

$result = $node_subscriber->safe_psql('postgres',
	"SELECT count(*) FROM tab_rep_next");
is($result, qq(10),
	'data for table added after subscription initialized are now synced');

# Add some data
$node_publisher->safe_psql('postgres',
	"INSERT INTO tab_rep_next SELECT generate_series(1,10)");

$node_publisher->wait_for_catchup($appname);

$result = $node_subscriber->safe_psql('postgres',
	"SELECT count(*) FROM tab_rep_next");
is($result, qq(20),
	'changes for table added after subscription initialized replicated');

$node_subscriber->safe_psql('postgres', "DROP SUBSCRIPTION tap_sub");

$node_subscriber->stop('fast');
$node_publisher->stop('fast');
