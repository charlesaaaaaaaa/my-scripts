-- 该测例使用的pg语法，主要是用的 【transfer_case】 存储过程 和 【change_user_status】 函数
-- 被转账(收款)者不能是id为1的root用户，且root用户创建后状态不能被修改
select '创建函数及存储过程';
-- 获取用户账号状态的函数
CREATE OR REPLACE FUNCTION get_user_status(u_uid int)
RETURNS status_t as $$
DECLARE u_status status_t;
BEGIN
    SELECT status INTO u_status FROM test_user where id = u_uid;
    IF u_status IS NULL THEN
        u_status := 'notexist';
    END IF;
    RETURN u_status;
END;
$$ LANGUAGE plpgsql;


-- 获取用户账号余额的函数
CREATE OR REPLACE FUNCTION get_user_amount(u_uid int)
RETURNS INT as $$
DECLARE t_amount int;
BEGIN
    -- 因为转账的存储过程已先验证过账户是否可用了，所以这里就不验证了
    SELECT u_amount INTO t_amount FROM amount where u_id = u_uid order by id desc limit 1;
    RETURN t_amount;
END;
$$ LANGUAGE plpgsql;


-- 变更用户账号状态的函数
CREATE OR REPLACE FUNCTION change_user_status(u_uid int, u_status status_t)
RETURNS INT AS $$
DECLARE res int;
DECLARE status_des text;
DECLARE tmp_status status_t;
DECLARE u_name text := 'user' || u_uid;
BEGIN
    select status INTO tmp_status from test_user where id = u_uid;
    -- 1: 正在使用中； 2：注销 3：冻结 4: 解冻
    IF tmp_status IS NULL THEN
        insert into test_user(name, password, status, update_times) value('tmp', 'tmp', 'using', 0);
        insert into opt_history(u_id, opt, opt_date, opt_res) values(u_uid, 'create', current_timestamp(), '1');
        -- insert into amount(u_id, u_amount) values(u_uid, 1000000);
        res := 1;
    ELSE
        IF tmp_status = 'using' THEN
            update test_user set update_times = update_times + 1 where id = u_uid;
            update test_user set status = u_status where id = u_uid;
            insert into opt_history(u_id, opt, opt_date, opt_res) values(u_uid, u_status, current_timestamp(), '1');
            res := 1;
        ELSIF tmp_status = 'delete' THEN
            update test_user set update_times = update_times + 1 where id = u_uid;
            insert into opt_history(u_id, opt, opt_date, opt_res) values(u_uid, u_status, current_timestamp(), '0');
            res := 0;
        ELSIF tmp_status = 'freeze' THEN
            update test_user set update_times = update_times + 1 where id = u_uid;
            if u_status = 'unfreeze' THEN
                update test_user set status = 'using' where id = u_uid;
                insert into opt_history(u_id, opt, opt_date, opt_res) values(u_uid, u_status, current_timestamp(), '1');
                res := 1;
            else
                insert into opt_history(u_id, opt, opt_date, opt_res) values(u_uid, u_status, current_timestamp(), '0');
                res := 0;
            END IF;
        END IF;
    END IF;
    RETURN res;
END;
$$ LANGUAGE plpgsql;


