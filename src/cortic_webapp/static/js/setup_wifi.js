/* 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, March 2020
  
 */

async function ajax_post(url, data) {
    return $.ajax({
      url: url,
      type: 'POST',
      data: data,
      timeout: 30000
    }).fail(function(jqXHR, textStatus){
        if(textStatus === 'timeout')
        {     
            alert("The device's AP internet has gone down during wifi connection, pleaase make sure you reconnect to the device's AP network again, then refresh this page."); 
        }
    });
}

var cait_system_up = false

const inputField = document.querySelector('.chosen-value');
const dropdown = document.querySelector('.value-list');
var dropdownArray = [... document.querySelectorAll('li')];
//console.log(typeof dropdownArray)
dropdown.classList.add('open');
var selected_wifi = "";
inputField.focus(); // Demo purposes only
let valueArray = [];
dropdownArray.forEach(item => {
    valueArray.push(item.textContent);
});

const closeDropdown = () => {
    dropdown.classList.remove('open');
}

inputField.addEventListener('input', () => {
    dropdown.classList.add('open');
    let inputValue = inputField.value.toLowerCase();
    let valueSubstring;
    if (inputValue.length > 0) {
    for (let j = 0; j < valueArray.length; j++) {
        if (!(inputValue.substring(0, inputValue.length) === valueArray[j].substring(0, inputValue.length).toLowerCase())) {
        dropdownArray[j].classList.add('closed');
        } else {
        dropdownArray[j].classList.remove('closed');
        }
    }
    } else {
    for (let i = 0; i < dropdownArray.length; i++) {
        dropdownArray[i].classList.remove('closed');
    }
    }
});

dropdownArray.forEach(item => {
    item.addEventListener('click', (evt) => {
    inputField.value = item.textContent;
    dropdownArray.forEach(dropdown => {
        dropdown.classList.add('closed');
    });
    });
})

inputField.addEventListener('focus', () => {
    document.getElementById('password').style.visibility = "hidden";
    inputField.placeholder = 'Select WiFi';
    dropdown.classList.add('open');
    dropdownArray.forEach(dropdown => {
    dropdown.classList.remove('closed');
    });
});

inputField.addEventListener('blur', () => {
    inputField.placeholder = localizedStrings.availWifi[locale];
    dropdown.classList.remove('open');
});

document.addEventListener('click', (evt) => {
    const isDropdown = dropdown.contains(evt.target);
    const isInput = inputField.contains(evt.target);
    if (!isDropdown && !isInput) {
    dropdown.classList.remove('open');
    }
});

current_wifi_list = [];

async function get_wifi() {
    $.post( "/getwifi", function( data ) {
        var new_wifi_list = [];
        for (var i = 0; i < data.length; i++) {
            var ssid = data[i];
            new_wifi_list.push(ssid)
          }
        for (var j = 0; j < current_wifi_list.length; j++){
            var exist_ssid = current_wifi_list[j];
            if (new_wifi_list.includes(exist_ssid) == false){
                current_wifi_list.splice(j, 1);
            }
        }

        for (var k = 0; k < new_wifi_list.length; k++) {
            var new_ssid = new_wifi_list[k];
            if (current_wifi_list.includes(new_ssid) == false){
                current_wifi_list.push(new_ssid);
            }
        }
        var ul = document.querySelector("ul");
        ul.innerHTML = "";

        for (var l = 0; l < current_wifi_list.length; l++) {
            var ssid = current_wifi_list[l];
            var listItem = document.createElement("li");
            listItem.textContent = ssid;
            ul.appendChild(listItem);
        }
        dropdownArray = [... document.querySelectorAll('li')];
        dropdownArray.forEach(item => {
            item.addEventListener('click', (evt) => {
            inputField.value = item.textContent;
            selected_wifi = item.textContent;
            document.getElementById('password').style.visibility = "visible";
            dropdownArray.forEach(dropdown => {
                dropdown.classList.add('closed');
            });
            });
        })
      });
  }
get_wifi();
setInterval(get_wifi, 10000);

async function connect_wifi() {
    var wifi_name = selected_wifi;
    var wifi_password = document.getElementById("wifi_pw").value;
    loader.style.display = "flex";
    loader.style.zIndex = 1;
    try {
        const result = await ajax_post("/connectwifi", {'ssid' : wifi_name, 
                                                        'password': wifi_password});
        console.log(result);
        if (result['result'] == false) {
            alert("Failed to connect wifi, please select another wifi or retry.");
            loader.style.display = 'none';
        }
        else {
            loader.style.display = 'none';
            url = window.location.protocol + "//" + window.location.hostname + "/set_device_info";
            window.location.href = url;
        }
      } 
    catch(err) {
          console.log(err);
          return err;
    }

    // $.post( "/connectwifi", {'ssid' : wifi_name, 'password': wifi_password}, function( data ) {
    //     console.log(data);
    //     if (data['result'] == false){
    //         alert("Failed to connect wifi, please select another wifi or retry.");
    //         loader.style.display = 'none';
    //     }
    //     else if (data['result'] == true) {
    //         loader.style.display = 'none';
    //         url = window.location.protocol + "//" +  window.location.hostname + "/set_device_info";
    //         window.location.href = url;
    //     }
    // });
}
