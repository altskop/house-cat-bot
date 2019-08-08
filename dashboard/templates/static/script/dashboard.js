$(document).ready(function() {
    var dropZone = document.getElementById('dropzone');
	dropZone.addEventListener("dragenter", handleDragEnter, false);
    dropZone.addEventListener("dragleave", handleDragLeave, false);
	dropZone.addEventListener('drop', handleFileSelect, false);

    var inputField = document.getElementById('getFileField');
    inputField.addEventListener('paste', handlePasteEvent, false);
    inputField.addEventListener('input', handleUrlFieldUpdate, false);
});

function getFileInput() {
    document.getElementById('getFileInput').click();
}

$(document).bind('drop dragover', function (e) {
    e.preventDefault();
});

/* When the user clicks on the button,
toggle between hiding and showing the dropdown content */
function goToCreateNew() {
  $('#mainMenu').hide();
  $("#loading").show();
  $('#editor').hide();
  $.getJSON("/guilds-create", function(data) {
    $("#loading").hide();
    if (data.length>0) {
        var serverList = document.getElementById('serverList');
        populateServerList(serverList, data, false);
        $("#createNewMeme").show();
        $('#backBtnDiv').show();
    } else {
        $("#insufficientPerms").show();
        $('#backBtnDiv').show();
    }
  });
};

function populateServerList(serverListElement, data, isManage) {
    for (var i in data) {
        var guild = data[i];
        var div = document.createElement("div");
        div.classList.add("container");
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
         // TODO No restrictions for dev purpopses
        if (isManage){
            img.onclick = chooseServer;
        } else {
            img.onclick = selectServer;
        }

        div.appendChild(img);
        // TODO append FULL on top of image and add a "full" class if server is full
        if (!isManage){
            if (guild['full'] == true) {
                var txt = document.createElement("p");
                txt.innerHTML = "FULL";
                div.appendChild(txt);
                img.classList.add('full');
            } else {
                img.classList.add('available');
            }
        }
        serverListElement.appendChild(div);

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

function chooseServer(event) {
    $('img', $('#manageServerList')).each(function () {
        this.classList.remove("selected");
    });
    selectServer(event);
}

function getSelectedServers(){
    var list = [];
    var serverList = document.getElementById('serverList');
    $('img', $('#serverList')).each(function () {
        if (this.classList.contains("selected")) {
            list.push(this.id); //log every element found to console output
        }
    });
    return list;
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

function handleFileSelect(evt) {
    var dataTransfer = evt.dataTransfer; // FileList object.
    readImage(dataTransfer);
}

function handlePasteEvent(evt) {
    readImage(evt.clipboardData);
}

function handleUrlFieldUpdate(e) {
    var element = e.target;
    element.classList.remove("notfound");
    var url = element.value;
    if (url.startsWith("http://") || url.startsWith("https://")){
        isUrlAnImage(url, 2000).then(
          function(result) { loadEditor(url); },
          function(error) { element.classList.add('notfound'); }
        );
    }
}

function readImage(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();

        reader.onload = function (e) {
            loadEditor(e.target.result);
        };

        reader.readAsDataURL(input.files[0]);
    }
}

function isUrlAnImage(url, timeoutT) {
    return new Promise(function (resolve, reject) {
        var timeout = timeoutT || 5000;
        var timer, img = new Image();
        img.onerror = img.onabort = function () {
            console.log('error');
            clearTimeout(timer);
            reject("error");
        };
        img.onload = function () {
            console.log('success');
            clearTimeout(timer);
            resolve("success");
        };
        timer = setTimeout(function () {
            // reset .src to invalid URL so it stops previous
            // loading, but doesn't trigger new load
            img.src = "//!!!!/test.jpg";
            console.log('error');
            reject("timeout");
        }, timeout);
        img.src = url;
    });
}



// MANAGE TEMPLATES


/* When the user clicks on the button,
toggle between hiding and showing the dropdown content */
function goToManage() {
  $('#mainMenu').hide();
  $("#loading").show();
  $.getJSON("/guilds-manage", function(data) {
    $("#loading").hide();
    if (data.length>0) {
        var serverList = document.getElementById('manageServerList');
        populateServerList(serverList, data, true);
        $("#manageMemes").show();
        $('#backBtnDiv').show();
    } else {
        $("#insufficientPerms").show();
        $('#backBtnDiv').show();
    }
  });
};