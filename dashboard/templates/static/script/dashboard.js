$(document).ready(function() {
    var dropZone = document.getElementById('dropzone');
	dropZone.addEventListener("dragenter", handleDragEnter, false);
    dropZone.addEventListener("dragleave", handleDragLeave, false);
	dropZone.addEventListener('drop', handleFileSelect, false);
});

$(document).bind('drop dragover', function (e) {
    e.preventDefault();
});

function goToMenu() {
  $('#mainMenu').show();
  $("#createNewMeme").hide();
  $('#backBtnDiv').hide();
  $("#insufficientPerms").hide();

  document.getElementById('serverList').innerHTML = '';
};

/* When the user clicks on the button,
toggle between hiding and showing the dropdown content */
function goToCreateNew() {
  $('#mainMenu').hide();
  $("#loading").show();
  $.getJSON("/guilds-create", function(data) {
    $("#loading").hide();
    if (data.length>0) {
        var serverList = document.getElementById('serverList');
        populateServerList(serverList, data);
        $("#createNewMeme").show();
        $('#backBtnDiv').show();
    } else {
        $("#insufficientPerms").show();
        $('#backBtnDiv').show();
    }
  });
};

function populateServerList(serverListElement, data) {
    for (var i in data) {
        var guild = data[i];
        var img = document.createElement("img");
        if (guild['icon'] != null) {
            img.src ="https://cdn.discordapp.com/icons/" + guild['id'] + "/" + guild['icon'];
        } else {
        // If a server has no icon, draw one
            var matches = guild['name'].match(/\b(\w)/g);
            var acronym = matches.join('');
            var canvas = document.createElement("canvas");
            canvas.width = 64;
            canvas.height = 64;
            var ctx=canvas.getContext("2d");
            ctx.fillStyle = "rgb(47, 49, 54)";
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = "rgb(184, 186, 189)";
            ctx.font="22px Arial";
            ctx.textAlign = "center";
            ctx.fillText(acronym,32,38);
            img.src = ctx.canvas.toDataURL();
        }
        img.id = guild['id'];
        img.title = guild['name'];
        img.classList.add('discord-avatar');
        img.classList.add('server-icon');
        img.classList.add('available'); // TODO No restrictions for dev purpopses
        img.onclick = selectServer;
        serverListElement.appendChild(img);

    }
}

function selectServer(event) {
    var element = event.target;
    if (element.classList.contains("available")) {
        if (element.classList.contains("selected")) {
            element.classList.remove("selected");
        } else {
            element.classList.add("selected");
        }
    }
}

/* When the user clicks on the button,
toggle between hiding and showing the dropdown content */
function handleDragEnter() {
    var dropZone = document.getElementById("dropzone");
    dropZone.classList.add("highlight");
};

/* When the user clicks on the button,
toggle between hiding and showing the dropdown content */
function handleDragLeave() {
    console.log("leave");
    var dropZone = document.getElementById("dropzone");
    dropZone.classList.remove("highlight");
};