import random
import string
import subprocess

db_list = ['es', 'mongodb']
choice_dict = {}
for db in db_list:
    tmp_dict = {db: []}
    choice_dict.update(tmp_dict)
max_case_num = random.randint(1, len(db_list) * 2)
test_db_list = random.choices(db_list, k=max_case_num)
test_db, test_engine, test_partition = '', '', ''
for db in test_db_list:
    random_engine = random.choice(['InnoDB', 'rocksdb'])
    random_partition = random.choice(['0', '1'])
    cur_list = [random_engine, random_partition]
    while cur_list in choice_dict[db]:
        random_engine = random.choice(['InnoDB', 'rocksdb'])
        random_partition = random.choice(['0', '1'])
        cur_list = [random_engine, random_partition]
    choice_dict[db].append(cur_list)
    if not test_db:
        test_db += db
        test_engine += random_engine
        test_partition += random_partition
    else:
        test_db += ', %s' % db
        test_engine += ', %s' % random_engine
        test_partition += ', %s' % random_partition
case = "python3 ./rcr2cdc_test.py --db '%s' --engine '%s' --partition '%s'" % (test_db, test_engine, test_partition)
print(case)
run_case = subprocess.Popen(case, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
run_case.communicate()
run_case.terminate()
