rm -r qrhythmcafe/usr

mkdir -p qrhythmcafe/usr/share/qrhythmcafe
mkdir -p qrhythmcafe/usr/share/applications
mkdir -p qrhythmcafe/usr/bin
mkdir -p qrhythmcafe/usr/share/mime/packages

cp ../*.py qrhythmcafe/usr/share/qrhythmcafe/
cp -r ../ui qrhythmcafe/usr/share/qrhythmcafe/

chmod +x runner.sh
cp runner.sh qrhythmcafe/usr/bin/qrhythmcafe

cp qrhythmcafe.desktop qrhythmcafe/usr/share/applications/

cp mime.xml qrhythmcafe/usr/share/mime/packages/qrhythmcafe.xml

dpkg-deb --build qrhythmcafe