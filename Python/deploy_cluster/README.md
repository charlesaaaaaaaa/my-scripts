* python3 deploy_cluster.py --help
```
usage: deploy_cluster.py [-h] [--config CONFIG] [--user USER]
                         [--cloudnative_version CLOUDNATIVE_VERSION]
                         [--product_version PRODUCT_VERSION]
                         [--extra_site EXTRA_SITE]
                         [--downloadsite DOWNLOADSITE]
                         [--downloadtype DOWNLOADTYPE]

deploy klustron

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG       KunlunBase deploy config file, default value =
                        "deploy-config.json"
  --user USER           KunlunBase user
  --cloudnative_version CLOUDNATIVE_VERSION
                        cloudnative version
  --product_version PRODUCT_VERSION
                        KunlunBase version
  --extra_site EXTRA_SITE
  --downloadsite DOWNLOADSITE
                        [internal]|[public]|[release]
  --downloadtype DOWNLOADTYPE
                        [release]|[debug]
```

== 选项参数
* `--config`, 就是我们的集群的配置文件
* `--user`, 这里的user是我们涉及的所有服务器上都通用的user
  * 且要有ssh免密互信
* `--cloudnative_version` 这个是集群部署脚本的branch版本，一般测试的话是`main`
* `--product_version` 集群的版本，就是集群各个组件是用的什么版本的
* `--downloadsite` 组件包的下载地址
  * `internal` 内部下载站
  * `public` 外部公共下载站，“http://zettatech.tpddns.cn:14000/”
  * `release` 外部已发布下载站 
* `--downloadtype` 下载包的类型，是release版本还是debug版本
  * 如果`--downloadsite`为release这里就不用赋值了
* `--extra_site` 下载地址的额外部分
  * 这个选项是只在测试的时候用得上。
  * 示例1. 如`--downloadsite`==`public`，`--downloadtype`==`release`
    * 则这时的下载站网址是`http://zettatech.tpddns.cn:14000/dailybuilds/enterprise/`
  * 如果当天的包全出问题，要退回前一天，则可以用上这个选项
    * 以示例1为例且假设今天是2024.1.12，回退到前一天的完整下载站地址如下所示
      * `http://zettatech.tpddns.cn:14000/dailybuilds/enterprise/archive/2024-01-11/`
    * 而相比原来的地址，多出来的部分就是`archive/2024-01-11/`
    * 则该选项的值是 `archive/2024-01-11/`

## 其它用法：
* 如果当天的包不是所有包都有问题的
  * 则可以把这个包用wget或者curl下载到当前目录下或者./tmp_download(如果有这个目录的话)下
  * 当检测到这个包存在的时候会自动跳过
* 如果已经用该脚本部署过，则下载使用该脚本，如果需要更新的版本，则直接删除./tmp_download目录或者清空该目录就行
