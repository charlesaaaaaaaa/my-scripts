* 该脚本有三个文件组成。
  * install.sh是用来配置通用配置参数的脚本，里面的配置项可以根据自己的情况来修改，默认的只是用来做示范的。
  * install.json 是集群的配置文件，可以根据自己的需求往上面添加或者减少节点。
  * pgx_install.py 就是脚本的主体。要传递的参数可以通过 `python3 pgx_install.py --help` 来查看
    * 示例：python3 pgx_install.py --type=pgxz --config=install.json --defbase=base-path --defuser=charles --package=tbase_bin_v2.0.tgz --opt=i
    * --type 有三个选项，分别是pgxc pgxl pgxz
    * --config 集群的配置文件, 默认install.json
    * --defbase 集群的base目录
    * --defuser 集群的默认linux用户
    * --package 集群的二进制包，要编译完成后的
    * --opt 有 `i` 和 `c`选项，i是install安装集群，c是clean清楚集群
## 注意：
* pgxl 9.5版本，在140上部署gtm组件后，gtm主节点会报以下错误，导致集群安装失败：(后面把这一个gtm组件改放在125上了。)
  * 而且pgxl因为过老了，也许久没有人进行更新维护，很多问题都没人去解决了。所以只能避免吧，网上现在几乎是找不到pgxl这个问题的解决方案了。有人提起但是没人解答。
  * 如果在部署dn备节点的时候出现对应dn主断开连接，去gtm主的log里面看有没有这些日志，有的话就是其中的gtm备出问题了，要把gtm备换到其它服务器上
```
4:717215488:2022-06-09 13:56:58.123 CST -WARNING:  No transaction handle for gxid: 60000
LOCATION:  GTM_GXIDToHandle_Internal, gtm_txn.c:280
5:717215488:2022-06-09 13:56:58.123 CST -WARNING:  Invalid transaction handle: -1
LOCATION:  GTM_HandleToTransactionInfo, gtm_txn.c:400
1:706725632:2022-06-09 13:56:58.132 CST -LOG:  could not receive data from client: Bad file descriptor
LOCATION:  pq_recvbuf, pqcomm.c:524
2:706725632:2022-06-09 13:56:58.132 CST -FATAL:  Expecting a startup message, but received ▒
LOCATION:  GTM_ThreadMain, main.c:1100
3:706725632:2022-06-09 13:56:58.132 CST -LOG:  could not send data to client: Bad file descriptor
```

