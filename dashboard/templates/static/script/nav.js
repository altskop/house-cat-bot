/* When the user clicks on the button,
toggle between hiding and showing the dropdown content */
function toggleProfileDropdown() {
  document.getElementById("profileDropdown").classList.toggle("show");
}

// Close the dropdown if the user clicks outside of it
window.onclick = function(e) {
  if (!document.getElementsByClassName('dropdown')[0].contains(e.target)) {
  var myDropdown = document.getElementById("profileDropdown");
    if (myDropdown.classList.contains('show')) {
      myDropdown.classList.remove('show');
    }
  }
}

function toggleMenu() {
  var x = document.getElementById("navLinks");
  var topRight = document.getElementsByClassName('topnav-right')[0] || document.getElementsByClassName('topnav-login')[0];
  if (x.className === "topnav-nav") {
    x.className += " responsive";
    topRight.className += " responsive";
  } else {
    x.className = "topnav-nav";
    topRight.className = topRight.className.replace(" responsive", "");
  }
}