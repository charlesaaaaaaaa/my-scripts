select '创建表和对应的类型';
create type res_t as enum('0', '1');
drop TABLE if exists history;
CREATE TABLE history(id bigserial primary key, tsf_id int not null, b_tsf_id int not null, amount int not null, res res_t not null, opt_date timestamp not null, tips text);
create type status_t as enum('using', 'delete', 'freeze', 'unfreeze', 'create', 'notexist');
drop TABLE if exists test_user;
create table test_user(id serial primary key, name text not null, password text not null, status status_t not null, update_times int not null);
drop TABLE if exists amount;
create table amount(id serial primary key, u_id int not null, u_amount int not null);
drop TABLE if exists opt_history;
create table opt_history(id serial primary key, u_id int not null, opt text not null, opt_date timestamp not null, opt_res res_t not null);
-- 创建root用户
insert into test_user(name, password, status, update_times) value('root', 'root', 'using', 0);
insert into opt_history(u_id, opt, opt_date, opt_res) value(1, 'create', current_timestamp(), '1');