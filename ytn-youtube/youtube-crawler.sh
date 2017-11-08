sudo pip3 install --upgrade youtube-dl
youtube-dl -i -f 140/m4a --id --write-description --write-auto-sub --convert-subs lrc -k --sub-lang ko $1
