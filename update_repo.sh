#!/bin/bash
#cd ~/toni/ethereum-data-pipeline
#git pull origin main

cd ~/ethereum/mempool.pics-building
#../bin/python3 zeromevparser.py
../bin/python3 dataprep.py
cp -r ./assets/ ./mempool.pics/
cp -r ./data/ ./mempool.pics/
cp app.py ./mempool.pics/app.py
cp requirements.txt ./mempool.pics/requirements.txt
#cp identified_validators.csv ./mempool.pics/identified_validators.csv
cp Procfile ./mempool.pics/Procfile
cp update_repo.sh ./mempool.pics/update_repo.sh 


cd mempool.pics
git add ./assets/
#git add ./.gitignore
git add ./data/
git add ./app.py
#git add ./dataprep.py
git add ./requirements.txt
git add ./Procfile
git add ./update_repo.sh

git commit -m "update progress"
git push origin main --force



