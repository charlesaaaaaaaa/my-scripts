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