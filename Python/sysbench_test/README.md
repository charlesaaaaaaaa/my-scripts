## 运行说明 
* 运行的话直接`python3 sysbench_test.py`
  * 一般我都是晚上写好配置文件直接放后台跑的, 第二天早上来看结果
  * `nohup python3 sysbench_test.py > log.log 2>&1 &`
* 配置文件我是直接写死在`./conf/config.conf`里面，所以跑之前改下这个文件

## 结果说明
* 目前每个case都在`"./pro%d" % num`目录里面
  * 这里的`num`是根据配置文件里面配置的node数量有关
  * 如配置了一个node，就会产生`./pro1`一个目录
  * 配置三个，就会产生`./pro1`,`./pro2`,`./pro3`三个目录
* 可以用`./util/result.sh`这个文件来快速整合查看这个结果
  * 这个脚本主要是我在早上出结果能马上整合并生成我们trac的ticket格式直接贴结果贴里面
  * 这个文件$1是目录位置，如`./pro1`,`./pro2`
  * $2是选择查看`tps`还是`qps`.
  * 示例：`./util/result.sh ./pro1 qps`

```
这个是只跑了oltp_write_only这个case，所以只有这个结果
queries
|| case || 100 || 200 || 300 || 400 || 500 || 600 || 700 || 800 || 900 || 1000 ||
|| oltp_write_only || 16854.87 || 12936.58 || 9492.39 || 9007.89 || 9108.93 || 9122.03 || 9089.29 || 8612.46 || 8117.95 || 8445.59 ||
```

# 配置说明
## database_info
* 这个是我们数据库的信息
  * `host`和`port`这边，如果要测多个节点，则可以写成如下形式
  * 假设有三个节点要测，且当前测100并发，则三个节点各分到 33，33，34三个并发同时跑
  * 如果要三个节点都跑100并发，则配置文件这里写成300就行
```
host = 192.168.0.18, 192.168.0.19, 192.168.0.20
port = 58881, 58881, 58881
``` 
* `db` 这里就是要测的db名
* `driver`就是对应的驱动，目前就只有`pgsql`|`mysql`
  * 确认安装的sysbench有pg驱动，有些机器上只有mysql驱动

## necessary_info
* `tables` 表数目
* `table_size` 每个表的size
* `time` 每个测试的运行时间，单位s
* `sleeptime` 测试成功后的休息时间，单位s
* `prepare_thread` 灌数据的thread数
* `threads` 压测时要跑的并发数，一般有多个
  * 示例 `threads = 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000` 代表每个配置的case要压100 到 1000且步长100的并发数
* `case` 要压的case，确认好当前机器有对应的case文件，case顺序和数目可以随意。
  * 示例 `case = oltp_point_select, oltp_insert, oltp_update_index, oltp_update_non_index, oltp_read_only, oltp_read_write, oltp_write_only`
  * 示例代表要压七个case，case去掉文件名的后缀`.lua`。跑的时候会在`./pro%d`目录下生成对应case名的目录，详细结果都在这下面
  * 示例的逻辑是先跑完 `oltp_point_select` 100到1000的并发测试，然后再轮到`oltp_insert`...... 跑完算 一轮
* `action` 这个是对应sysbench的动作。有[prepare]|[run]|[cleanup], 分别对应 [灌数据]|[跑压测]|[消除数据]
  * 如`case`, 顺序和动作及其数据可随意调整，每填一个就会跑一轮
  * 示例`cleanup, prepare, run` 先`清除数据`(如果有的话)， 再`灌数据`， 再`跑一轮压测`
  * `prepare, run`, `cleanup, prepare, run, run, run`, `cleanup, prepare` 这样都是可以的, 随意填写

## other_info
* 这个是非必要的sysbench选项，自行增加删减
* 如--rand-type=uniform, 就写成rand-type = uniform
* 目前我知道的就是要加上rand-type db-ps-mode这两个选项，当时winter让我加的
