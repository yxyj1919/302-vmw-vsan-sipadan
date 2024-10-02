#supportselectpath=$(pwd)

## 定义supportselect
#function supportselect ()
#{

# 日志选择列表
# 日志选择列表
cat << EOF
######################################################################################
#          _____         _   _                                 _                     #
#         / ____|  /\   | \ | |     /\                        | |                    #
#  __   _| (___   /  \  |  \| |    /  \   _ __  _   ___      _| |__   ___ _ __ ___   #
#  \ \ / /\___ \ / /\ \ | . \` |   / /\ \ | \'_ | | | \ \ /\ / / '_ \ / _ \ '__/ _ \  #
#   \ V / ____) / ____ \| |\  |  / ____ \| | | | |_| |\ V  V /| | | |  __/ | |  __/  #
#    \_/ |_____/_/    \_\_| \_| /_/    \_\_| |_|\__, | \_/\_/ |_| |_|\___|_|  \___|  #
#                                                __/ |                               #
#                                               |___/                                #
######################################################################################
EOF
echo "==================================================="
echo "   搜索日志中，请等待......"
echo "   Searching log bundle, please wait a moment..."
echo "=================================================="
echo "Please Select:"
touch t1
find . -name commands -type d|sed -e 's/\/commands$//g'|while read host; do echo ${host##*/};done > t1 #统计所有vm-support数量
num=$(cat t1|wc -l)  #统计所有vm-support数量到临时文件t1
for i in `seq 1 $num`;do
	t2=$(echo $i"p")
	t3=$(cat t1 |sed -n ''$t2'') #从vm-support文件中读取指定行
	echo $i")" $t3    #显示序列号和vm-support名称
	echo "$i')' $t3" >> t4 #导出序列号和vm-support的临时文件t4
done
echo "0) Quit"

read -p "Enter selection [0-$num] >" select #等待用户输入选项

#if [[ $select =~ ^[0-'$num']$ ]]; then
	if [[ $select == 0 ]]; then #选项为0的话退出
		echo "Program terminated"
		rm t1 
		rm t4
		exit;
	else
		echo "选择的项目为:$select"
		t5=$(echo $select"p")
		t6=$(cat t4 |sed -n ''$t5''|awk '{print$2}') #选项不为0的话，从t4文件中截取vm-support名称
		echo "选择的目录为:$t6"
		t7=$(find . -name $t6 -type d) #查找指定vm-support
	#	echo $t7
#		rm t1 
#		rm t4 
		cd $t7 #切换到指定目录
		echo "切换至目录: $(pwd)"
#		main_menu
	fi
cd - > /dev/null
		rm t1 
		rm  t4
cd - > /dev/null
#fi
#}

#supportselect

#设置环境变量
originalpath=$(pwd)
cmdpath=$originalpath/commands
logpath=$originalpath/var/run/log
tdlogpath=$originalpath/var/log/tdlog


 if [ ! -x "$cmdpath" ]; then
   echo -e "没有发现相关目录(c)，请确认当前路径在vm-support根目录下，并且运行td_log。"
#	exit 0
 fi

 if [ ! -x "$logpath" ]; then
   echo -e "没有发现相关目录(l)，请确认当前路径在vm-support根目录下，并且运行td_log。"
#	exit 0
 fi

 if [ ! -x "$tdlogpath" ]; then
   echo -e "没有发现相关目录(t)，请确认当前路径在vm-support根目录下，并且运行td_log。"
#	exit 0
 fi

#创建临时文件夹
findmycat=$(find $originalpath  -name mycat -type d)
if [ -z "$findmycat" ]; then
	echo "临时文件夹不存在，创建新临时文件夹"
	mkdir  $originalpath/mycat;
	mycat=$originalpath/mycat;
	echo $mycat
else
	echo "临时文件夹已经存在"
	rm -r -f $originalpath/mycat
	echo "删除现有临时文件夹成功"
	mkdir  $originalpath/mycat
	mycat=$originalpath/mycat;
	echo $mycat
	echo "创建临时文件夹成功"
fi

#记录SR
SRoriginal=$(echo $originalpath|awk -F "/" '{print $6$7$8$9$10}')
echo ${SRoriginal#*0} >> /users/home10/changw/Tools/backupsipadan/SRrecord
#echo ${SRoriginal#*0} >> /users/home10/changw/Tools/SRrecord
date >> /users/home10/changw/Tools/backupsipadan/SRrecord
#date >> /users/home10/changw/Tools/SRrecord
echo $originalpath >> /users/home10/changw/Tools/backupsipadan/SRrecord
#echo $originalpath >> /users/home10/changw/Tools/SRrecord
whoami >>  /users/home10/changw/Tools/backupsipadan/SRrecord
#whoami >>  /users/home10/changw/Tools/SRrecord
echo -e "\n" >> /users/home10/changw/Tools/backupsipadan/SRrecord
#echo -e "\n" >> /users/home10/changw/Tools/SRrecord
usenum=$(cat /users/home10/changw/Tools/backupsipadan/SRrecord|grep 188|wc -l)
#usenum=$(cat /users/home10/changw/Tools/SRrecord|grep 188|wc -l)

echo -e "\n########################################################################################################################"
echo -e "#                                                                                                                      #"
echo -e "# 		         _____         _   _                                 _                  		       #"
echo -e "#		        / ____|  /\   | \ | |     /\                        | |                                        #"
echo -e "#		 __   _| (___   /  \  |  \| |    /  \   _ __  _   ___      _| |__   ___ _ __ ___                       #"
echo -e "#		 \ \ / /\___ \ / /\ \ | . \` |   / /\ \ | \'_ | | | \ \ /\ / / '_ \ / _ \ '__/ _ \'                     #"
echo -e "#		  \ V / ____) / ____ \| |\  |  / ____ \| | | | |_| |\ V  V /| | | |  __/ | |  __/                      #"
echo -e "#    		   \_/ |_____/_/    \_\_| \_| /_/_   \_\_| |_|\__, | \_/\_/ |_| |_|\___|_|  \___|                      #"
echo -e "#		        / ____(_)               | |            __/ |                                                   #"
echo -e "#		       | (___  _ _ __   __ _  __| | __ _ _ __ |___/                              		       #"
echo -e "#		        \___ \| | '_ \ / _\` |/ _\` |/ _\` | '_ \                                                         #"
echo -e "#  	  	        ____) | | |_) | (_| | (_| | (_| | | | |                                                        #"
echo -e "# 		       |_____/|_| .__/ \__,_|\__,_|\__,_|_| |_|                                                        #"
echo -e "#		                | |                                                                     	       #"
echo -e "#             		        |_|                                                                                    #"
echo -e "#                                                                                                                      #"
echo -e "########################################################################################################################"
echo -e "	 				vSAN Log Analysis Tool		  "
echo -e "			        barracuda point   v1.6  Chang Wang changw@ $usenum "
echo -e " Please access https://confluence.eng.vmware.com/display/china/2+vSAN+Log+Analysis+Tool+-+Sipadan for any feedback."
echo -e "########################################################################################################################"


# 定义main_menu
function main_menu ()
{
echo " 日志路径：$originalpath"
cat << EOF
--------------------------------------------------
|***************vSAN日志分析工具*****************|
|************vSAN Log Analysis Tool**************|
--------------------------------------------------
`echo -e "\033[35m 1)vSAN主机信息分析/vSAN Node Information\033[0m"`
`echo -e "\033[35m 2)vSAN集群信息分析/vSAN Cluster Information\033[0m"`
`echo -e "\033[35m 3)主机日志分析/vSAN Log Analysis\033[0m"`
`echo -e "\033[35m 4)虚拟机/对象分析/VM & Object Analysis\033[0m"`
`echo -e "\033[35m s)重新选择日志包/Select Other Log Bundle\033[0m"`
`echo -e "\033[35m q)退出/Quit\033[0m"`
EOF
read -p "请输入对应选项/Please select：" num1

case $num1 in
    1)
      echo -e "\nWelcome to vSAN主机信息分析主页!!"
      echo -e "Welcome to vSAN Node Information!!\n"
	cd $cmdpath
      main_host_menu
      ;;
    2)
      echo -e "\nWelcome to vSAN集群信息分析主页!!"
      echo -e "Welcome to vSAN Cluster Information!!\n"
	cd $cmdpath
      main_cluster_menu
      ;;
    3)
      echo -e "\nWelcome to vSAN日志分析主页!!"
      echo -e "Welcome to vSAN Log Analysis!!\n"
	cd $tdlogpath
      main_log_menu
      ;;
    4)
      echo -e "\nWelcome to 虚拟机/对象分析主页!!"
      echo -e "Welcome to VM & Object Analysis!!\n"
	cd $cmdpath
      main_vm_menu
      ;;
    s)
#	cd $supportselectpath
#      supportselect
	main_menu
      ;;
    q)
	rm -r $originalpath/mycat
      exit 0
	;;
     *)
        echo "the is fail!!"
	main_menu
esac
}


#main_menu

# 测试函数
function main_test_menu-0001 ()
{
date
uname -a 
}

#定义main_host_menu
function main_host_menu ()
{
cat << EOF
-----------------------------------------------------
|***************vSAN集群信息分析主页****************|
|***************vSAN Node Information***************|
-----------------------------------------------------
`echo -e "\033[35m 1)本节点基本信息/ESXi Basic Information\033[0m"`
`echo -e "\033[35m 2)本节点磁盘状态/Disk Information\033[0m"`
`echo -e "\033[35m 3)本节点磁盘路径/控制卡信息/Disk Path & Raid Card Information\033[0m"`
`echo -e "\033[35m 4)本节点磁盘组拥堵状态/Congestion Status\033[0m"`
`echo -e "\033[35m 5)本节点活动网卡丢包统计/Network Card Status\033[0m"`
`echo -e "\033[35m 6)未完成\033[0m"`
`echo -e "\033[35m A)运行所有选项/Run All\033[0m"`
`echo -e "\033[35m b)返回主菜单/Back to Home Page\033[0m"`
EOF
read -p "请输入对应产品的数字/Please select：" num2
case $num2 in
    1)
	main_host_0001
	main_host_menu
	;;
    2)
        main_host_0002
        main_host_menu
        ;;
    3)
        main_host_0003
        main_host_menu
        ;;
    4)
        main_host_0004
        main_host_menu
        ;;
    5)
        main_host_0005
        main_host_menu
        ;;
    6)
        main_host_menu
        ;;
    A)
        main_host_0001 >> $originalpath/sipadan-host.log
        main_host_0002 >> $originalpath/sipadan-host.log
        main_host_0003 >> $originalpath/sipadan-host.log
        main_host_0004 >> $originalpath/sipadan-host.log
        main_host_0005 >> $originalpath/sipadan-host.log
	mv $originalpath/sipadan-host.log $originalpath/sipadan-host-`date +%Y%m%d%H%M`.log
	echo "文件已经导出至/Log has been exported to $originalpath "
	main_host_menu
        ;;
    b)
      clear
      main_menu
      ;;
    *)
      echo "the is fail!!"
      main_host_menu
esac
}


#定义main_host_0001
function main_host_0001 ()
{
clear
echo "============================================";
echo "1.本vSAN节点基本信息/Node Basic Information";
echo -e "============================================\n";
buildnum=$(cat vmware_-vl.txt|grep build|awk '{print$4}')
build=$(cat vmware_-vl.txt|grep Update)
hostuuid=$(more localcli_vsan-cluster-get.txt|grep "Local Node UUID:"|sed -e "s/Local Node UUID://g"); #本节点vSAN UUID
hostname=$(cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt|grep -C6 -F "HOSTNAME" |grep $hostuuid -A9|grep content| sed -e 's/\"content\"://g' | awk '{print $2}' | sed -e 's/[\",\},\,]//g'); #主机名
hostmagmtip=$(cat esxcfg-vmknic_-l.txt |grep "Management Network"|awk '{print$5}'); #管理口地址
netifs=$(cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt|grep -C6 -F "NET_INTERFACE" |grep $hostuuid -A9 |grep content | sed -e "s/[],\[,\\,\",\,]//g" | awk '{print "vSAN VMK IP: " $3 "\n vSAN VMK Subnet: " $4"\n vSAN Agent Multicast Address: " $5 "\n vSAN Master Multicast Address: " $6}') #vSAN地址
echo -e " Host UUID:" $hostuuid" \n Host Name: $hostname \n Management Network Information: $hostmagmtip \n vSAN Network Information:\n $netifs \n ESXi Version: $build $buildnum\n"
}



#定义main_host_0002
function main_host_0002 ()
{
clear
echo "======================================";
echo "2.本vSAN节点磁盘状态/Disk Information";
echo -e "=====================================\n";
more localcli_vsan-storage-list.txt | awk 'BEGIN{printf "%40s | %6s | %40s | %12s | %10s\n","Device","Is_SSD","VSAN_DG_UUID","Used_by_host","In_CMMDs"}/Device:/{naa=$2}/Is SSD:/{ssd=$3}/VSAN Disk Group UUID:/{dguuid=$5}/Used by this host/{used=$5}/In CMMDS:/{printf "%40s | %6s | %40s | %12s | %10s\n",naa,ssd,dguuid,used,$3}' | sort -k5
echo -e "\n"
}


#定义main_host_0003
function main_host_0003 ()
{
clear
echo "============================================================";
echo "3.vSAN磁盘路径/控制卡信息/Disk Path & Raid Card Information"
echo -e "===============================i==========================\n";
echo -e "磁盘路径映射关系/Disk Path\n"
for vsandisk in $(more localcli_vsan-storage-list.txt |grep Device|awk '{print$2}')
	do diskpath=$(grep $vsandisk esxcfg-mpath_-b.txt  -A1 |awk '{print$1}'|xargs -n 2)
	raidcard=$(grep $vsandisk  esxcfg-mpath_-b.txt -A1 |grep Target|awk '{print$1}'|awk -F ':' '{print$1}'|sort|uniq)
	echo $diskpath
	echo $raidcard >> $originalpath/mycat/tmp1.txt
done
echo -e "\n控制卡信息/Raid Card Information \n"
for raidcardname in $(cat $originalpath/mycat/tmp1.txt|sort|uniq)
	do raidcardtype=$(grep $raidcardname localcli_storage-core-adapter-list.txt |awk  '{for (i=6;i<=NF;i++) {printf$i" "}printf "\n" }')
	echo "控制卡名称/Name: $raidcardname"
	echo "控制卡型号/Model: $raidcardtype"
	echo -e "\n"
done
rm $originalpath/mycat/tmp1.txt
}


#定义main_host_0004
function main_host_0004 ()
{
clear
echo "=======================================";
echo "4.vSAN磁盘组拥堵状态/Congestion Status";
echo -e "======================================\n";

echo -e "检查每个磁盘组拥堵指数/Checking Congestion Status for Per DG\n"
# 检查拥堵指数
for ssd in $(cat localcli_vsan-storage-list.txt |grep "Group UUID"|awk '{print $5}'|sort -u);do echo $ssd; automagicallyrun vsish -c vsi_traverse_-s.txt -e get /vmkModules/lsom/disks/$ssd/info | grep -i congest ;done;

# 检查系统版本
buildversion=$(cat vmware_-vl.txt |grep build|awk  '{print$3}')

if [ "$buildversion" == "6.5.0" ]; then
	 echo -e "\n 检查vSAN 6.5 每个磁盘组PLOG/LLOG /Checking vSAN 6.5 PLOG/LLOG"

	#vSAN6.5 PPLOG日志
	for ssd in $(cat localcli_vsan-storage-list.txt |grep "Group UUID"|awk '{print $5}'|sort -u);
	do echo $ssd; llogTotal=$(automagicallyrun vsish -c vsi_traverse_-s.txt -e get /vmkModules/lsom/disks/$ssd/info | grep "Log space consumed by LLOG"|awk -F \: '{print $2}'); plogTotal=$(automagicallyrun vsish -c vsi_traverse_-s.txt -e get /vmkModules/lsom/disks/$ssd/info|grep "Log space consumed by PLOG"|awk -F \: '{print $2}');llogGib=$(echo $llogTotal |awk '{print $1 /  1073741824}');plogGib=$(echo $plogTotal |awk '{print $1 / 1073741824}');allGibTotal=$(expr $llogTotal \+ $plogTotal|awk '{print $1 / 1073741824}');echo $ssd;echo "    LLOG consumption: $llogGib";echo "    PLOG consumption: $plogGib";echo "    Total log consumption: $allGibTotal"; done;

	else
        echo -e "\n检查vSAN 6.2 每个磁盘组PLOG/LLOG /Checking vSAN 6.2 PLOG/LLOG\n"
	#vSAN6.2 PPLOG日志
	for ssd in $(cat localcli_vsan-storage-list.txt |grep "Group UUID"|awk '{print $5}'|sort -u);do llogTotal=$(jvc -c "get /vmkModules/lsom/disks/$ssd/info" |grep "Log space consumed by LLOG"|awk -F \: '{print $2}');plogTotal=$(jvc -c "get /vmkModules/lsom/disks/$ssd/info"|grep "Log space consumed by PLOG"|awk -F \: '{print $2}');llogGib=$(echo $llogTotal |awk '{print $1 /  1073741824}');plogGib=$(echo $plogTotal |awk '{print $1 / 1073741824}');allGibTotal=$(expr $llogTotal \+ $plogTotal|awk '{print $1 / 1073741824}');echo $ssd;echo "    LLOG consumption: $llogGib";echo "    PLOG consumption: $plogGib";echo "    Total log consumption: $allGibTotal";done;
fi
echo -e "\n"
}

#定义main_host_0005
function main_host_0005 ()
{
clear
echo "===============================================";
echo "5.vSAN节点活动网卡报错统计/Network Card Status";
echo -e "==============================================\n";

for i in $(grep "MTU     Uplinks" esxcfg-vswitch_-l.txt  -A1|grep vmnic|awk '{print$NF}'|sed -e 's/,/ /g'|xargs);
do echo -e "$i 的错误记录为：";
grep "NIC statistics for $i:" nicinfo.sh.txt -A24|egrep 'dropped|errors';
echo -e "\n";
done
}


######################################################################################
#定义main_host_0006
#function main_host_0006 ()
#{
#}
######################################################################################
######################################################################################

#定义main_cluster_menu
function main_cluster_menu ()
{
cat << EOF
-----------------------------------------------------
|***************vSAN集群信息分析主页****************|
|*************vSAN Cluster Information**************|
-----------------------------------------------------
`echo -e "\033[35m 1)vSAN集群基本信息/vSAN Cluster Information\033[0m"`
`echo -e "\033[35m 2)vSAN集群所有节点是否是维护状态/Maintenance Mode Status\033[0m"`
`echo -e "\033[35m 3)vSAN集群所有节点磁盘使用率/vSAN Nodes Disks Usage\033[0m"`
`echo -e "\033[35m 4)主机加入集群记录/Joining vSAN Cluster Record\033[0m"`
`echo -e "\033[35m 5)vSAN集群所有节点主机vSAN vmk配置/vSAN Nodes Network Configration\033[0m"`
`echo -e "\033[35m 6)测试\033[0m"`
`echo -e "\033[35m A)运行所有选项/Run All\033[0m"`
`echo -e "\033[35m b)返回主菜单/Back to Home Page\033[0m"`
EOF
read -p "请输入对应选项/Please select：" num3
case $num3 in
#    0)
#        main_test_menu-0001
#        main_cluster_menu
#	;;
    1)
        main_cluster_0001
        main_cluster_menu
        ;;
    2)
        main_cluster_0002
        main_cluster_menu
        ;;
    3)
        main_cluster_0003
        main_cluster_menu
        ;;
    4)
        main_cluster_0004
        main_cluster_menu
        ;;
    5)
        main_cluster_0005
        main_cluster_menu
        ;;
    6)
        main_cluster_menu
        ;;
    A)
        main_cluster_0001 >> $originalpath/sipadan-cluster.log
        main_cluster_0002 >> $originalpath/sipadan-cluster.log
        main_cluster_0003 >> $originalpath/sipadan-cluster.log
        main_cluster_0004 >> $originalpath/sipadan-cluster.log
        main_cluster_0005 >> $originalpath/sipadan-cluster.log
        mv $originalpath/sipadan-cluster.log $originalpath/sipadan-cluster-`date +%Y%m%d%H%M`.log
        echo "文件已经导出至$originalpath 下"
        main_cluster_menu
        ;;
    b)
        clear
        main_menu
        ;;
    *)
        echo "the is fail!!"
	main_cluster_menu
esac
}

#定义main_cluster_0001
function main_cluster_0001 ()
{
clear
echo "================================================";
echo "1.vSAN集群所有节点UUID/vSAN Cluster Information";
echo -e "===============================================\n";
vsanclusteruuid=$(cat localcli_vsan-cluster-get.txt |grep "Sub-Cluster UUID"|awk '{print$3}')
vsanclusternum=$(cat localcli_vsan-cluster-get.txt |grep "Sub-Cluster Member Count"|awk '{print$4}')
echo -e " vSAN Cluster UUID: $vsanclusteruuid \n vSAN Nodes Count: $vsanclusternum \n vSAN Nodes Include："
#cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt|grep -C6 -F "HOSTNAME"|grep -E "uuid|content"|sed 'N;s/\n/ /'|awk -F \" '{print $10": " $4}'|sort #查询所有主机UUID
cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt|grep -C6 -F "HOSTNAME"|grep -E '"uuid"|"health"|"content"'|awk '{print$NF}' |xargs -n 3|sed -e 's/}//g' -e 's/,//g'|awk '{print$3,$1,$2}'|sort 
echo -e "\n"
}


#定义main_cluster_0002
function main_cluster_0002 ()
{
clear
echo "=========================================================";
echo "2.vSAN集群所有节点是否是维护状态/Maintenance Mode Status";
echo -e "========================================================\n";
echo "主机名称/Host		维护状态/Status	维护工作类型/Job Type";

for host in $(cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt|grep -C6 -F "HOSTNAME"|grep -B2 Healthy|grep uuid|awk -F \" '{print $4}');#节点UUID
do hostName=$(cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt|grep -C6 -F "HOSTNAME"|grep $host -A9|grep content|awk -F \" '{print $6}');#主机名称
decomInfo=$(cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt|grep -C6 -F "NODE_DECOM_STATE"|grep $host -A10|grep -E "content"|awk '{print $3 $5}'|sed 's/,$//');#是否进入MM
echo "$hostName		$decomInfo";done|sort
echo -e ""
echo -e "维护状态	    含义"
echo -e "   0		未进入维护模式"
echo -e "   1		已经开始进入维护模式"
echo -e "   3		正在进入维护模式"
echo -e "   6		处于维护模式"
echo -e "\n维护工作类型	      含义"
echo -e "   0		不迁移任何数据"
echo -e "   1		确保数据可访问性"
echo -e "   2		迁移所有数据"
echo -e ""
echo -e "参考文档：KB#2149238"
}


#定义main_cluster_0003
function main_cluster_0003 ()
{
clear
echo "====================================================";
echo "3.vSAN集群所有主机磁盘使用率/vSAN Nodes Disks Usage";
echo -e "===================================================\n";
for hostuuid in $(cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt|grep -C6 -F "HOSTNAME"|grep -B2 Healthy|grep uuid|awk -F \" '{print $4}');  #查询所有主机UUID
	do hostname=$(cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt|grep -C6 -F "HOSTNAME"|grep $hostuuid -A9|grep content|awk -F \" '{print $6}'); #查询所有主机名
	echo -e "\n\nHost Name: $hostname::: Host UUID: $hostuuid\n Disk Name\t\t| Disk UUID\t\t | Disk Usage     | Disk Capacity | Usage Percentage"; #标题行
	cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt|grep -C6 -F '"DISK"'|grep $hostuuid -A9 -B1|egrep "uuid|content" | sed -e 's/\"content\":|\\"uuid\"://g' | sed -e 's/[\",\},\]//g' |awk '{printf $0}' | sed -e 's/dedupScope: [0-9]*/\n/g' -e 's/dedupMetadata: [0-9]*//g' -e 's/isEncrypted: [0-9]//g'|awk '{print $37 " " $2 " " $5 " " $45}'|grep -v ^$|grep -v "^ "|while read disknaa diskuuid diskcap maxcomp;
		do diskcapused=$(cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt|grep -C6 -F '"DISK_STATUS"'|grep $diskuuid -A9|grep content |sed -e 's/[\",\},\]//g' | awk '{print $3}');
		diskperc=$(echo "$diskcapused $diskcap" | awk '{print $1/$2*100}');
			if [ "$maxcomp" != 0 ]; then
			echo -en " $disknaa\t| $diskuuid\t| $diskcapused\t | $diskcap\t | $diskperc%\n";
			fi;
		done
	done
}

#定义main_cluster_0004
function main_cluster_0004 ()
{
clear
echo "===============================================";
echo "4.主机加入集群记录/Joining vSAN Cluster Record";
echo -e "==============================================\n";
#echo $originalpath
cd $tdlogpath
joincluster=$(grep "Added [^ ]* of type CdbObjectNode to CLOMDB" clomd.all |head -1)
if [ -z "$joincluster" ]; then
	echo "没有发现相关记录/No Related Records Found";
else
	echo "发现相关记录/Found Related Records"
	grep "Added [^ ]* of type CdbObjectNode to CLOMDB" clomd.all |awk '{print $1,$4}'> 123321.txt
	cat 123321.txt| while read w1 w2 ;do  echo "$w1,主机/Host $w2 尝试加入集群/tried to join the Cluster"; done
fi
cd $cmdpath
}

#定义main_cluster_0005
function main_cluster_0005 ()
{
clear
echo "===================================================================";
echo "5.vSAN集群所有节点主机vSAN vmk配置/vSAN Nodes Network Configration";
echo -e "==================================================================\n";
cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt|grep -C6 -F "HOSTNAME" | egrep "uuid|hostname" | sed -e 's/\"content\"://g' | awk '{print $2}' | sed -e 's/[\",\},\,]//g' | xargs -n 2 |
for hostuuid in $(cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt|grep -C6 -F "HOSTNAME"|grep -B2 Healthy|grep uuid|awk -F \" '{print $4}');
	do hostname=$(cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt|grep -C6 -F "HOSTNAME"|grep $hostuuid -A9|grep content|awk -F \" '{print $6}');
	netifs=$(cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt|grep -C6 -F "NET_INTERFACE" |grep $hostuuid -A9 |grep content | sed -e "s/[],\[,\\,\",\,]//g" | awk '{print "vSAN VMK IP: " $3 "\n vSAN VMK Subnet: " $4"\n vSAN Agent Multicast Address: " $5 "\n vSAN Master Multicast Address: " $6}');
	echo -en "\nHost Name: $hostname ::: Host UUID: $hostuuid\n $netifs\n"; 
done
}

######################################################################################
#定义main_XXXXX_0006
#function main_XXXXX_0006 ()
#{
#}
######################################################################################
######################################################################################



##定义main_log_menu
function main_log_menu ()
{
cat << EOF
-----------------------------------------------------
|***************vSAN日志信息分析主页****************|
|****************vSAN Log Analysis******************|
-----------------------------------------------------
`echo -e "\033[35m 1)主机启动日期/Bootup History\033[0m"`
`echo -e "\033[35m 2)主机进入维护模式记录/Maintenance Mode History\033[0m"`
`echo -e "\033[35m 3)主机Power-On Reset记录/Power-On Reset Record\033[0m"`
`echo -e "\033[35m 4)检查lsi_mr3驱动事件/Lsi_mr3 Event Record\033[0m"`
`echo -e "\033[35m 5)检查SCSI Code事件/SCSI Code Event Record\033[0m"`
`echo -e "\033[35m 6)主机无响应记录/Hostd non-responsive Record\033[0m"`
`echo -e "\033[35m 7)主机磁盘高延时记录/Disks High Latency Record\033[0m"`
`echo -e "\033[35m 8)检测SSD corruption事件/SSD Corruption Record\033[0m"`
`echo -e "\033[35m 9)测试\033[0m"`
`echo -e "\033[35m A)运行所有选项/Run All\033[0m"`
`echo -e "\033[35m b)返回主菜单/Back to Home Page\033[0m"`
EOF
read -p "请输入对应选项/Please select：" num3
case $num3 in
#     0)
#         main_test_menu-0001
#         main_log_menu
#         ;;
     1)
         main_log_0001
         main_log_menu
         ;;
     2)
         main_log_0002
         main_log_menu
         ;;
     3)
         main_log_0003
         main_log_menu
         ;;
     4)
         main_log_0004
         main_log_menu
         ;;
     5)
         main_log_0005
         main_log_menu
         ;;
     6)
         main_log_0006
         main_log_menu
         ;;
     7)
         main_log_0007
         main_log_menu
         ;;
     8)
         main_log_0008
         main_log_menu
         ;;
     9)
         main_log_0009
         main_log_menu
         ;;
    A)
        main_log_0001 >> $originalpath/sipadan-log.log
        main_log_0002 >> $originalpath/sipadan-log.log
        main_log_0003 >> $originalpath/sipadan-log.log
        main_log_0004 >> $originalpath/sipadan-log.log
        main_log_0005 >> $originalpath/sipadan-log.log
        main_log_0006 >> $originalpath/sipadan-log.log
        main_log_0007 >> $originalpath/sipadan-log.log
        main_log_0008 >> $originalpath/sipadan-log.log
        main_log_0009 >> $originalpath/sipadan-log.log
        main_log_0010 >> $originalpath/sipadan-log.log
        mv $originalpath/sipadan-log.log $originalpath/sipadan-log-`date +%Y%m%d%H%M`.log
        echo "文件已经导出至$originalpath 下"
        main_log_menu
        ;;
     b)
         clear
         main_menu
         ;;
     *)
        echo "the is fail!!"
	main_log_menu
esac
}


#定义main_log_0001
function main_log_0001 ()
{
clear
cd $logpath
echo "===============================";
echo "1.主机重启记录/Bootup History";
echo -e "===============================\n";
#originalpath=$(pwd)
#srpath=${originalpath%/*}
#cd $srpath/var/run/log
grep boot vmksummary*|grep Host
#grep boot vmksummary*
cd $tdlogpath
}



#定义main_log_0002
function main_log_0002 ()
{
#originalpath=$(pwd)
#srpath=${originalpath%/*}
#cd $srpath/var/run/log
clear
echo "================================================";
echo "2.主机进入维护模式记录/Maintenance Mode History";
echo -e "===============================================\n";
grep "vob.user.maintenancemode.entering" vobd.* |grep GenericCorrelator|awk '{print $1,$4}'|sort|uniq|while read i ii;do echo "主机于/Host ${i%.*}  尝试进入维护模式/tried to enter MM:$ii";done
echo -e ""
grep "vob.user.maintenancemode.entered" vobd.* |grep GenericCorrelator|awk '{print $1,$4}'|sort|uniq|while read i ii;do echo "主机于/Host ${i%.*}  进入了维护模式/had entered in MM:$ii";    done
echo -e ""
grep "vob.user.maintenancemode.exit" vobd.* |grep GenericCorrelator|awk '{print $1,$4}' |sort|uniq|while read i ii;do echo "主机于/Host ${i%.*}  退出维护模式/exited MM:$ii";done
echo -e ""
}

#定义main_log_0003
function main_log_0003 ()
{
clear
echo "===============================================";
echo "3.主机Power-On Reset记录/Power-On Reset Record";
echo -e "==============================================\n";
vobdlogstart=$(head -n 2 vobd.all |grep -v vobd|awk '{print$1}')
vobdlogend=$(tail -n 1 vobd.all |awk '{print$1}')
echo "vobd日志开始时间: $vobdlogstart";
echo "vobd日志结束时间: $vobdlogend";
echo -e "\n"

echo -e "主机在下列时间段发生Power-On Rest/By Date\n"
grep "Power-on Reset occurred" vobd.all |awk '{print$1}'|awk -F ':' '{print$1}'|sort|uniq -c
echo -e "\n"
echo "发生次数/Count	磁盘ID/NaaID";
cat vobd.all|grep "Power-on Reset occurred"|awk '{print $NF}'|sort|uniq -c
}

#定义main_log_0004
function main_log_0004 ()
{
clear
echo "===========================================";
echo "4.检查lsi_mr3驱动事件/Lsi_mr3 Event Record";
echo -e "==========================================\n";

#cd $tdlogpath
vmklogstart=$(head -n 2 vmkernel.all |grep -v vmkernel|awk '{print$1}')
vmklogend=$(tail -n 1 vmkernel.all |awk '{print$1}')
echo "vmkernel日志开始时间: $vmklogstart";
echo "vmkernel日志结束时间: $vmklogend";
echo -e "\n"

echo "发生次数/Count	事件ID/Event ID";
cat vmkernel.all| grep lsi_mr3 |grep "event code" |grep -v Initialized |awk '{print $4,$5,$NF}'|sort|uniq -c
echo -e "\n参考链接/Reference"
echo -e "https://www.thomas-krenn.com/de/wiki/MegaRAID_Event_Messages"
}

#定义main_log_0005
function main_log_0005 ()
{
clear
echo "=======================================";
echo "2.SCSI Code 统计/SCSI Code Event Record";
echo -e "======================================\n";
grep naa $cmdpath/localcli_storage-core-device-list.txt |grep -v D|sed -e 's/:$//g'|while read disk; do grep "ScsiDeviceIO" $tdlogpath/vmkernel.all |grep Cmd|grep -v "D:0x2 P:0x0 Valid sense data: 0x5 0x20"|grep -v "D:0x2 P:0x0 Valid sense data: 0x5 0x24"|grep $disk|awk '{print$15,$16,$17,$18, $19, $20,$21,$22,$23 }'|sed -e 's/.$//g'|sort|uniq -c|while read num event;do echo "磁盘名称/Disk Name:$disk 事件/Event:$event 数量/Count:$num" ; done;done
}


#定义main_log_0006
function main_log_0006 ()
{
clear
echo "=============================================";
echo "6.主机无响应记录/Hostd non-responsive Record";
echo -e "===========================================\n";
hostdhung=$(grep "hostd detected to be non-responsive" vmkernel.all)
if [ -z "$hostdhung" ]; then
	echo -e "没有发现相关记录/No Related Records Found\n";
else
	echo -e "主机发生主机无响应/Found Related Record:\n"
	echo -e " $hostdhung \n"
fi
}


#定义main_log_0007
function main_log_0007 ()
{
clear
echo "===============================================";
echo "7.主机磁盘高延时记录/Disks High Latency Record";
echo -e "=============================================\n";
echo -e "主机磁盘高延时记录（按时间段统计）/ By Time:\n "
echo -e "    时间段/Time	次数/Count "
grep esx.problem.scsi.device.io.latency.high vobd.all |awk '{print$1}'|awk -F ':' '{print$1}'|sort|uniq -c|while read num time; do echo " $time		$num"; done
echo -e "\n主机磁盘高延时记录（按NAAID统计）/ By NaaID:\n "
echo -e "    NAAID			次数/Count "
grep esx.problem.scsi.device.io.latency.high vobd.all |awk '{print$6}'|sort|uniq -c|while read num2 lun ; do echo " $lun		$num2"; done
echo -e "\n最大延时时间（超过500000微秒）/ Max Latency larger than 0.5 sec:"
grep esx.problem.scsi.device.io.latency.high vobd.all|awk '{print$6}'|sort|uniq|while read naa;
	#do echo $naa|
	do grep esx.problem.scsi.device.io.latency.high vobd.all|grep $naa |awk '{print$20}'|sort|uniq|while read lat;
		#do if [ "$(expr length $lat)" -ge 6 ]; then
		do if [ "$lat" -ge 500000 ]; then
		#echo -e "\n$naa \n磁盘延时高于0.5秒，达到: $($lat/100000) 秒"
		latsec=$(echo "scale=6;$lat/1000000" | bc)
		echo -e "\n$naa \n磁盘延时高于0.5秒，达到: $latsec 秒"
		echo "对应日志:"
		grep esx.problem.scsi.device.io.latency.high vobd.all|grep $naa|grep $lat;
		#else
		#echo "没有超过1000000 microseconds记录"
		fi;
		done
	done
}

#定义main_log_0008
function main_log_0008 ()
{
clear
echo "===============================================";
echo "8.检测SSD corruption事件/SSD Corruption Record";
echo -e "==============================================\n";
cd ..

echo -e "\033[44;37;5m Searching boot log... \033[0m"

findboot=$(find . -name boot* )
if [ "$findboot" == "./boot.gz" ]; then
	echo "Found boot.gz file"
	ssdcorrupt=$(zcat boot.gz | grep -i corrup)
		if [ -z "$ssdcorrupt" ]; then
			echo -e "No related log found in boot.gz file"
			echo ""
		else
			echo -e "Found such log in boot.gz file: \n$ssdcorrupt"
			echo ""
		fi

	elif  [ "$findboot" == "./boot" ]; then
		echo "Found boot file"
		ssdcorrupt=$(cat boot | grep -i "SSD corruption detected")
		if [ -z "$ssdcorrupt" ]; then
			echo "No related log found in boot file"
			echo ""
		else
			echo -e "Found such log in boot file:\n$ssdcorrupt"
			echo ""
		fi

	else
		echo -e "No boot file found"
			echo ""
	fi
cd $tdlogpath

echo -e "\033[44;37;5m  Searching vmkwarning log...\033[0m\n"
grep "SSD corruption detected" $logpath/vmkwarning*|awk -F / '{print$NF}'
echo ""
echo -e "KB#50100366 KB#2145434"


}




######################################################################################
#定义main_XXXXX_0006
#function main_XXXXX_0006 ()
#{
#}
######################################################################################
######################################################################################

# 定义main_vm_menu
function main_vm_menu ()
{
cat << EOF
------------------------------------------------------------
|***************vSAN虚拟机/对象信息分析主页****************|
|******************VM & Object Analysis********************|
------------------------------------------------------------
`echo -e "\033[35m 1)vSAN集群所有对象状态统计/All Objects Status\033[0m"`
`echo -e "\033[35m 2)本节点运行VM清单/List of VM (Running on this Node)\033[0m"`
`echo -e "\033[35m 3)vSAN当前可识别VM清单/Namespace List\033[0m"`
`echo -e "\033[35m 4)查询VM对象分配/VM & Object Mapping\033[0m"`
`echo -e "\033[35m 5)查询对象结构和基本状态/Query Object Information\033[0m"`
`echo -e "\033[35m 6)查询VM基本信息/Query VM Configration (Running on this Node)\033[0m"`
`echo -e "\033[35m 7)查询非健康状态组件/Query Unhealthy Component\033[0m"`
`echo -e "\033[35m 8)查询不可访问对象/Query Inaccessible Object\033[0m"`
`echo -e "\033[35m 9)查询UUID(Object/Comp/disk/host)/Query UUID Information(DOM/LSOM/HOST/DISK)\033[0m"`
`echo -e "\033[35m 10)测试3\033[0m"`
`echo -e "\033[35m A)运行所有选项/Run ALL\033[0m"`
`echo -e "\033[35m b)返回主菜单/Back to Home Page\033[0m"`
EOF
read -p "请输入对应选项/Please select：" num3
case $num3 in
     1)
         main_vm_0001
         main_vm_menu
         ;;
     2)
         main_vm_0002
         main_vm_menu
         ;;
     3)
         main_vm_0003
         main_vm_menu
         ;;
     4)
         main_vm_0004
         main_vm_menu
         ;;
     5)
         main_vm_0005
         main_vm_menu
         ;;
     6)
         main_vm_0006
         main_vm_menu
         ;;
     7)
         main_vm_0007
         main_vm_menu
         ;;
     8)
         main_vm_0008
         main_vm_menu
         ;;
     9)
         main_vm_0009
         main_vm_menu
         ;;
    A)
        main_vm_0001 >> $originalpath/sipadan-vm.log
        main_vm_0002 >> $originalpath/sipadan-vm.log
        main_vm_0003 >> $originalpath/sipadan-vm.log
        main_vm_0004 >> $originalpath/sipadan-vm.log
        main_vm_0005 >> $originalpath/sipadan-vm.log
        main_vm_0006 >> $originalpath/sipadan-vm.log
        mv $originalpath/sipadan-vm.log $originalpath/sipadan-vm-`date +%Y%m%d%H%M`.log
        echo "文件已经导出至$originalpath 下"
        main_log_menu
        ;;
     b)
         clear
         main_menu
         ;;
     *)
        echo "the is fail!!"
        main_vm_menu
esac
}

#定义main_vm_0001
function main_vm_0001 ()
{
clear
echo "===============================================";
echo "1.vSAN集群所有对象状态统计/All Objects Status";
echo -e "==============================================\n";
echo "	数量/Count		状态/Status";
grep state cmmds-tool_find--f-python.txt | awk '{print $1,$2,$3}' | sort | uniq -c
echo -e "\n*************************"
echo -e " 状态定义:"
echo -e " 状态07:健康 \n 状态12:数据丢失 \n 状态13:可访问但是未重建 \n 状态15:可访问但不符合存储策略"
echo -e "*************************\n"
}

#定义main_vm_0002
function main_vm_0002 ()
{
clear
echo "====================================================";
echo "2.本节点运行VM清单/List of VM (Running on this Node)";
echo -e "===================================================\n";
#echo $cmdpath
cat localcli_vm-process-list.txt| grep "Display Name\|World ID\|Config File" |awk '{l=$0;getline;print;print l; getline;print $0"\n";}'
worldnum=$(cat localcli_vm-process-list.txt|egrep "Display Name"|wc -l)
echo " 共计 $worldnum 个运行的VM"
echo " $worldnum VMs are Running"
}

#定义main_vm_0003
function main_vm_0003 ()
{
clear
echo "============================================"
echo "3.vSAN存储当前可识别目录(VM)/Namespace List"
echo "============================================"
#	echo $mycat
cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt |grep DOM_NAME -C5|grep -E 'uuid|content'|sed -e 's/"uuid"://g' -e 's/"content"://g' -e 's/{"ufn"://g' -e 's/"cid"://g' -e 's/"00000000-0000-0000-0000-000000000000"},//g' -e 's/,//g' -e 's/}//g'|xargs -n 2|grep -v ".vsan.stats"|grep -v ".iSCSI-CONFIG" > $mycat/vmt1
#	cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt |grep DOM_NAME -C5|grep -E 'uuid|content'|xargs -n 5|sed -e 's/uuid://g' -e 's/, content: {ufn://g' -e 's/},//g'|grep -v .vsan.stats > $originalpath/mycat/vmt1
num=$(cat $mycat/vmt1|wc -l)
for i in `seq 1 $num`;do
	t2=$(echo $i"p")
	t3=$(cat $mycat/vmt1 |sed -n ''$t2'')
	echo $i")" $t3    #
done
echo -e "\n共计 $num 个目录"
echo "Please Select:"
}

#定义 main_vm_0004
function main_vm_0004 ()
{
clear
echo "============================================"
echo "4.查询VM的对象分配/VM & Object Mapping Info"
echo "============================================"
echo ""
echo " Please wait a moment..."
#查询所有对象UUID
cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt |grep DOM_OBJECT -B4|grep '"uuid"'|awk -F \" '{print$4}'| while read i;

#查询所有groupuuid
do groupUuid=$(cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt |grep DOM_OBJECT -C5 |grep '"uuid": "'$i'"' -A9|grep -o "\"groupUuid\": \"[A-Za-z0-9]*-[A-Za-z0-9]*-[A-Za-z0-9]*-[A-Za-z0-9]*-[A-Za-z0-9]*\""|awk -F \" '{print $4}');


#检查对象uuid的类型 
objclass=$(cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt |grep DOM_OBJECT -C5 |grep '"uuid": "'$i'"' -A9 |grep -o "\"objClass\": [0-9]*"|awk '{print$2}'|sort|uniq)

if [ "$objclass" == "2" ]; then
	objtype="namespac"
elif	[ "$objclass" == "3" ];then
	objtype="swap"
elif
	[ "$objclass" == "4" ]; then
	objtype="vmem"
else
	objtype="vdisk"
fi



if [ "$groupUuid" != "" ];then
	nameSpace=$(cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt |grep DOM_NAME -C5 |grep '"uuid": "'$groupUuid'"' -A9|grep content|awk -F \" '{print $6}')
else
	groupUuid="noGroup";
fi


if [ "$nameSpace" != "" ];then
	echo "Namespace \"$nameSpace\" 分配给对象UUID $i  $objtype";
else
	echo "Namespace \"$groupUuid\" (没有发现对应名称) 分配给对象UUID $i $objtype";
fi;done|grep -v noGroup |sort
}


#定义main_vm_0005
function main_vm_0005 ()
{
clear
echo "=================================================="
echo "5.查询对象结构和基本状态/Query Object Information"
echo "=================================================="
echo ""
read -p "请输入查询的对象UUID/Please input DOM object UUID：" DOMUUID
echo -e "\n您要查询的UUID为 $DOMUUID \n"

#检查组件状态
#检查DOM_Object
#echo -e "\033[44;37m查询DOM_Object\033[5m"
echo ""

 owner=$(cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt |grep DOM_OBJECT -C5|grep '"uuid": "'$DOMUUID'"' -A9|grep owner|awk '{print$2}'|sed -e 's/,//g' -e 's/"//g')
 objclass=$(cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt |grep DOM_OBJECT -C5|grep '"uuid": "'$DOMUUID'"' -A9|grep -E 'content'|grep -o '\"objClass\": [0-9]*'|awk '{print$2}')

 if [ "$objclass" == "2" ]; then
        objtype="namespac"
 elif   [ "$objclass" == "3" ];then
        objtype="swap"
 elif
        [ "$objclass" == "4" ]; then
        objtype="vmem"
 else
        objtype="vdisk"
 fi

 echo -e "================================================="
 echo -e " UUID: $DOMUUID \n"
 echo -e " OWNER: $owner \n"
 #echo -e "$objclass"
 echo -e " TYPE: $objtype"

cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt |grep DOM_OBJECT -C5|grep '"uuid": "'$DOMUUID'"' -A9|grep -E 'content'|sed s/'child'/'\n\n=============child'/g|grep -v "content"|sed -e 's/"attributes"://g' -e 's/"capacity": [0, [0-9]*]//g' -e 's/"capacity": [0-9]*//g' -e 's/"componentStateTS": [0-9]*,//g' -e 's/"lastScrubbedOffset": [0-9]*,//g' -e 's/"nVotes": [0-9]*,//g' -e 's/"objClass": [0-9]*},//g' -e 's/"staleLsn": [0-9]*,//g' -e 's/"staleCsn": [0-9]*,//g' -e  's/"transient": [0-9]*,//g' -e 's/"flags": [0-9]*,//g' -e 's/"rLsn": [0-9]*},//g' -e 's/"bytesToSync": [0-9]*,//g' -e 's/"recoveryETA": [0-9]*,//g' -e 's/"isFastCCPEnabled": [0-9]*,//g' -e 's/{"stripeBlockSize": [0-9]*}, "//g' -e 's/{"scope": [0-9]*}, "//g' -e 's/"isWitness": [0-9]*,//g' -e 's/"subFaultDomainId": "[A-Za-z0-9]*-[A-Za-z0-9]*-[A-Za-z0-9]*-[A-Za-z0-9]*-[A-Za-z0-9]*"//g' -e 's/=============child-[0-9]*"://g' -e 's/"lastScrubbedOffset": [0-9]*//g' -e 's/"aggregateCapacity": [0-9]*//g'|sed -e 's/"componentUuid"/Component UUID/g' -e 's/{"type"/Type/g' -e 's/"addressSpace"/Address Space/g' -e 's/"componentState"/Component Status/g' -e 's/"faultDomainId"/Fault Domain/g' -e 's/"objClass"/对象类型/g' -e 's/"diskUuid"/Disk UUID/g' -e 's/}//g'|sed -e 's/ "$//g' -e 's/{//g' |sed -e 's/,$//g'  -e 's/,//g'
echo ""
#echo -e "\033[44;37m查询DOM_STALE_OWNER\033[5m"
echo ""
cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt |grep DOM_STALE_OWNER -C5|grep '"uuid": "'$DOMUUID'"' -A9|grep -E 'content'|sed s/'child'/'\n\n=============child'/g|grep -v "content"|sed -e 's/"attributes"://g' -e 's/"capacity": [0, [0-9]*]//g' -e 's/"capacity": [0-9]*//g' -e 's/"componentStateTS": [0-9]*,//g' -e 's/"lastScrubbedOffset": [0-9]*,//g' -e 's/"nVotes": [0-9]*,//g' -e 's/"objClass": [0-9]*},//g' -e 's/"staleLsn": [0-9]*,//g' -e 's/"staleCsn": [0-9]*,//g' -e  's/"transient": [0-9]*,//g' -e 's/"flags": [0-9]*,//g' -e 's/"rLsn": [0-9]*},//g' -e 's/"bytesToSync": [0-9]*,//g' -e 's/"recoveryETA": [0-9]*,//g' -e 's/"isFastCCPEnabled": [0-9]*,//g' -e 's/{"stripeBlockSize": [0-9]*}, "//g' -e 's/{"scope": [0-9]*}, "//g' -e 's/"isWitness": [0-9]*,//g' -e 's/"subFaultDomainId": "[A-Za-z0-9]*-[A-Za-z0-9]*-[A-Za-z0-9]*-[A-Za-z0-9]*-[A-Za-z0-9]*"//g' -e 's/=============child-[0-9]*"://g' -e 's/"lastScrubbedOffset": [0-9]*//g' -e 's/"aggregateCapacity": [0-9]*//g'|sed -e 's/"componentUuid"/组件UUID/g' -e 's/{"type"/类别/g' -e 's/"addressSpace"/声明空间/g' -e 's/"componentState"/组件状态/g' -e 's/"faultDomainId"/主机UUD/g' -e 's/"objClass"/对象类型/g' -e 's/"diskUuid"/磁盘UUID/g' -e 's/}//g'|sed -e 's/ "$//g' -e 's/,//g' -e 's/{//g'
#cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt |grep DOM_OBJECT -C5|grep '"uuid": "'$DOMUUID'"' -A9|grep -E 'content'|sed s/'child'/'\n\n=============child'/g|grep Component|sed -e 's/"attributes"://g' -e 's/{"capacity": [0, [0-9]*],//g' -e 's/"componentStateTS": [0-9]*,//g' -e 's/"lastScrubbedOffset": [0-9]*,//g' -e 's/"nVotes": [0-9]*,//g' -e 's/"objClass": [0-9]*},//g' -e 's/"staleLsn": [0-9]*,//g' -e 's/"staleCsn": [0-9]*,//g' -e  's/"transient": [0-9]*,//g' -e 's/"flags": [0-9]*,//g' -e 's/"rLsn": [0-9]*},//g' -e 's/"bytesToSync": [0-9]*,//g' -e 's/"recoveryETA": [0-9]*,//g'|awk '{print $2 $3 $12 $13 $4 $5 $6 $7 $8 $9 $14 $15}'|sed -e 's/"componentUuid"/ 组件UUID/g' -e 's/{"type"/ 类别/g' -e 's/"addressSpace"/ 声明空间/g' -e 's/"componentState"/ 组件状态/g' -e 's/"faultDomainId"/ 主机UUD/g' -e 's/"objClass"/ 对象类型/g' -e 's/"diskUuid"/ 磁盘UUID/g' -e 's/}//g'|sed -e 's/,$//g' -e 's/{//g'
#
#检查见证
#cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt |grep DOM_OBJECT -C5|grep '"uuid": "'$DOMUUID'"' -A9|grep -E 'content'|sed s/'child'/'\n\n=============child'/g|grep Witness|awk '{print $2 $3 $15 $16 $5 $6  $9 $10 $11 $12  $17 $18}'|sed -e 's/"componentUuid"/ 组件UUID/g' -e 's/{"type"/ 类别/g' -e 's/"addressSpace"/ 声明空间/g' -e 's/{"componentState"/ 组件状态/g' -e 's/"faultDomainId"/ 主机UUD/g' -e 's/"objClass"/ 对象类型/g' -e 's/"diskUuid"/ 磁盘UUID/g' -e 's/}//g'|sed -e 's/,$//g'

echo ""
}

#定义函数main_vm_0006
function main_vm_0006 ()
{
#clear
echo "============================================================="
echo "6.查询VM基本信息/Query VM Configration (Running on this Node)"
echo "============================================================="
echo ""
#输入查询VM名称
read -p "请输入查询的VM名称/Please input VM name：" searchvmname
echo "您要查询的VM名称为：$searchvmname"


vmpathsearch=$(cat localcli_vm-process-list.txt |grep $searchvmname":" -A6|grep " Config File:"|awk '{print$3}')

if [ "$vmpathsearch" != "" ]; then

	vmpath=..${vmpathsearch%/*}	
	echo "您要查询的VM的路径为/VM's Path：$vmpath"

else
#	echo "VM在本台主机上未处于开机状态"
#获取VM的UUID
	namespaceuuid=$(cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt |grep DOM_NAME -C5 |grep -w "$searchvmname" -B9|grep uuid|awk -F \: '{print$2}'|sed -e 's/,//g' -e 's/"//g')
	echo "您要查询的VM的UUID为/VM's UUID：$namespaceuuid"

#获取VM的路径
vmpath=$(find ../vmfs/volume*/* -name $namespaceuuid)
echo "您要查询的VM的路径为/VM's Path：$vmpath"

fi

echo -e "您要查询的VM基本信息如下/VM's Basic Information:\n"

main_vm_0099
}

#定义函数main_vm_0099
function main_vm_0099 ()
{

#查询VM基本信息
 cat $vmpath/*vmx |grep -E 'displayName|scsi[0-9]*:[0-9]*.fileName|numvcpus|memSize|ethernet[0-9]*'|grep -v -E '.pciSlotNumber|.addressType|.uptCompatibility|.present' > $mycat/vminfo

 vmname=$(cat $mycat/vminfo|grep displayName|awk '{print$3}')

 vcpu=$(cat $mycat/vminfo|grep numvcpus|awk '{print$3}')

 vmem=$(cat $mycat/vminfo|grep memSize|awk '{print$3}')

 numvmdk=$(cat $mycat/vminfo |grep scsi|wc -l)
 vmdk=$(cat $mycat/vminfo|grep scsi[0-9]*:[0-9]*.fileName)

 numvnic=$(cat $mycat/vminfo|grep ethernet|awk -F . '{print$1}'|sort|uniq|wc -l)
 vnic=$(cat $mycat/vminfo|grep ethernet[0-9]*)


 echo -e "VM Name: $vmname\n\nvCPU:$vcpu\n\nMemory:$vmem\n\nVMDK Info: 共配置$numvmdk块磁盘\n$vmdk \n\nVM Network Info: 共配置$numvnic个网口\n$vnic"
}




#定义函数main_vm_0007
function main_vm_0007 ()
{
echo "==============================================="
echo "7.查询非健康状态组件/Query Unhealthy Component"
echo "==============================================="
echo ""
#导出unhealthyelsomuuid
egrep -o componentState[^}]+}[^}]+ cmmds-tool_find--f-python.txt | grep -v 'componentState\\": 5' |sed -e 's/\\"//g'|grep -o -E 'componentState: [0-9]*,|componentUuid: [a-zA-Z0-9]*-[a-zA-Z0-9]*-[a-zA-Z0-9]*-[a-zA-Z0-9]*-[a-zA-Z0-9]*'|grep componentUuid > $mycat/unhealthylsomuuid

#导出unhealthylsomstate
egrep -o componentState[^}]+}[^}]+ cmmds-tool_find--f-python.txt | grep -v 'componentState\\": 5' |sed -e 's/\\"//g'|grep -o -E 'componentState: [0-9]*,|componentUuid: [a-zA-Z0-9]*-[a-zA-Z0-9]*-[a-zA-Z0-9]*-[a-zA-Z0-9]*-[a-zA-Z0-9]*'|grep componentState > $mycat/unhealthylsomstate


paste $mycat/unhealthylsomuuid $mycat/unhealthylsomstate | sed -e 's/componentUuid/组件UUID/g' -e 's/componentState/组件状态/g'


echo ""
read -p "请输入查询的非健康状态组件UUID/Please input unhealthy component UUID:" unhealthylsomuuid
echo ""

cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt |grep LSOM_OBJECT -C5|grep $unhealthylsomuuid -A10|grep -o -E '\"uuid\": \"[a-zA-Z0-9]*-[a-zA-Z0-9]*-[a-zA-Z0-9]*-[a-zA-Z0-9]*-[a-zA-Z0-9]*\"|\"owner\": \"[a-zA-Z0-9]*-[a-zA-Z0-9]*-[a-zA-Z0-9]*-[a-zA-Z0-9]*-[a-zA-Z0-9]*\"|\"health\": \"[a-zA-Z]*\"|\"diskUuid\": \"[a-zA-Z0-9]*-[a-zA-Z0-9]*-[a-zA-Z0-9]*-[a-zA-Z0-9]*-[a-zA-Z0-9]*\"|\"compositeUuid\": \"[a-zA-Z0-9]*-[a-zA-Z0-9]*-[a-zA-Z0-9]*-[a-zA-Z0-9]*-[a-zA-Z0-9]*\"|\"capacityUsed\": [0-9]*|\"physCapacityUsed\": [0-9]*'|sed -e 's/"uuid"/UUID/g' -e 's/"owner"/Owner(Host)/g' -e 's/"health"/Health/g' -e 's/"diskUuid"/Disk UUID/g' -e 's/"compositeUuid"/DOM Object UUID/g'

}


#定义main_vm_0008
function main_vm_0008 ()
{
echo "==================================================="
echo "8.查询不可访问的对象列表/Query Inaccessible Object"
echo "==================================================="
echo ""
#所有DOM UUID    
cat cmmds-tool_find--f-python.txt |grep DOM_OBJECT -B4 |grep uuid |awk '{print$2}'|sed -e 's/"//g' -e 's/,//g' > $mycat/objectuuidlist


#所有state12uuidlist UUID  
grep  '\\\"state\\\": 12' cmmds-tool_find--f-python.txt  -B9|grep uuid|awk '{print$2}'|sed -e 's/"//g' -e 's/,//g' > $mycat/state12uuidlist


rm -f $mycat/inaccessibleobjlist >> /dev/null

for i in $(cat $mycat/state12uuidlist);
        do if [ "$(grep $i $mycat/objectuuidlist)" != "" ]; then
                echo $i >> $mycat/inaccessibleobjlist

        fi
done
echo -e "不可访问的对象包括/Inaccessible Object List:"	
cat  $mycat/inaccessibleobjlist
echo ""
main_vm_0098

}

#定义main_vm_0098
function main_vm_0098 ()
{

 read -p "请输入不可访问的对象UUID/Please input inaccessible object UUID:" inaccessibleuuid
 owner=$(cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt |grep DOM_OBJECT -C5|grep '"uuid": "'$inaccessibleuuid'"' -A9|grep owner|awk '{print$2}'|sed -e 's/,//g' -e 's/"//g')
 objclass=$(cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt |grep DOM_OBJECT -C5|grep '"uuid": "'$inaccessibleuuid'"' -A9|grep -E 'content'|grep -o '\"objClass\": [0-9]*'|awk '{print$2}')
 
 if [ "$objclass" == "2" ]; then
 	objtype="namespac"
 elif	[ "$objclass" == "3" ];then
 	objtype="swap"
 elif
 	[ "$objclass" == "4" ]; then
 	objtype="vmem"
 else
 	objtype="vdisk"
 fi
 
 
 echo -e "================================================="
 echo -e " UUID: $inaccessibleuuid \n"
 echo -e " OWNER: $owner \n"
 #echo -e "$objclass"
 echo -e " TYPE: $objtype"
 
 cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt |grep DOM_OBJECT -C5|grep '"uuid": "'$inaccessibleuuid'"' -A9|grep -E 'content'|sed s/'child'/'\n\n=============child'/g|grep -v "content"|sed -e 's/"attributes"://g' -e 's/"capacity": [0, [0-9]*]//g' -e 's/"capacity": [0-9]*//g' -e 's/"componentStateTS": [0-9]*,//g' -e 's/"lastScrubbedOffset": [0-9]*,//g' -e 's/"nVotes": [0-9]*,//g' -e 's/"objClass": [0-9]*},//g' -e 's/"staleLsn": [0-9]*,//g' -e 's/"staleCsn": [0-9]*,//g' -e  's/"transient": [0-9]*,//g' -e 's/"flags": [0-9]*,//g' -e 's/"rLsn": [0-9]*},//g' -e 's/"bytesToSync": [0-9]*,//g' -e 's/"recoveryETA": [0-9]*,//g' -e 's/"isFastCCPEnabled": [0-9]*,//g' -e 's/{"stripeBlockSize": [0-9]*}, "//g' -e 's/{"scope": [0-9]*}, "//g' -e 's/"isWitness": [0-9]*,//g' -e 's/"subFaultDomainId": "[A-Za-z0-9]*-[A-Za-z0-9]*-[A-Za-z0-9]*-[A-Za-z0-9]*-[A-Za-z0-9]*"//g' -e 's/=============child-[0-9]*"://g' -e 's/"lastScrubbedOffset": [0-9]*//g' -e 's/"aggregateCapacity": [0-9]*//g'|sed -e 's/"componentUuid"/Component UUID/g' -e 's/{"type"/Type/g' -e 's/"addressSpace"/Address Space/g' -e 's/"componentState"/Component State/g' -e 's/"faultDomainId"/Fault Domain/g' -e 's/"objClass"/Obect Type/g' -e 's/"diskUuid"/Disk UUID/g' -e 's/}//g'|sed -e 's/ "$//g' -e 's/{//g' |sed -e 's/,$//g'  -e 's/,//g'
  echo -e "================================================="
}


#定义main_vm_0009
function main_vm_0009 ()
{

echo "================================================================="
echo "9.查询UUID(Object/Comp/disk/host)/Query UUID (DOM/LSOM/HOST/DISK)"
echo "================================================================="
echo ""
read -p "请输入查询的对象UUID/Please input the UUID:" UUID
echo -e "\n您要查询的UUID为 $UUID \n"

#定义UUID类型
type=$(cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt |grep "\"uuid\": \"$UUID\"" -A4|grep \"type\"|grep -w -E 'DOM_OBJECT|LSOM_OBJECT|HOSTNAME|DISK' |awk '{print$2}'|sed -e 's/"//g' -e 's/,//g')
echo -e "您查询的UUID的类型为/The Type of UUID is $type \n "
# DOM_OBJECT
# 对象UUID具体分类
if [ "$type" == "DOM_OBJECT" ]; then
	owner=$(cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt |grep DOM_OBJECT -C5|grep '"uuid": "'$UUID'"' -A9|grep owner|awk '{print$2}'|sed -e 's/,//g' -e 's/"//g')
	ownerhostname=$(cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt |grep HOSTNAME -C5|grep '"uuid": "'$owner'"' -A9|grep '"content"'|awk '{print$3}'|sed -e 's/"//g' -e 's/}//g' -e 's/,//g')
	objclass=$(cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt |grep DOM_OBJECT -C5|grep '"uuid": "'$UUID'"' -A9|grep -E 'content'|grep -o '\"objClass\": [0-9]*'|awk '{print$2}')
	if [ "$objclass" == "2" ]; then
		objtype="namespace"
		domname=$(cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt |grep DOM_NAME -C5|grep '"uuid": "'$UUID'"' -A9|grep -E 'content'|awk '{print$3}'|sed -e 's/"//g' -e 's/}//g' -e 's/,//g')
	elif   [ "$objclass" == "3" ];then
		objtype="swap"
	elif   [ "$objclass" == "4" ]; then
	        objtype="vmem"
	else
		objtype="vdisk"
	fi

	echo -e "================================================="
	echo -e " UUID: $UUID \n"
	echo -e " OWNER: $owner  $ownerhostname\n"
	echo -e " TYPE: $objtype $domname"
	cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt |grep DOM_OBJECT -C5|grep '"uuid": "'$UUID'"' -A9|grep -E 'content'|sed s/'child'/'\n\n=============child'/g|grep -v "content"| tr ',' '\n'|grep -E 'child|type|addressSpace|"componentState"|faultDomainId|componentUuid|diskUuid|isWitness'|sed ':a ; N;s/\n/ / ; t a ; '|sed -e 's/=============child-[0-9]*":/\n/g' -e 's/"attributes"://g' -e 's/"isWitness": [0-9]*//g'|sed -e 's/"componentUuid"/Component UUID/g' -e 's/{"type"/Type/g' -e 's/"addressSpace"/Address Space/g' -e 's/"componentState"/Component State/g' -e 's/"faultDomainId"/Fault Domain/g' -e 's/"objClass"/Object Type/g' -e 's/"diskUuid"/Disk UUID/g' -e 's/}//g'|sed -e 's/ "$//g' -e 's/{//g' |sed -e 's/,$//g'  -e 's/,//g'
	#cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt |grep DOM_OBJECT -C5|grep '"uuid": "'$UUID'"' -A9|grep -E 'content'|sed s/'child'/'\n\n=============child'/g|grep -v "content"|sed -e 's/"attributes"://g' -e 's/"capacity": [0, [0-9]*]//g' -e 's/"capacity": [0-9]*//g' -e 's/"componentStateTS": [0-9]*,//g' -e 's/"lastScrubbedOffset": [0-9]*,//g' -e 's/"nVotes": [0-9]*,//g' -e 's/"objClass": [0-9]*},//g' -e 's/"staleLsn": [0-9]*,//g' -e 's/"staleCsn": [0-9]*,//g' -e  's/"transient": [0-9]*,//g' -e 's/"flags": [0-9]*,//g' -e 's/"rLsn": [0-9]*},//g' -e 's/"bytesToSync": [0-9]*,//g' -e 's/"recoveryETA": [0-9]*,//g' -e 's/"isFastCCPEnabled": [0-9]*,//g' -e 's/{"stripeBlockSize": [0-9]*}, "//g' -e 's/{"scope": [0-9]*}, "//g' -e 's/"isWitness": [0-9]*,//g' -e 's/"subFaultDomainId": "[A-Za-z0-9]*-[A-Za-z0-9]*-[A-Za-z0-9]*-[A-Za-z0-9]*-[A-Za-z0-9]*"//g' -e 's/=============child-[0-9]*"://g' -e 's/"lastScrubbedOffset":[0-9]*//g' -e 's/"aggregateCapacity": [0-9]*//g'|sed -e 's/"componentUuid"/组件UUID/g' -e 's/{"type"/类别/g' -e 's/"addressSpace"/声明空间/g' -e 's/"componentState"/组件状态/g' -e 's/"faultDomainId"/主机UUD/g' -e 's/"objClass"/对象类型/g' -e 's/"diskUuid"/磁盘UUID/g' -e 's/}//g'|sed -e 's/ "$//g' -e 's/{//g' |sed -e 's/,$//g'  -e 's/,//g'
	domname=""
	echo -e "================================================="
# LOSM_OBJECT
elif [ "$type" == "LSOM_OBJECT" ]; then
 	owner=$(cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt |grep LSOM_OBJECT -C5|grep '"uuid": "'$UUID'"' -A9|grep owner|awk '{print$2}'|sed -e 's/,//g' -e 's/"//g')
	ownerhostname=$(cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt |grep HOSTNAME -C5|grep '"uuid": "'$owner'"' -A9|grep '"content"'|awk '{print$3}'|sed -e 's/"//g' -e 's/}//g' -e 's/,//g')
 	health=$(cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt |grep LSOM_OBJECT -C5|grep '"uuid": "'$UUID'"' -A9|grep health|awk '{print$2}'|sed -e 's/,//g' -e 's/"//g')
	echo -e "================================================="
	echo -e " UUID: $UUID \n"
	echo -e " OWNER: $owner $ownerhostname\n"
	echo -e " Health: $health \n"
 	cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt |grep LSOM_OBJECT -C5|grep '"uuid": "'$UUID'"' -A9|grep -E 'content'|awk '{print$2, $3, $4, $5, $6, $7, $8,$9}'|sed -e 's/"diskUuid"/ Disk UUID/g' -e 's/"compositeUuid"/Object UUID/g' -e 's/{//g'
	echo -e "================================================="
# HOSTNAME
elif [ "$type" == "HOSTNAME" ]; then
	hostname=$(cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt |grep HOSTNAME -C5|grep '"uuid": "'$UUID'"' -A9|grep content|awk '{print$3}'|sed -e 's/"//g' -e 's/}//g' -e 's/,//g')
 	health=$(cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt |grep HOSTNAME -C5|grep '"uuid": "'$UUID'"' -A9|grep health|awk '{print$2}'|sed -e 's/,//g' -e 's/"//g')
	echo -e "================================================="
	echo -e " UUID: $UUID \n"
	echo -e " Hostname: $hostname \n"
	echo -e " Health: $health \n"
	echo -e " 包含以下磁盘/Have these disks:"
	for diskuuid in $(cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt |grep -e '"DISK"' -C5 |grep $UUID  -B1|grep uuid|awk '{print$2}'|sed -e 's/"//g' -e 's/,//g');
	do echo "------------------------------"
	echo " Disk UUID: $diskuuid"
	cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt |grep -e '"DISK"' -C5 |grep '"uuid": "'$diskuuid'"' -A9|grep content| tr ',' '\n'|grep -E 'devName|isSsd'|sed -e 's/"//g' ;
 done
	echo -e "================================================="
# DISK
elif [ "$type" == "DISK" ]; then
	owner=$(cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt |grep -w '"DISK"' -C5|grep '"uuid": "'$UUID'"' -A9|grep owner|awk '{print$2}'|sed -e 's/,//g' -e 's/"//g')
	ownerhostname=$(cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt |grep HOSTNAME -C5|grep '"uuid": "'$owner'"' -A9|grep '"content"'|awk '{print$3}'|sed -e 's/"//g' -e 's/}//g' -e 's/,//g')
	health=$(cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt |grep -w '"DISK"' -C5|grep '"uuid": "'$UUID'"' -A9|grep health|awk '{print$2}'|sed -e 's/,//g' -e 's/"//g')
	echo -e "================================================="
	echo -e " UUID: $UUID \n"
	echo -e " OWNER: $owner $ownerhostname\n"
	echo -e " Health: $health \n"
	cat cmmds-tool_-f-json-readdump--p--d-scratchlogcmmdsdump.txt |grep -w '"DISK"' -C5|grep '"uuid": "'$UUID'"' -A9|grep content| tr ',' '\n'|grep -E 'capacity|isSsd|ssdUuid|formatVersion|devName'|sed -e 's/  "content": {//g'
	echo -e "================================================="



else
	 echo "其他类型UUID/Other Type"

fi
}

######################################################################################
#定义main_XXXXX_0006
#function main_XXXXX_0006 ()
#{
#}
######################################################################################
######################################################################################


main_menu
#supportselect
