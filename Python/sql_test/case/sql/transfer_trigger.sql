-- 新增用户时触发余额加100000的触发器
CREATE OR REPLACE FUNCTION add_amount()
RETURNS TRIGGER AS $$
DECLARE max_id int;
   BEGIN
      select max(id) INTO max_id from test_user;
      insert into amount(u_id, u_amount) values(max_id, 100000);
      RETURN NEW;
   END;
$$
LANGUAGE plpgsql;

CREATE TRIGGER trigger_add_amount AFTER INSERT ON test_user FOR EACH ROW EXECUTE PROCEDURE add_amount();