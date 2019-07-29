var list = document.querySelectorAll("h2,h3"); // get all h1 & h2
var tocArr = [], cur; // holds the structure of the ToC
for (var i = 0; i < list.length; i++) {
  var e = list[i];
  if (e.tagName == "H2") {
    // for an h2, create a new heading entry (with a blank child list)
    tocArr.push({text:e.textContent, children:(cur=[]), id: e.id});
  } else {
    // for an h3, add it to the current h1's child list
    cur.push({text: e.textContent, id: e.id});
  }
}
console.log(tocArr);

// build the DOM nodes
var toc = document.getElementById('table-of-contents');
for (var i in tocArr) {
  var li = document.createElement("li");
  var a = document.createElement("a");
  a.href = "#" + tocArr[i].id;
  a.textContent = tocArr[i].text;
  li.appendChild(a);

  // NEW: add a sub-ul for any subheadings
  var ch = tocArr[i].children;
  if (ch.length > 0) {
    var ul = document.createElement("ul");
    for (var i2 in ch) {
      var li2 = document.createElement("li");
      var a2 = document.createElement("a");
      a2.href = "#" + ch[i2].id;
      a2.textContent = ch[i2].text;
      li2.appendChild(a2);
      ul.appendChild(li2);
    }
    li.appendChild(ul);
  }

  toc.appendChild(li);
}