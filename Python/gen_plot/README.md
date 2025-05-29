# 这个脚本是用来生成折线统计图的
* 命令示例
  * `python3 matplot.py --grep "] thds:" --awk_line 9 --x_awk_line 2 --input_dir pro1/oltp_read_write/ --title read_write --output ./1.3.3_1comp_read_write.png`
```shell
[kunlun@klustron-test5 sysbench_test]$ python3 matplot.py --help
usage: matplot.py [-h] [--grep GREP] [--awk_line AWK_LINE]
                  [--x_awk_line X_AWK_LINE] [--input_dir INPUT_DIR]
                  [--expect_datasize EXPECT_DATASIZE] [--title TITLE]
                  [--ylabel YLABEL] [--xlabel XLABEL] [--output OUTPUT]

展示折线统计图的小脚本

optional arguments:
  -h, --help            show this help message and exit
  --grep GREP           使用grep命令，如--grep "] thds:" == grep "] thds:"
  --awk_line AWK_LINE   awk第几列数据
  --x_awk_line X_AWK_LINE
                        这个是x轴的标签数据，用文件里面的指定列展示，不指定就是从1到最大数据量展示
  --input_dir INPUT_DIR
                        放原始数据文件的目录
  --expect_datasize EXPECT_DATASIZE
                        预期中数据文件应该存在多少行数据, 超过或者少于该数会报错，不指定则不会有该检测步骤
  --title TITLE         折线统计图的标题
  --ylabel YLABEL       折线统计图的y轴标签名
  --xlabel XLABEL       折线统计图的s轴标签名
  --output OUTPUT       把图片输出到什么路径下, 默认为`input_dir`/`title`.png
```
## 参数
* --grep 就是要指定要匹配的行
* --awk_line 这个是指定文件的那一列为数据列
* --x_awk_line 这个是指定文件的那一列为x轴标签数据列
* --input_dir 从指定文件夹里面读取数据文件，默认./result
* --expect_datasize 预期应该有几行数据，超过或者少于会报错，可以不指定
* --title 折线统计图的标题, 默认test
* --ylabel 折线统计图的y轴标签名，默认‘Q P S’
* --xlabel 折线统计图的s轴标签名，默认'time'
* --output 把图片输出到对应文件下，默认为`--input_dir`/`--title`.png
## 备注
* 该脚本目前只能对数据以列的形式展示的文件生效，如sysbench测试输出的那些内容
  * 以表格的形式展示的暂时不支持
