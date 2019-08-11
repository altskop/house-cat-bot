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

        if (isManage){
            img.onclick = chooseServer;
        } else {
            img.onclick = selectServer;
        }

        div.appendChild(img);

        if (!isManage){
            if (guild['full'] == true) {
                var txt = document.createElement("p");
                txt.innerHTML = "FULL";
                div.appendChild(txt);
                img.classList.add('full');
            } else {
                img.classList.add('available');
            }
        } else {
            img.classList.add('available');
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
    return element.id;
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
          function(result) { loadEditor(url, true); },
          function(error) { element.classList.add('notfound'); }
        );
    }
}

function readImage(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();

        reader.onload = function (e) {
            loadEditor(e.target.result, true);
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

function chooseServer(event) {
    $('img', $('#manageServerList')).each(function () {
        this.classList.remove("selected");
    });
    id = selectServer(event);
    getGuildTemplates(id);
}

function getChosenServer(){
    var list = [];
    var serverList = document.getElementById('serverList');
    $('img', $('#manageServerList')).each(function () {
        if (this.classList.contains("selected")) {
            list.push(this.id); //log every element found to console output
            return list;
        }
    });
    return list;
}

function getGuildTemplates(id){
    $("#manageTemplatesView").hide();
    $("#noTemplatesFound").hide();
    $("#createNewMeme").hide();
    // Disable navigation prompt
    window.onbeforeunload = null;
    previewCanvas = document.getElementById('managePreviewCanvas');
    previewCanvas.width = 0;
    previewCanvas.height = 0;
    $("#loading").show();
    $.getJSON("/guild-templates",
        {"id": id},
        function(data) {
            $("#loading").hide();
            if (data.length>0) {
                $("#manageTemplatesView").show();
                renderTemplatesList(data, id);
            } else {
                $("#noTemplatesFound").show();
            }
          });
}

function renderTemplatesList(list, guild){
    var fieldsList = document.getElementById('templatesList');
    fieldsList.innerHTML = "";

    for (var i in list){
        var template = list[i];
        var li = document.createElement('li');
        li.name = template['name'];
        li.guild = guild;
        li.onclick = function(){
             $('li', fieldsList).each(function () {
                this.classList.remove("selected");
            });
            this.classList.add("selected");
            fetchManagePreviewImage(this.name, this.guild);
        }

        var b = document.createElement('b');
        b.innerHTML = template["name"];
        li.appendChild(b);

        var div = document.createElement('div');

        var span = document.createElement('span');
        span.innerHTML = "by "+template["author"];
        div.appendChild(span);


        var editButton = document.createElement('span');
        editButton.classList.add("copy-button");
        editButton.innerHTML = "&#9998";
        editButton.onclick = function() { event.stopPropagation(); this.disabled=true; editTemplate($(this).closest('li')); };
        div.appendChild(editButton);

        var deleteButton = document.createElement('span');
        deleteButton.classList.add("delete-button");
        deleteButton.innerHTML = "&#10006";
        deleteButton.onclick = function() { event.stopPropagation(); this.disabled=true; deleteTemplate($(this).closest('li')); };
        div.appendChild(deleteButton);

        li.appendChild(div);
        fieldsList.appendChild(li);
    }
}

function fetchManagePreviewImage(name, guild){
    $('#manageTemplateDisplay > .button-loader').remove();
    previewDisplayDiv = document.getElementById('manageTemplateDisplay');
    previewDisplayDiv.style.width = "300px";
    previewDisplayDiv.style.height = "300px";
    loader = document.createElement("div");
    loader.classList.add("button-loader");
    previewDisplayDiv.appendChild(loader);
    previewCanvas = document.getElementById('managePreviewCanvas');
    previewCanvas.width = 0;
    previewCanvas.height = 0;
    $.get("/preview",
             {"name": name, "guild": guild},
             function(data) {
                var img = new Image();
                img.onload = function () {
	                previewContext = previewCanvas.getContext('2d');
                    previewCanvas.width = this.width;
                    previewCanvas.height = this.height;
                    previewContext.drawImage(this,0,0,this.width,this.height);

                    previewDisplayDiv.style.width = this.width+"px";
                    previewDisplayDiv.style.height = this.height+"px";
                    $('#manageTemplateDisplay > .button-loader').remove();
                };

                img.src = "data:image/png;base64,"+data;
            }).fail(function(data) {
                $('#manageTemplateDisplay > .button-loader').remove();
            });
}

function deleteTemplate(element){
    element = element.get(0);
    document.body.style.cursor = "progress";
    $.ajax({
        url: "/delete",
        type: 'GET',
        data: {"name": element.name, "guild": element.guild},
        success: function(data) {
            element.remove();
            document.body.style.cursor = "auto";
        },
        error: function(data){
            document.body.style.cursor = "auto";
        }
        });

}

function editTemplate(element){
    element = element.get(0);
    $("#loading").show();
    $("#manageTemplatesView").hide();
    $.getJSON("/template",
        {"name": element.name, "guild": element.guild},
         function(data) {
           $("#createNewMeme").show();
           $("#serverListContainer").hide();
           $("#loading").hide();
           loadEditor("data:image/png;base64,"+data['image'], false);
           editor.fields = data['metadata']['fields'];
           editor.oldName = element.name;
           $("#templateName").val(element.name);
           refreshFieldsList();
    });
}