options=("$@")
modelName="my_nlu_model"

docker run -it --network host --privileged -v /opt/cortic_modules/nlp_module:/nlp_module --rm cortictech/nlp:0.51 rasa train --config /nlp_module/config.yml  --data /nlp_module/training_data/  --domain /nlp_module/domain.yml --out /nlp_module/tmp_models

for i in ${!options[@]}; do

    option="${options[$i]}"

    if [ "$option" = --model-name=* ]; then
        modelName="$(echo $option | awk -F '=' '{print $2}')"
    fi

done

echo "Extracting the trained model to CAIT directory..."

cd /opt/cortic_modules/nlp_module/tmp_models
sudo tar xvf nlu*.tar.gz
sudo cp -R nlu /opt/cortic_modules/nlp_module/models/$modelName
cd ..
sudo rm -rf tmp_models

echo "Finish training a custom NLU model named: $modelName, you can use it in CAIT now."