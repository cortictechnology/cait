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

function serverReachable(hostname) {
  // IE vs. standard XHR creation
  var x = new ( window.ActiveXObject || XMLHttpRequest )( "Microsoft.XMLHTTP" ),
      s;
  x.open(
    // requesting the headers is faster, and just enough
    "HEAD",
    // append a random string to the current hostname,
    // to make sure we're not hitting the cache
    "//" + hostname + "/?rand=" + Math.random(),
    // make a synchronous request
    false
  );
  try {
    x.send();
    s = x.status;
    // Make sure the server is reachable
    return ( s >= 200 && s < 300 || s === 304 );
  // catch network & other problems
  } catch (e) {
    return false;
  }
}

async function restart() {
  $.post( "/newname", {}, async function( data ) {
    var hostname = data['hostname'] + ".local";
    console.log(hostname);
    if (data['hostname'] == "") {
      hostname = window.location.hostname;
    }
    url = window.location.protocol + "//" +  hostname;
    console.log(url);
    var loader = document.getElementById('loader');
    loader.style.display = "flex";
    loader.style.zIndex = 1;
    $.post( "/finish", {}, async function( data ) {
      console.log(data);
      ajax_post("/reboot", {});
      // Wait until cait is done booting up.
      await sleep(60000);
      var i;
      for (i = 0; i < 3; i++) {
        if (serverReachable(hostname)) {
          // Redirect to new hostname
          window.location.href = url;
        }
        else {
          console.log("Not done rebooting yet");
          await sleep(10000);
        }
      }
    });
  });
}
