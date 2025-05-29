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
        insert into amount(u_id, u_amount) values(u_uid, 1000000);
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


-- 转账的存储过程
--  先调用 获取用户状态 的函数，确认正常的情况下进行下一步，否则直接失败
--   失败则更新history表
--  调用获取本用户账号余额的函数，如果大于要转账的金额则进行下一步，否则失败
--   失败则更新history表
--  减去amount表本账户的金额，增加amount表对方的金额
--   更新history表，状态成功
CREATE OR REPLACE PROCEDURE transfer_case(u_uid int, t_amount int, b_uid int)
LANGUAGE plpgsql
AS $$
DECLARE user_status text;
DECLARE u_user_amount int;
DECLARE b_user_amount int;
DECLARE b_u text := '被转账者';
DECLARE u_u text := '转账者';
BEGIN
    IF u_uid = b_uid then
        insert into history(tsf_id, b_tsf_id, amount, res, opt_date, tips) values(u_uid, b_uid, t_amount, '0', current_timestamp(), '无法于对同一用户进行转账');
        commit;
        RAISE EXCEPTION '无法于对同一用户进行转账';
    END IF;
    -- 查看用户状态, 非使用中的用户直接更新history表并退出
    select * into user_status from get_user_status(u_uid);
    IF user_status <> 'using' then
        user_status = u_u || user_status;
        insert into history(tsf_id, b_tsf_id, amount, res, opt_date, tips) values(u_uid, b_uid, t_amount, '0', current_timestamp(), user_status);
        commit;
        RAISE EXCEPTION '转账者状态异常';
    END IF;
    select * into user_status from get_user_status(b_uid);
    IF user_status <> 'using' then
        user_status = b_u || user_status;
        insert into history(tsf_id, b_tsf_id, amount, res, opt_date, tips) values(u_uid, b_uid, t_amount, '0', current_timestamp(), user_status);
        commit;
        RAISE EXCEPTION '被转账者状态异常';
    END IF;
    -- 查看转账者钱够不够, 不够的话直接更新history表并退出
    -- 如果转账者u_id是1(root用户)，则代表是充钱到被转账者账户上了，不会减少钱
    IF u_uid <> 1 then
        select * into u_user_amount from get_user_amount(u_uid);
        IF u_user_amount < t_amount then
            insert into history(tsf_id, b_tsf_id, amount, res, opt_date, tips) values(u_uid, b_uid, t_amount, '0', current_timestamp(), '不够，得加钱');
            commit;
            RAISE EXCEPTION '转账者钱不够';
        END IF;
        insert into amount(u_id, u_amount) values(u_uid, u_user_amount - t_amount);
    END IF;
    select * into b_user_amount from get_user_amount(b_uid);
    insert into amount(u_id, u_amount) values(b_uid, b_user_amount + t_amount);
    IF u_uid = 1 then
        insert into history(tsf_id, b_tsf_id, amount, res, opt_date, tips) values(u_uid, b_uid, t_amount, '1', current_timestamp(), '充值用户余额');
    ELSE
        insert into history(tsf_id, b_tsf_id, amount, res, opt_date, tips) values(u_uid, b_uid, t_amount, '1', current_timestamp(), '');
    END IF;
END;
$$;