// function inspiration from https://www.w3schools.com/howto/tryit.asp?filename=tryhow_js_topnav
//Changes the class name of navbar
//Due to the change new styles are applied to navbar's children
//These changes hide/show the children (the children are the menu items)
function showMenuItems() {
  var x = document.getElementById("navBar");
  if (x.className === "navBar") {
    x.className += " show";
  } 
  else {
    x.className = "navBar";
  }
}


//Event listener for clicking on the hamburger icon
var hamburger = document.getElementById("hamburger");
hamburger.addEventListener("click", showMenuItems);