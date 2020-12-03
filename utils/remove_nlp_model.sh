modelName=""
for i in ${!options[@]}; do

    option="${options[$i]}"

    if [[ $option == --model-name=* ]]; then
        modelName="$(echo $option | awk -F '=' '{print $2}')"
        sudo rm -rf /opt/cortic_modules/nlp_module/models/$modelName
    fi

done