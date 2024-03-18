let count = 0;
//Used to check username and password
//If succesful log in -> Home
//If not succesful -> stay of log in page
function checkCredentials() {
    
    // package data in a JSON object
    const data_d = {'email': 'owner@email.com', 'password': 'password'};
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    data_d['email'] = email;
    data_d['password'] = password;
    // SEND DATA TO SERVER VIA jQuery.ajax({})
    jQuery.ajax({
        url: "/processlogin",
        data: data_d,
        type: "POST",
        success:function(retruned_data){
              retruned_data = JSON.parse(retruned_data);
              // if log in succesful
              if(retruned_data.success){
                window.location.href = "/home";
              }
              // if log in no succesful
              else{
                count = count + 1;
                document.getElementById('failure').innerText = "Failed Log-In Attempts: " + count;
              }
            }
    });
}

//Used to create an account, given an input of a username and password
//If creation succesful -> login page
//If creation unsuccesful -> stay on creation page and give warning 
function CreateAccount() {
    // package data in a JSON object
    const data_d = {'email': 'owner@email.com', 'password': 'password'};
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    data_d['email'] = email;
    data_d['password'] = password;

    // SEND DATA TO SERVER VIA jQuery.ajax({})
    jQuery.ajax({
        url: "/createaccount",
        data: data_d,
        type: "POST",
        success:function(retruned_data){
              retruned_data = JSON.parse(retruned_data);
              if(retruned_data.success){
                window.location.href = "/login";
              }
              else{
                count = count + 1;
                document.getElementById('failure').innerText = "Email is already in use. Attempts: " + count;
              }
            }
    });
}