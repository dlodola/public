function myFunction() {
    // var x = document.getElementById("myDIV");
    // if (x.style.display === "none") {
    //   x.style.display = "block";
    // } else {
    //   x.style.display = "none";
    // }

    var tags = document.getElementsByClassName('tag');
    for (var i = 0; i < tags.length; i ++) {
        // tags[i].style.display = 'none';
        if (tags[i].style.display === "none") {
          tags[i].style.display = "block";
        } else {
          tags[i].style.display = "none";
        }
    }

  }