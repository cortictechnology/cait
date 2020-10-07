/* 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, March 2020
  
 */

async function ajax_post(url, data) {
    return $.ajax({
      url: url,
      type: 'POST',
      data: data
    });
}

async function set_device_info(){
    var device_name = document.getElementById("device_name").value;
    var username = document.getElementById("user_name").value;
    var user_password = document.getElementById("user_password").value;
    if (username.length > 0 && user_password.length > 0 && device_name.length > 0) {
      try {
        const result = await ajax_post("/customdev", {'device_name': device_name, 
                                                      'username': username, 
                                                      'user_password': user_password});
        url = window.location.protocol + "//" +  window.location.hostname + "/testhardware";
        //console.log(url);
        window.location.href = url;
        
      } catch(err) {
          console.log(err);
          return err;
      }
    } else {
      alert(localizedStrings.emptyField[locale])
  }
}