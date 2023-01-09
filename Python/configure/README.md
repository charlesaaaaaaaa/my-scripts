* 该文件是用来配置集群参数的。
* 有两个配置文件:
  * 一个是`configure.json`
    * 这个是用来指定配置参数的文件。分了三个部分，一个是计算节点的配置参数，另外两个分别是data和meta-data节点的配置参数。
    * 里面有几个默认的参数，是做个示范的。可以自己往上添加，只要符合json语法,参数名和值范围是正确的就行,后期如果有时间会考虑改成YAML格式，因为YAML语法更简洁且可以注释
  * 另一个是`install_xc.json` 
    * 这个是用来指定要配置的`计算节点`参数
    * 至于meta节点和存储节点会自动在`计算节点的系统表`里找，所以不用再加上这两个节点的参数
* 脚本主体是congfigure.py,可以通过`python3 configure.py --help` 来查看需要传递什么参数
  * --defuser 集群的使用者，前提是这个用户要在`所有计算节点做好了免密互信`,就是不用密码可以直接登录对应的服务器
  * --version 计算节点的版本,默认0.9.3，如果是其它的就要指定
  * --install 集群的json配置文件,如 install.json
  * --config  集群配置的文件，如configure.json
  * --component 三个参数:
    * `all` 代表修改计算节点、元数据节点和存储节点
    * `server` 只修改计算节点
    * `storage` 只修改元数据节点和存储节点
  
  * 示例：`python3 configure.py --version 1.1 --defuser charles --install install_xc.json --config configure.json --component all`
