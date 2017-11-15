sudo pip3 install --upgrade youtube-dl
youtube-dl -i -f 140/m4a --id --write-description --write-auto-sub --convert-subs lrc -k --sub-lang ko 'https://www.youtube.com/user/ytnnews24' --datebefore 20171108 --playlist-start 300 --playlist-end 1500
mv ./*.m4a crawled
mv ./*.lrc crawled
mv ./*.vtt crawled
mv ./*.description crawled