/* 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, March 2020
  
 */

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function ajax_post(url, data) {
  $.ajax({
    url: url,
    type: 'POST',
    data: data
  });
}

async function restart() {
  $.post( "/newname", {}, async function( data ) {
    var hostname = data['hostname'] + ".local";
    console.log(hostname);
    if (data['hostname'] == "") {
      url = window.location.protocol + "//" +  window.location.hostname;
    }
    else {
      url = window.location.protocol + "//" +  hostname;
    }
    console.log(url);
    var loader = document.getElementById('loader');
    loader.style.display = "flex";
    loader.style.zIndex = 1;
    $.post( "/finish", {}, async function( data ) {
      console.log(data);
      ajax_post("/reboot", {});
      await sleep(60000);
      
      window.location.href = url;
    });
  });
}
