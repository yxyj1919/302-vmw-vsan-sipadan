
#!/bin/bash
 
# 获取所有符合条件的文件 *.txt.FRAG-*
files=$(ls *.txt.FRAG-* 2> /dev/null)
 
# 检查是否有符合条件的文件
if [ -z "$files" ]; then
    echo "当前目录下没有匹配的 *.txt.FRAG-* 文件"
    exit 1
fi
 
# 处理每个文件，按前缀分类合并
for file in $files; do
    # 提取前缀作为目标文件名 (如 a.txt 从 a.txt.FRAG-00001)
    base_filename=$(echo "$file" | sed 's/\.FRAG-[0-9]*//')
 
    # 如果目标文件不存在，先创建空文件
    if [ ! -f "$base_filename" ]; then
        cat /dev/null > "$base_filename"
    fi
 
    # 将当前文件的内容追加到目标文件中
    cat "$file" >> "$base_filename"
    rm -f $file
done
 
echo "所有文件已根据前缀合并完成！"