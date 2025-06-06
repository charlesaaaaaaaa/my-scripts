# Copyright (c) 2021-2022, PostgreSQL Global Development Group

# Verify WAL consistency

use strict;
use warnings;

use PostgreSQL::Test::Utils;
use Test::More;
use PostgreSQL::Test::Cluster;

# Set up primary
my $whiskey = PostgreSQL::Test::Cluster->new('whiskey');
$whiskey->init(allows_streaming => 1);
$whiskey->append_conf('postgresql.conf', 'wal_consistency_checking = brin');
$whiskey->start;
$whiskey->safe_psql('postgres', 'create extension pageinspect');
is( $whiskey->psql(
		'postgres',
		qq[SELECT pg_create_physical_replication_slot('standby_1');]),
	0,
	'physical slot created on primary');

# Take backup
my $backup_name = 'brinbkp';
$whiskey->backup($backup_name);

# Create streaming standby linking to primary
my $charlie = PostgreSQL::Test::Cluster->new('charlie');
$charlie->init_from_backup($whiskey, $backup_name, has_streaming => 1);
$charlie->append_conf('recovery.conf', 'primary_slot_name = standby_1');
$charlie->start;

# Now write some WAL in the primary

$whiskey->safe_psql(
	'postgres', qq{
create table tbl_timestamp0 (d1 timestamp(0) without time zone) with (fillfactor=10);
create index on tbl_timestamp0 using brin (d1) with (pages_per_range = 1, autosummarize=false);
});
# Run a loop that will end when the second revmap page is created
$whiskey->safe_psql(
	'postgres', q{
do
$$
declare
  current timestamp with time zone := '2019-03-27 08:14:01.123456789 UTC';
begin
  loop
    insert into tbl_timestamp0 select i from
      generate_series(current, current + interval '1 day', '28 seconds') i;
    perform brin_summarize_new_values('tbl_timestamp0_d1_idx');
    if (brin_metapage_info(get_raw_page('tbl_timestamp0_d1_idx', 0))).lastrevmappage > 1 then
      exit;
    end if;
    current := current + interval '1 day';
  end loop;
end
$$;
});

$whiskey->wait_for_catchup($charlie, 'replay', $whiskey->lsn('insert'));

done_testing();
