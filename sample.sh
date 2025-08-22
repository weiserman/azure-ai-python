#!/bin/bash
#--------------------------------------------------------------------------------
SUBSCRIPTION_KEY=someKey
ENDPOINT=https://southafricanorth.api.cognitive.microsoft.com
MODELID=prebuilt-invoice
IMGURL=https://myblobstoragesa12345.blob.core.windows.net/my-blob-container/a.jpg
ACCOUNT_NAME="myblobstoragesa12345"
CONTAINER_NAME="my-blob-container"
BLOB_NAME="a.jpg"
LOCAL_FILE="./data/a.jpg"
SAS_TOKEN="sv=2024-11-04&ss=bfqt&srt=sco&sp=rwdlacupiytfx&se=2025-08-11T03:53:42Z&st=2025-08-10T19:38:42Z&spr=https&sig=SOMETHING%2FdfkMkZJVUzCXC8KC2lBTjwsZ%2Bbl68RU%3D"
NRNDLINES=30
#--------------------------------------------------------------------------------
echo Generating document
mkdir -p ./res/
declare -a SUBS=("The cat" "A dog" "My friend" "The sun")
declare -a VERBS=("runs" "jumps" "sings" "shines")
declare -a OBJS=("quickly" "happily" "brightly" "loudly")
RNDLINES="${SUBS[$SUBIDX]} ${VERBS[$VERBIDX]} ${OBJS[$OBJIDX]}.\n"
for I in $(seq 0 1 $NRNDLINES);do
        SUBIDX=$(( RANDOM % ${#SUBS[@]} ))
        VERBIDX=$(( RANDOM % ${#VERBS[@]} ))
        OBJIDX=$(( RANDOM % ${#OBJS[@]} ))
        RNDLINES=$RNDLINES"${SUBS[$SUBIDX]} ${VERBS[$VERBIDX]} ${OBJS[$OBJIDX]}.\n"
done
echo $RNDLINES > data/lines.txt
convert \
        -size 595x842 xc:white \
        -font Helvetica \
        -pointsize 12 \
        -gravity NorthWest \
        -annotate +10+10 "$RNDLINES" \
        -resize 595x842 "./data/a.jpg"
#--------------------------------------------------------------------------------
echo Uploading document
curl \
        -X PUT \
        -H "x-ms-blob-type: BlockBlob" \
        --upload-file "$LOCAL_FILE" \
        "https://$ACCOUNT_NAME.blob.core.windows.net/$CONTAINER_NAME/$BLOB_NAME?$SAS_TOKEN"
#--------------------------------------------------------------------------------
echo Scanning document
rm -rf ./headers.txt
curl \
	-s \
	-D headers.txt \
	"$ENDPOINT/documentintelligence/documentModels/$MODELID:analyze?api-version=2024-11-30" \
	-X POST \
	-H "Content-Type: application/json" \
	-H "Ocp-Apim-Subscription-Key: $SUBSCRIPTION_KEY" \
	--data-ascii "{'urlSource': '$IMGURL'}"
OPERATION_URL=$(cat ./headers.txt |grep -i operation-location|tr -d '\r'|awk -F': ' '{print $2}')
rm ./headers.txt
STATUS=running
while [[ "$STATUS" = "running" ]]; do
	sleep 1
	echo polling...
	curl \
		-s \
		"$OPERATION_URL" \
		-H "Ocp-Apim-Subscription-Key: $SUBSCRIPTION_KEY" | jq '.' > ./operation.json
	STATUS=$(cat operation.json|jq '.status' -r)
done
cat operation.json|jq '.analyzeResult.content' -r
#--------------------------------------------------------------------------------
