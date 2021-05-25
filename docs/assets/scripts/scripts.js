function myFunction(id) {

    var tags = document.getElementsByClassName('tag');
    for (var i = 0; i < tags.length; i ++) {
        tags[i].style.display = 'none';
    }

    document.getElementById(id).style.display = "block";

  }

// $(document).ready(function () {
//     getContent();
// });
// $(window).bind('hashchange', function (e) {
//     getContent();
// });
// document.ready(function () {getContent();});
// window.bind('hashchange', function (e) {getContent();});

// window.onload = getContent();
window.addEventListener('load', function () {
  getContent()
})

function getContent() {
    var url = window.location.toString();
    var hash = url.substring(url.indexOf('#')+1);

  // alert(url);
  alert('tag_' + hash);

  var tags = document.getElementsByClassName('tag');
  for (var i = 0; i < tags.length; i ++) {
      tags[i].style.display = 'none';
  }
  document.getElementById('tag_' + hash).style.display = "block";
}