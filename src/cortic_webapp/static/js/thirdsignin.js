/* 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, December 2019
  
 */

async function ajax_post(url, data) {
    return $.ajax({
      url: url,
      type: 'POST',
      data: data
    });
}

async function upload_account() {
  const account_file = document.getElementById("account_json");
  const reader = new FileReader();
  reader.addEventListener('load', async (event) => {
    const result = await ajax_post("/upload_account", {'account_credentials': event.target.result});
    console.log(result)
    url = window.location.protocol + "//" +  window.location.hostname + "/congrats";
    window.location.href = url;

  });
  reader.readAsText(account_file.files[0]);
}