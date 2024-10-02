#!/bin/bash
 
# 获取所有符合条件的文件
files=$(ls vobd* vmkwarning* vmkernel* hostd* vpxa* vsanmgmt* 2> /dev/null)
 
# 检查是否有符合条件的文件
if [ -z "$files" ]; then
    echo "当前目录下没有匹配的文件"
    exit 1
fi
 
# 处理每个文件，按前缀分类合并
for file in $files; do
    # 提取前缀作为目标文件名 (如 a.txt 从 a.txt.FRAG-00001)
    base_filename=$(echo "$file" | awk -F '.' '{print$1}')
 
    # 如果目标文件不存在，先创建空文件
    mkdir -p tdlog
    cat /dev/null > ./tdlog/"$base_filename.all"
 
 
    # 将当前文件的内容追加到目标文件中
    cat "$file" >> ./tdlog/"$base_filename.all"
    #rm -f $file
done
 
echo "所有文件已根据前缀合并完成！"