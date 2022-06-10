这个是用来记录我在用pgxz/pgxc/pgxl三个数据库时遇到的错误，及解决方法。

## 超过最大prepare 事务数：
* 一般这个只有在pgxl才有(pgxz,pgxc都没有)，pgxl默认的max_prepared_transactions 数量太小，只有10
* 一般情况下这个参数是要大于max_connections这个参数的才不会有该错误。

## Failed to get pooled connections
这个问题的原因是pgxz在运行完高并发的测试后，后台的idle（闲置进程）过多且要很久之后才会自动杀掉。
**解决方式如下：**
* 1. 可以直接kill掉所有的postgres idle进程
  * `ps -ef | grep postgres | grep idle | awk '{print $2}' | sed '$d' | xargs kill -9`
  * 但这个要每次测试一次性能后 所有的cn节点和dn节点及其备节点所在的服务器 都要kill一次，很麻烦
* 2. 在配置文件设置idle超时自动杀掉参数。
  * 在pg14就加入了一个 `idle_session_timeout` 这个参数，以ms计, 为0代表禁用该功能。但当前的pgxz（tbase）用的是比较老的pg版本，所以没有这个参数。之所以提出来是因为想记录一下这个问题当前版本的pg的解决方案
  * 但这个参数也有一个问题，如果只是普通登录上数据库，超过这个时间没有动作也会被断掉当前的会话。所以如果是为了测试是可以用这个参数的，但是如果只是正常登录数据库进行操作就不要用这个参数了

