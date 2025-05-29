from case import load_data, parquet_file, select_case
from res import connection, other, read_conf

def run_case():
    # try:
    other.wget_cdc()
    load_data.create_table()
    load_data.load_worker()
    res = 0
    for interrupt in range(0, 2):
        parquet_file.create_andscp_parquet_file(storage_type='local', interrupt=interrupt)
        load_data.create_parquet_table()
        tmp_res = select_case.Select().compare_table()
        res += tmp_res
    if res != 2:
        exit(1)
    # except Exception as err:
    #     print(err)
    #     res = 0
    # return res


if __name__ == "__main__":
    run_case()
