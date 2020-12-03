options=("$@")
modelName="my_nlu_model"
traininDataPath="/nlp_module/training_data/default"

for i in ${!options[@]}; do

    option="${options[$i]}"

    if [[ $option == --model-name=* ]]; then
        modelName="$(echo $option | awk -F '=' '{print $2}')"
    fi

    if [[ $option == --training-data-path=* ]]; then
        traininDataPath="$(echo $option | awk -F '=' '{print $2}')"
    fi

done

nluDataPath=$traininDataPath
configPath="$traininDataPath/config.yml"
domainPath="$traininDataPath/domain.yml"

docker run -it --network host --privileged -v /opt/cortic_modules/nlp_module:/nlp_module -v $traininDataPath:$traininDataPath --rm cortictech/nlp:0.52 rasa train --config $configPath  --data $nluDataPath  --domain $domainPath --out /nlp_module/tmp_models

echo "Extracting the trained model to CAIT directory..."

cd /opt/cortic_modules/nlp_module/tmp_models
sudo tar xvf nlu*.tar.gz
sudo cp -R nlu /opt/cortic_modules/nlp_module/models/$modelName
cd ..
sudo rm -rf tmp_models

echo "Finish training a custom NLU model named: $modelName, you can use it in CAIT now."