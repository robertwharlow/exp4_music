cd package
rm my-function.zip
zip -r my-function.zip *
aws lambda update-function-code --function-name  exp4 --zip-file fileb://my-function.zip
cd ..
