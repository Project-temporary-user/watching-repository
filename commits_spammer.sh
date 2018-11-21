#!/bin/bash


if [ $# -eq 0 ]; then
 echo "Provide token, username, repository and number of commits"
 exit 1
fi

current_dir=$(dirname "$0")
token=$1
username=$2
controlled_repository=$3
commit_number=$4
controlled_repository_dir="$current_dir/$controlled_repository"

echo "$token"
echo "$username"
echo "$controlled_repository"
echo "$controlled_repository_dir"


if ! [ -d ${controlled_repository_dir} ]; then
mkdir ${controlled_repository_dir}
cd "$controlled_repository_dir"
git clone "https://github.com/$username/$controlled_repository.git" ${controlled_repository_dir}
git remote set-url origin "https://$username:${token}@github.com/$username/$controlled_repository.git"
fi


cd ${controlled_repository_dir}
for i in `seq $commit_number`; do
    echo `date '+%Y%m%d%H%M%S'` > README.md
    git add README.md
    git commit -m "new code change"
    git push origin master
    sleep 5
done