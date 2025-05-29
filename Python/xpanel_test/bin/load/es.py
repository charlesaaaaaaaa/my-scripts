import json
import multiprocessing
import threading
import warnings
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import bin
import random
import datetime
import string
import time


class LoadEs:
    def __init__(self):
        host, port = [], []
        conf = bin.other_opt.getconf().getXpanelInfo()
        host_port = conf['es_host_port'].replace(', ', ',').split(',')
        for i in range(len(host_port)):
            hp = host_port[i].split(':')
            host.append(hp[0])
            port.append(hp[1])
        self.host, self.port = host, port

    def es_conn(self, host_num=0, print_url=0):
        # host_num, 如果设置文件里面的有多个es信息时，host_num从0开始代表对应的es信息
        url = 'http://%s:%s' % (self.host[host_num], self.port[host_num])
        if print_url == 1:
            print('\n正在操作es: [%s]' % url)
        # 禁用特定警告, 这个安全功能不可用的警告一直在刷，看得心烦
        warnings.filterwarnings("ignore", message="Elasticsearch built-in security features are not enabled")
        # 请求超时60s，并在连接失败后最多重试三次
        conn = Elasticsearch([url], request_timeout=60, max_retries=3, retry_on_timeout=True)
        return conn

    def delete_create_index(self, index_name='test_index', host_num=0):
        conn = self.es_conn(host_num=host_num, print_url=1)
        print('删除索引【%s】' % index_name)
        if conn.indices.exists(index=index_name):
            response = conn.indices.delete(index=index_name)
            print('索引【%s】存在，删除成功, 响应【%s】' % (index_name, response))
        else:
            print('索引【%s】不存在，跳过' % index_name)
        index_body = {
            "mappings": {
            "properties": {
                "cur_time": {
                    "type": "date"
                },
                "float": {
                    "type": "float"
                },
                "ip": {
                    "properties": {
                        "ipv4": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        },
                        "ipv6": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "ipv4": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "ipv6": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "mac": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "num": {
                    "type": "long"
                },
                "thread": {
                    "type": "long"
                },
                "txt": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                }
            }
        }
        }
        response = conn.indices.create(index=index_name, body=index_body)
        print('索引创建成功，响应[%s]' % response)
        conn.close()

    def gen_data(self, num, thread_num, index_name='test_index'):
        # 随机产生一个从小到大且不重复的数字列表，数量随机
        insert_type = sorted(set(random.choices(range(1, 8), k=7)))

        def text():
            txt = ''.join(random.choices(string.ascii_letters, k=random.randint(25, 50)))
            return txt

        def float_type():
            float_num = random.uniform(0, 10000)
            return float_num

        def time_type():
            cur_time = datetime.datetime.now()
            return cur_time

        def generate_mac(separator=":"):
            # 生成6个字节的十六进制数（0x00 ~ 0xFF）
            mac_bytes = [random.randint(0x00, 0xff) for _ in range(6)]
            # 将字节格式化为2位十六进制字符串，并用分隔符连接
            mac = separator.join(f"{byte:02x}" for byte in mac_bytes)
            return mac

        def generate_ipv(sep=".", ipv=4):
            # ipv = [4] or [6]
            # 生成[ipv]个256的str字符
            net_bytes = [str(random.randint(0, 256)) for _ in range(ipv)]
            # 通过join转化成ipv[ipv]地址
            net = sep.join(net_bytes)
            return net

        insert_dict = {}
        # 通过最开始随机生成的数字列表来确定要生成的是什么类型的数据
        for i in insert_type:
            if i == 1:
                insert_dict.update({"txt": text()})
            elif i == 2:
                insert_dict.update({"float": float_type()})
            elif i == 3:
                insert_dict.update({"cur_time": time_type()})
            elif i == 4:
                insert_dict.update({"mac": generate_mac()})
            elif i == 5:
                insert_dict.update({"ipv4": generate_ipv(ipv=4)})
            elif i == 6:
                insert_dict.update({"ipv6": generate_ipv(ipv=6)})
            elif i == 7:
                insert_dict.update({"ip": {"ipv4": generate_ipv(ipv=4), "ipv6": generate_ipv(ipv=6)}})
        insert_dict.update({"num": num, "thread": thread_num})
        gen_dict = {'_index': index_name, "_source": insert_dict}
        # print(gen_dict)
        return gen_dict

    def mutil_load(self, threads=None, process=None, each_thread_size=100, index_name="test_index", drop=0):
        # drop为1时删除并创建同名的index
        if drop == 1:
            self.delete_create_index(index_name=index_name)
        if process:
            size = process * each_thread_size
        elif threads:
            size = threads * each_thread_size
        else:
            size = 10 * each_thread_size
        print('\n开始准备【%s】数据到【%s】' % (size, index_name))
        time.sleep(1)

        def single_process(process_num):
            # 指定了进程数就用进程跑，提示词也为进程
            # 反之用线程
            if not process:
                mutli_word = 'threads'
            else:
                mutli_word = 'process'
            print('\t<<< %s_%s 开始准备[%s]行数据 >>>' % (mutli_word, process_num, each_thread_size))
            time.sleep(1)
            conn = self.es_conn()
            data_list = []
            try:
                for num in range(1, each_thread_size + 1):
                    data = self.gen_data(num=num, thread_num=process_num, index_name=index_name)
                    data_list.append(data)
                    if num % 100 == 0:
                        bulk(conn, actions=data_list)
                        data_list = []
                        print('\r%s_%s [%s]' % (mutli_word, process_num, num), end='')
                if data_list:
                    bulk(client=conn, actions=data_list)
                print('\t<<< %s_%s [%s]行数据准备完成 >>>' % (mutli_word, process_num, each_thread_size))
            except Exception as err:
                print('ERROR: %s_%s %s' % (mutli_word, process_num, str(err)))
            finally:
                conn.close()

        tl = []
        # 当同时都不指定用进程数或者线程数灌数据时默认使用10个线程灌数据
        if not process:
            if not threads:
                threads = 10
        else:
            threads = process
        for i in range(threads):
            # 但只要指定了进程数灌数据，那么一定是用多进程灌数据，即使同时指定了线程数也一样
            if not process:
                t = threading.Thread(target=single_process, args=(i, ))
            else:
                t = multiprocessing.Process(target=single_process, args=(i, ))
            tl.append(t)
            t.start()
        for t in tl:
            t.join()
        print('数据准备完毕')

    def single_process(self, slice_id, total_slices, index_name, host_num):
        results = []
        conn = self.es_conn(host_num=host_num)
        response = conn.search(index=index_name, body={
            "query": {
                "match_all": {}
            },
            "sort": {
                "num": {
                    "order": "asc"
                },
                "thread": {
                    "order": "asc"
                }
            }
        }, size=10000, scroll="3m", params={"slice": {"id": slice_id, "max": total_slices}})
        # }, size=10000, scroll="3m")
        # 获取scroll_id， 以这个变量来获取后续的文档
        scroll_id = response['_scroll_id']
        hits = response['hits']['hits']
        results.extend(hits)
        n = 1
        while len(response["hits"]["hits"]) > 0:
            # 获取下一批
            n += 1
            print('\rprocess_%s: %s>>>>>' % (slice_id, n), end='')
            response = conn.scroll(scroll_id=scroll_id, scroll="2m")
            scroll_id = response['_scroll_id']
            # 这是只获取_source，因为与_source同级的还有es自动生成的_id值和其它东西
            # results.extend(response["hits"]["hits"])
            for i in response["hits"]["hits"]:
                results.append(i['_source'])
        return results

    def show_data(self, count=0, index_name='test_index', host_num=0):
        # return_column就是当要返回总文档数据时要其中的什么列，有['_index']|['_id']|['_score']|['_source']
        # _index 就是index名，一般不用；_id就是id值；_score全都是1.0，不知道干嘛的；_source就是其文档数据，默认值
        # 有用的除了默认的_source之外就只有_id了，获取了后可以给后面做delete和update操作
        conn = self.es_conn(host_num=host_num)
        res = []
        if host_num == 0:
            es_role = '上游'
        else:
            es_role = '下游'
        bodys = {
            "query": {
                "match_all": {}
            },
            "sort": {
                "num": {
                    "order": "asc"
                },
                "thread": {
                    "order": "asc"
                }
            }
        }
        if count == 1:
            # 当count为1时，只返回文档总数量
            res = conn.count(index=index_name)['count']
            # print('index[%s]共有文档数量: [%s]' % (index_name, res))
        elif count == 0:
            # 当为0时，返回总文档数据，返回一个列表
            count = conn.count(index=index_name)['count']
            if count <= 10000:
                res = conn.search(index=index_name, body=bodys, size=count)
            else:
                # 因为有最大查询数据量的限制(10000条)，故我们在大于10000条时要用到scroll来去查出所有的文档
                # 第一次查询 scroll="3m" 就是保持上下文三分钟
                conn = self.es_conn(host_num=host_num)
                response = conn.search(index=index_name, body=bodys, size=10000, scroll="3m")
                # }, size=10000, scroll="3m", params={"slice": {"id": slice_id, "max": total_slices}})
                # 获取scroll_id， 以这个变量来获取后续的文档
                scroll_times = 1
                total_times = int(count / 10000)
                while len(response["hits"]["hits"]) > 0:
                    print('\r正在获取[%s]数据第[%s/%s]批次' % (es_role, scroll_times, total_times), end='')
                    scroll_id = response['_scroll_id']
                    # 这是只获取_source，因为与_source同级的还有es自动生成的_id值和其它东西
                    for i in response["hits"]["hits"]:
                        res.append(i['_source'])
                    # 获取下一批
                    response = conn.scroll(scroll_id=scroll_id, scroll="2m")
                    scroll_times += 1
                # print('开始多进程获取 %s es总文档数，每个进程需要获取约%s次' % (nodes, int(count / total_slices / 10000) + 1))
                # with multiprocessing.Pool(total_slices) as pool:
                #     # 为每个切片创建一个任务
                #     tasks = [(i, total_slices, index_name, host_num) for i in range(total_slices)]
                #     results = pool.starmap(self.single_process, tasks)
                #
                # # 合并所有切片的结果
                # print('合并文档...', end='')
                # res = [doc for slice_result in results for doc in slice_result]
                # print(f"\t总文档数量: {len(res)}")
        return res

    def update_data(self, id_num, index_name='test_index'):
        # 这里thread为1001就代表是修改过的文档
        res = 0
        data = self.gen_data(id_num, thread_num='1001')
        try:
            conn = self.es_conn()
            conn.update(index=index_name, id=id_num, body=data)
            res = 1
        except Exception as err:
            print('ERROR update id=%s: %s' % (id_num, str(err)))
        finally:
            conn.close()
        return res

    def delete_data(self, id_num, index_name='test_index'):
        res = 0
        try:
            conn = self.es_conn()
            conn.delete(index=index_name, id=id_num)
            res = 1
        except Exception as err:
            print('ERROR update id=%s: %s' % (id_num, str(err)))
        finally:
            conn.close()
        return res

    def compare_data(self, stop_times=20, process=0, index_name='test_index'):
        print('\n开始检查上下游es数据一致性，索引[%s]' % index_name)
        # stop_times: 在一开始查询数据量的时候如果下游查询指定的stop_times次数依旧未改变其数据量，
        #             则认为可能是卡住了或者什么问题故会直接返回失败，默认最多查询20次

        def research_datas():
            # 获取并返回主备的总数据
            master_datas = self.show_data(index_name=index_name, host_num=0)
            slave_datas = self.show_data(index_name=index_name, host_num=1)
            return master_datas, slave_datas

        def count_datas():
            master_counts = self.show_data(index_name=index_name, count=1)
            slave_counts = self.show_data(index_name=index_name, host_num=1, count=1)
            return master_counts, slave_counts

        master_count, slave_count = count_datas()
        # 当主备数据量不一致的时候会开始刷新，直到数据量一致再进行下一步对比数据一致性
        while master_count != slave_count:
            cur_times = 0
            old_master_data, old_slave_data = master_count, slave_count
            print('上下游es索引[%s]数据量不一样, 主[%s]条，备[%s]条, 10s后再次查询' % (index_name, master_count, slave_count))
            time.sleep(10)
            master_count, slave_count = count_datas()
            while old_slave_data == slave_count and master_count != slave_count:
                cur_times += 1
                master_count, slave_count = count_datas()
                print('下游es索引[%s]第[%s/%s]次无变化，主[%s]条，备[%s]条, 10s后再次查询'
                      % (index_name, cur_times, stop_times, master_count, slave_count))
                if cur_times >= stop_times:
                    print('下游超过20次查询无变化，故本次数据一致性失败')
                    return ['es', 0]
                time.sleep(10)
        print('\n上下游es数据量一致，开始进行下一步\n')
        master_data, slave_data = research_datas()

        res = 1
        if process <= 1:
            for i in range(len(master_data)):
                num = i + 1
                if master_data[i]['_source'] != slave_data[i]['_source']:
                    print('备第[%s]行数据与主不一致！\n主：%s\n备：%s' %
                          (num, master_data[i]['_source'], slave_data[i]['_source']))
                    res = 0
        else:
            # 开始多进程对比
            process_size_list = []
            each_process = int(len(master_data) / process)
            succ_times = multiprocessing.Manager().Value('i', 0)
            for i in range(process):
                start_num = i * each_process
                end_num = start_num + each_process
                if i == process - 1:
                    end_num = len(master_data)
                cur_list = [start_num, end_num]
                process_size_list.append(cur_list)

            def single_process(process_num, shared_num):
                succ = 1
                show_num = process_num + 1
                cur_size_list = process_size_list[process_num]
                cur_start_num, cur_end_num = cur_size_list[0], cur_size_list[1]
                print('process_%s: 开始检查主备第[%s - %s]行数据' % (show_num, cur_start_num, cur_end_num))
                time.sleep(1)
                for i in range(cur_start_num, cur_end_num):
                    if master_data[i] not in slave_data:
                        print('备第[%s]行数据不存在主上！\n%s' %
                              (i, slave_data[i]['_source']))
                        succ = 0
                print('process_%s: 开始检查完毕' % show_num)
                shared_num.value += succ

            pl = []
            for i in range(process):
                p = multiprocessing.Process(target=single_process, args=(i, succ_times,))
                pl.append(p)
                p.start()
            for i in pl:
                i.join()
            if succ_times.value == process:
                print('本次对比数据一致性成功')
                res = 1
            else:
                res = 0
        return ['es', res]
