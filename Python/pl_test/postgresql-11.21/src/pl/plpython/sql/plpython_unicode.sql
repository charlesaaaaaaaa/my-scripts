--
-- Unicode handling
--
-- Note: this test case is known to fail if the database encoding is
-- EUC_CN, EUC_JP, EUC_KR, or EUC_TW, for lack of any equivalent to
-- U+00A0 (no-break space) in those encodings.  However, testing with
-- plain ASCII data would be rather useless, so we must live with that.
--

SET client_encoding TO UTF8;

CREATE TABLE unicode_test (
	testvalue  text NOT NULL
);

CREATE FUNCTION unicode_return() RETURNS text AS E'
return u"\\xA0"
' LANGUAGE plpython3u;

CREATE FUNCTION unicode_trigger() RETURNS trigger AS E'
TD["new"]["testvalue"] = u"\\xA0"
return "MODIFY"
' LANGUAGE plpython3u;

CREATE TRIGGER unicode_test_bi BEFORE INSERT ON unicode_test
  FOR EACH ROW EXECUTE PROCEDURE unicode_trigger();

CREATE FUNCTION unicode_plan1() RETURNS text AS E'
plan = plpy.prepare("SELECT $1 AS testvalue", ["text"])
rv = plpy.execute(plan, [u"\\xA0"], 1)
return rv[0]["testvalue"]
' LANGUAGE plpython3u;

CREATE FUNCTION unicode_plan2() RETURNS text AS E'
plan = plpy.prepare("SELECT $1 || $2 AS testvalue", ["text", u"text"])
rv = plpy.execute(plan, ["foo", "bar"], 1)
return rv[0]["testvalue"]
' LANGUAGE plpython3u;


SELECT unicode_return();
INSERT INTO unicode_test (testvalue) VALUES ('test');
SELECT * FROM unicode_test;
SELECT unicode_plan1();
SELECT unicode_plan2();
