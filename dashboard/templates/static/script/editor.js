var editor;
var delayTimer;

//$(document).ready(function() { // TODO debug function remove later
//    loadEditor("https://upload.wikimedia.org/wikipedia/en/8/8b/Purplecom.jpg");
//});

$( function() {
    $( "#fieldsList" ).sortable({
        start: function(event, ui) {
            var start_pos = ui.item.index();
            ui.item.data('start_pos', start_pos);
        },
        change: function(event, ui) {
        },
        update: function(event, ui) {
            var start_pos = ui.item.data('start_pos');
            var index = ui.item.index();
            editor.changeFieldIndex(start_pos, index);
            refreshFieldsList();
        }
    });
    $( "#fieldsList" ).disableSelection();
  } );

function loadEditor(url) {
    var img = new Image();

    img.onload = function () {
        loadImage(this);
    };

    editor = new Editor();

    img.setAttribute('crossOrigin', 'anonymous');
    img.src = url;

    $('#imageLoadingInputs').hide();
    $('#editor').show();

    // Enable navigation prompt TODO reenable
//    window.onbeforeunload = function() {
//        return true;
//    };
}

class Color {
    constructor(input){
        this.value =  input.match(/[A-Za-z0-9]{2}/g).map(function(v) { return parseInt(v, 16) }).join(",");
    }

    get(opacity=0.5){
        return "rgba("+this.value+","+opacity+")"
    }
    getText(){
        return "white";
    }
}

class Editor {
    constructor() {
        this.canvas = document.getElementById('templateImg');
	    this.context = this.canvas.getContext('2d');
        this.drawCanvas = document.getElementById('fieldsCanvas');
        this.drawContext = this.drawCanvas.getContext('2d');
        this.fields = [];
        this.selectedField = null;
        // JavaScript seems to not have enums, so I'll keep the state as a string for now.
        // TODO perhaps there is a better way?
        // States: "none" "drawing" "dragging" "resizing"
        this.state = "none";
        this.currentField = {};
        this.mouseClick = null;
        this.resizer = new Resizer();
    };

    reset(){
        this.fields = [];
    };

    setEditorFieldsColor(input){
        this.drawColor = new Color(input);
        this.render();
    }

    render(){
        this.drawContext.clearRect(0,0,this.canvas.width,this.canvas.height);
        for (var i in this.fields) {
            var field = this.fields[i];
            this.drawRect(field.x, field.y, field.w, field.h, i);
        };
    };

    changeFieldIndex(fromIndex, toIndex){
        var field = this.fields[fromIndex];
        this.fields.splice(fromIndex, 1);
        this.fields.splice(toIndex, 0, field);
        this.render();
    }

    drawRect(x, y, w, h, i, isNew=false){
        if (isNew) {
            this.drawContext.fillStyle = this.drawColor.get(0.2);
            this.drawContext.fillRect(x, y, w, h);
        } else {
            this.drawContext.fillStyle = this.drawColor.get();
            this.drawContext.fillRect(x, y, w, h);
            this.drawContext.clearRect(x+3, y+3, w-6, h-6);
            this.drawContext.fillStyle = this.drawColor.get(0.35);
            this.drawContext.fillRect(x+3, y+3, w-6, h-6);
            this.drawContext.fillStyle = this.drawColor.getText();
            this.drawContext.font="22px Arial";
            this.drawContext.textAlign = "center";
            this.drawContext.fillText(+i+1,x+(w/2),y+(h/2)+8);
        }
    }

    getFieldAtLoc(x, y){
        for (var i = this.fields.length-1; i >= 0; i--) { // Loop in reverse so that the higher fields will be prioritized
            var field = editor.fields[i];
            var marginOut = 5;
            if (field.x - marginOut < x &&
                    x < field.x+field.w+marginOut &&
                     field.y-marginOut < y &&
                      y < field.y+field.h+marginOut){
                this.selectedField = {};
                this.selectedField.index = i;
                this.selectedField.mode = "body";
                this.selectedField.startX = field.x;
                this.selectedField.startY = field.y;
                this.selectedField.startW = field.w;
                this.selectedField.startH = field.h;
                var marginX = Math.max(marginOut, field.w*0.1);
                var marginY = Math.max(marginOut, field.h*0.1);
                if (y < field.y+marginY && x > field.x+field.w-marginX) {
                    this.selectedField.mode = "top-right";
                } else if (y < field.y+marginY && x < field.x+marginX){
                    this.selectedField.mode = "top-left";
                } else if (y > field.y+field.h-marginY && x > field.x+field.w-marginX){
                    this.selectedField.mode = "bottom-right";
                } else if (y > field.y+field.h-marginY && x < field.x+marginX){
                    this.selectedField.mode = "bottom-left";
                } else if (y < field.y+marginY) {
                    this.selectedField.mode = "top";
                } else if (y > field.y+field.h-marginY) {
                    this.selectedField.mode = "bottom";
                } else if (x > field.x+field.w-marginX) {
                    this.selectedField.mode = "right";
                } else if (x < field.x+marginX) {
                    this.selectedField.mode = "left";
                }
                return;
            }
        }
        this.selectedField = null;
        return null;
    }

    isOnField(x, y){
        this.getFieldAtLoc(x, y);
        if (this.selectedField != null){
            return true;
        }
        return false;
    }

    addNewField(w, h){

        if (Math.abs(w) < 15 && Math.abs(h) < 9) {
            return;
        }

        var field = {};
        field.x = this.mouseClick.x;
        field.y = this.mouseClick.y;
        field.w = w;
        field.h = h;
        field.font = $("#fontSelect :selected").val();

        var defaultColor;
        if (field.font == "normal") {
            defaultColor = "#000000";
        } else {
            defaultColor = "#FFFFFF";
        }
        field.color = defaultColor;

        field.align = "center";
        this.constrainField(field);
        this.fields.push(field);
        this.mouseClick = null;
        refreshFieldsList();
    }

    deleteField(index){
        resetMainNotification();
        this.fields.splice(index, 1);
        this.render();
        refreshFieldsList();
    }

    copyField(index){
        if (this.fields.length < 20) {
            var fieldCopy = Object.assign({}, this.fields[index]);
            this.fields.push(fieldCopy);
            this.render();
            refreshFieldsList();
        } else {
            setMainNotification("You can not add more than 20 fields.", false);
        }
    }

    setFieldFontType(index, type){
        this.fields[index].font = type;
    }

    setFieldAlign(index, align){
        this.fields[index].align = align;
    }

    setFieldColor(index, color){
        this.fields[index].color = color;
    }

    setAllFieldsFontType(type){
        var defaultColor;
        if (type == "normal") {
            defaultColor = "#000000";
        } else {
            defaultColor = "#FFFFFF";
        }
        for (var i in this.fields) {
            var field = editor.fields[i];
            field.font = type;
            field.color = defaultColor;
        }
    }

    moveField(newX, newY, newW, newH){
        var field = this.fields[this.selectedField.index];
        this.constrainField(field, newX, newY, newW, newH);
    }

    finishResizing(){
        var field = this.fields[this.selectedField.index];
        if (field.w < 15) {
            field.w = 15;
        }
        if (field.h < 9) {
            field.h = 9;
        }
        this.constrainField(field);
    }

    constrainField(field, newX, newY, newW, newH){
        if (newX == null) {newX = field.x;}
        if (newY == null) {newY = field.y;}
        if (newW == null) {newW = field.w;}
        if (newH == null) {newH = field.h;}

        // invert if necessary (first point has to always point to top-left corner)

        if (newW < 0) {
            newW = Math.abs(newW);
            newX -= newW;
        }
        if (newH < 0) {
            newH = Math.abs(newH);
            newY -= newH;
        }

        // Restrict X movement by canvas (snap to edges if out)
        if (newX + newW <= this.canvas.width && newX >= 0){
            field.x = newX;
            field.w = newW;
        }
        else if (newX + newW > this.canvas.width){
            field.x = this.canvas.width - newW;
            field.w = newW;
        }
        else if (newX < 0){
            field.x = 0;
            field.w = newW;
        }

        // Restrict Y movement by canvas (snap to edges if out)
        if (newY + newH <= this.canvas.height && newY >= 0){
            field.y = newY;
            field.h = newH;
        }
        else if (newY + newH > this.canvas.height){
            field.y = this.canvas.height - newH;
            field.h = newH;
        }
        else if (newY < 0){
            field.y = 0;
            field.h = newH;
        }
    }
}


function refreshFieldsList(){
    var fieldsList = document.getElementById('fieldsList');
    fieldsList.innerHTML = "";

    for (var i in editor.fields){
        var field = editor.fields[i];
        var li = document.createElement('li');

        var b = document.createElement('b');
        b.innerHTML = (+i+1)+". ";
        li.appendChild(b);

        var alignLabel = document.createElement('span');
        alignLabel.innerHTML = "Alignment: ";
        li.appendChild(alignLabel);

        var selectAlign = createSelectAlignElement();
        selectAlign.fieldId = i;
        selectAlign.onchange = function() { editor.setFieldAlign(this.fieldId, this.value); };
        li.appendChild(selectAlign);

        if (!document.getElementById('sameFontCheckbox').checked){
            var fontLabel = document.createElement('span');
            fontLabel.innerHTML = " Font: ";
            li.appendChild(fontLabel);

            var select = createSelectFontElement();
            select.value = $("#fontSelect :selected").val();
            select.fieldId = i;
            select.onchange = function() { editor.setFieldFontType(this.fieldId, this.value); };
            li.appendChild(select);
        }

        var colorLabel = document.createElement('span');
        colorLabel.innerHTML = "Color: ";
        li.appendChild(colorLabel);

        var colorInput = document.createElement('input');
        colorInput.type = "color";
        colorInput.classList.add("color");
        colorInput.fieldId = i;
        colorInput.value = field.color;
        colorInput.onchange = function() { editor.setFieldColor(this.fieldId, this.value); };
        li.appendChild(colorInput);

        var copyButton = document.createElement('span');
        copyButton.classList.add("copy-button");
        copyButton.innerHTML = "&#x2398";
        copyButton.value = i;
        copyButton.onclick = function() { editor.copyField(this.value); };
        li.appendChild(copyButton);

        var deleteButton = document.createElement('span');
        deleteButton.classList.add("delete-button");
        deleteButton.innerHTML = "&#10006";
        deleteButton.value = i;
        deleteButton.onclick = function() { editor.deleteField(this.value); };
        li.appendChild(deleteButton);

        fieldsList.appendChild(li);
    }
}

function createSelectFontElement(){
    var select = document.createElement('select');
    select.classList.add('discord-select');
    var optionRegular = document.createElement('option');
    optionRegular.value = "normal";
    optionRegular.innerHTML = "Regular";
    var optionBold = document.createElement('option');
    optionBold.value = "bold";
    optionBold.innerHTML = "Bold (with thick stroke)";
    select.appendChild(optionRegular);
    select.appendChild(optionBold);
    return select;
}

function createSelectAlignElement(){
    var select = document.createElement('select');
    select.classList.add('discord-select');
    var optionCenter = document.createElement('option');
    optionCenter.value = "center";
    optionCenter.innerHTML = "Center";
    var optionLeft = document.createElement('option');
    optionLeft.value = "left";
    optionLeft.innerHTML = "Left";
    var optionRight = document.createElement('option');
    optionRight.value = "right";
    optionRight.innerHTML = "Right";
    select.appendChild(optionCenter);
    select.appendChild(optionLeft);
    select.appendChild(optionRight);
    return select;
}

class Resizer {
    resize(e) {
        var w = e.offsetX - editor.mouseClick.x;
        var h = e.offsetY - editor.mouseClick.y;
        var selectedField = editor.fields[editor.selectedField.index];
        if (editor.selectedField.mode == "top"){
            this.resizeTop(h);
        } else if (editor.selectedField.mode == "bottom") {
            this.resizeBottom(h);
        } else if (editor.selectedField.mode == "right") {
            this.resizeRight(w);
        } else if (editor.selectedField.mode == "left"){
            this.resizeLeft(w);
        } else if (editor.selectedField.mode == "top-left"){
            this.resizeTop(h);
            this.resizeLeft(w);
        } else if (editor.selectedField.mode == "top-right"){
            this.resizeTop(h);
            this.resizeRight(w);
        } else if (editor.selectedField.mode == "bottom-left"){
            this.resizeBottom(h);
            this.resizeLeft(w);
        } else if (editor.selectedField.mode == "bottom-right"){
            this.resizeBottom(h);
            this.resizeRight(w);
        }
    }

    resizeTop(h){
        this.resizeOnYAxis(this.resizeTopOrLeft, h);
    }

    resizeBottom(h){
        this.resizeOnYAxis(this.resizeBottomOrRight, h);
    }

    resizeRight(w){
        this.resizeOnXAxis(this.resizeBottomOrRight, w);
    }

    resizeLeft(w){
        this.resizeOnXAxis(this.resizeTopOrLeft, w);
    }

    resizeOnXAxis(f, w){
        var result = f(editor.selectedField.startX, editor.selectedField.startW, w);
        var newX = result[0];
        var newW = result[1];

        editor.moveField(newX, null, newW, null);
    }

    resizeOnYAxis(f, h){
        var result = f(editor.selectedField.startY, editor.selectedField.startH, h);
        var newY = result[0];
        var newH = result[1];

        editor.moveField(null, newY, null, newH);
    }

    resizeTopOrLeft(a, c, deltaC){
        var newA = a + deltaC;
        var newC = c - deltaC;
        return [newA, newC];
    }

    resizeBottomOrRight(a, c, deltaC){
        var newC = c + deltaC;
        var newA = null;
        if (newC < 0){
            newA = a + newC;
            newC = a - newA;
        }
        return [newA, newC];
    }
}

function mouseDown(e){
    resetMainNotification();
    var x = e.offsetX;
    var y = e.offsetY;
    if (editor.state == "none"){
        editor.mouseClick = {x: x, y: y};
        if (editor.selectedField == null) {
            if (editor.fields.length < 20){
                editor.state = "drawing";
                document.body.style.cursor = "crosshair"; // Reference for cursor styles: https://www.w3schools.com/jsref/prop_style_cursor.asp
            } else {
                setMainNotification("You can not add more than 20 fields.", false);
            }
        } else if (editor.selectedField.mode == "body"){
            editor.state = "dragging";
            var selectedField = editor.fields[editor.selectedField.index];
        } else {
            editor.state = "resizing";
        }
    }
};

function mouseMove(e) {
  if (editor.state == "drawing") {
    editor.render();
    var w = e.offsetX - editor.mouseClick.x;
    var h = e.offsetY - editor.mouseClick.y ;
    editor.drawRect(editor.mouseClick.x, editor.mouseClick.y, w, h, null, true);
  }
  else if (editor.state == "dragging") {
        editor.render();
        var w = e.offsetX - editor.mouseClick.x;
        var h = e.offsetY - editor.mouseClick.y;
        var newX = editor.selectedField.startX + w;
        var newY = editor.selectedField.startY + h;

        editor.moveField(newX, newY);
  }
  else if (editor.state == "resizing") {
        editor.resizer.resize(e);
        editor.render();
  } else {
      if (editor.isOnField(e.offsetX, e.offsetY)){
        if (editor.selectedField.mode == "body"){
            document.body.style.cursor = "move";
        } else if (editor.selectedField.mode == "top" || editor.selectedField.mode == "bottom") {
            document.body.style.cursor = "ns-resize";
        } else if (editor.selectedField.mode == "left" || editor.selectedField.mode == "right") {
            document.body.style.cursor = "ew-resize";
        } else if (editor.selectedField.mode == "top-left" || editor.selectedField.mode == "bottom-right") {
            document.body.style.cursor = "nwse-resize";
        } else if (editor.selectedField.mode == "top-right" || editor.selectedField.mode == "bottom-left") {
            document.body.style.cursor = "nesw-resize";
        }

      } else {
        document.body.style.cursor = "auto";
      }
  }
};

function mouseUp(e) {
    if (editor.state != "none"){
        editor.lastMousePos = null;
        if (editor.state == "drawing"){
            var w = e.offsetX - editor.mouseClick.x;
            var h = e.offsetY - editor.mouseClick.y;
            editor.addNewField(w, h);

            document.body.style.cursor = "auto";
        } else if (editor.state == "dragging") {

        } else if (editor.state == "resizing") {
            editor.finishResizing();
        }
        editor.render();
    }
    editor.state = "none";
};


function mouseOut(e){
    var x = e.offsetX;
    var y = e.offsetY;
    editor.lastMousePos = {offsetX: x, offsetY: y};
    document.body.style.cursor = "auto";
}

function mouseUpOutsideOfCanvas(){
    if (editor.state != "none") {
        mouseUp(editor.lastMousePos);
    }
}

function toggleFontSelection(checkbox) {
    if (checkbox.checked) {
        $('#fontSelectionMenu').show();
        changeAllFont();
        refreshFieldsList();
    } else {
        $('#fontSelectionMenu').hide();
        refreshFieldsList();
    }
}


function changeAllFont(){
    editor.setAllFieldsFontType($("#fontSelect :selected").val());
    refreshFieldsList();
}

function verifyNameUniqueness(name, servers, element, inputNotification){

    clearTimeout(delayTimer);
    delayTimer = setTimeout(function() {
        $.get("/check-template-name",
             JSON.stringify({"name": name, "guilds": servers}),
             function(data) {
               element.classList.add("success");
             }
           ).fail(function(data) {
                inputNotification.innerHTML = "This template name is already in use in one of the selected servers.";
                inputNotification.classList.add("fail");
                element.classList.add("notfound");
            });
    }, 1000); // Will do the ajax stuff after 1000 ms, or 1 s

}


function verifyTemplateName(e){
    var element = e.target;
    element.classList.remove("notfound");
    element.classList.remove("success");
    var text = element.value;

    var inputNotification = document.getElementById('inputNotification');
    inputNotification.classList.remove("fail");
    inputNotification.classList.remove("success");
    inputNotification.innerHTML = "";

    if (text.length == 0){
        return;
    }

    var regex = /^(?!.*(-)-*\1)[a-zA-Z][a-zA-Z0-9-]*$/i; // tests https://regex101.com/r/oGiiAx/1
    if (!text.match(regex)) {
        element.classList.add("notfound");
        inputNotification.innerHTML = "A template name has to:<br> - start with a letter<br> - contain only letters, numbers and dashes<br> - dashes can't be repeated in a row (like --).";
        inputNotification.classList.add("fail");
        return;
    }

    if (text.length>2) {
        servers = getSelectedServers()
        if (servers.length > 0){
            verifyNameUniqueness(text, servers, element, inputNotification);
        }
    }
}

function verifyTemplateNameSize(){
    var element = document.getElementById("templateName");
    var text = element.value;

    var inputNotification = document.getElementById('inputNotification');
    inputNotification.classList.remove("fail");
    inputNotification.classList.remove("success");
    inputNotification.innerHTML = "";

    if (text.length < 3){
        element.classList.add("notfound");
        inputNotification.innerHTML = "Template name has to be longer than 3 characters.";
        inputNotification.classList.add("fail");
        return false;
    } else if (text.length > 21) {
        // Realistically shouldn't fire but who knows
        element.classList.add("notfound");
        inputNotification.innerHTML = "Template name has to be no longer than 21 characters.";
        inputNotification.classList.add("fail");
        return false;
    }
    return true;
}

function verifyNumberOfFields(){
    if (editor.fields.length > 0){
        return true;
    }
    setMainNotification("Need at least 1 field in the template", false);
    return false;
}

function verifySelectedServers(){
    console.log(getSelectedServers());
    if (getSelectedServers().length > 0){
        return true;
    }
    setMainNotification("Select at least 1 server to which you'd like to upload your template", false);
    return false;
}

function setMainNotification(text, isSuccess){
    resetMainNotification();
    var mainNotification = document.getElementById('mainNotification');
    if (isSuccess) {
        mainNotification.classList.add("success");
    } else {
        mainNotification.classList.add("fail");
    }
    mainNotification.innerHTML = text;
}

function resetMainNotification(){
    var mainNotification = document.getElementById('mainNotification');
    mainNotification.classList.remove("fail");
    mainNotification.classList.remove("success");
    mainNotification.innerHTML = "";
}

function changeUploadBtnToLoading(btn){
    btn.disabled=true;
    btn.classList.add("loading");
    $('img', btn).each(function () {
        console.log(this); //log every element found to console output
        $(this).hide();
    });
    btn.innerHTML = "<div class=\"button-loader\"></div>" + btn.innerHTML
}

function changeUploadBtnToDefault(btn){
    btn.disabled=false;
    btn.classList.remove("loading");
    $('img', btn).each(function () {
        $(this).show();
    });
    $('div', btn).each(function () {
        this.remove();
    });
//    btn.innerHTML.replace("<div class=\"button-loader\"></div>", "");
}

function uploadTemplate(btn){
    if (verifyTemplateNameSize() && verifyNumberOfFields() && verifySelectedServers()){
        changeUploadBtnToLoading(btn);
       resetMainNotification();

        console.log('test');
        var json = {};
        json.name = document.getElementById("templateName").value;
        json.guilds = getSelectedServers();
        json.image = editor.canvas.toDataURL();
        json.metadata = {};
        json.metadata.fields = editor.fields;
        console.log(json);

        json = JSON.stringify(json);
        document.body.style.cursor = "progress";

        $.post("/create",
             json,
             function(data) {
               document.body.style.cursor = "auto";
               setMainNotification("Template created!", true);
               changeUploadBtnToDefault(btn)
             }
           ).fail(function(data) {
                document.body.style.cursor = "auto";
                setMainNotification(data.responseText, false);
                changeUploadBtnToDefault(btn)
            });
    }
}


function loadImage (img)
{
    console.log(img.width, img.height);
    size = setWidth(img.width, img.height, 600);
    console.log(size);
	editor.canvas.width = size.width;
	editor.canvas.height = size.height;

	editor.context.drawImage(img,0,0,size.width,size.height);

	editor.drawCanvas.width = size.width;
	editor.drawCanvas.height = size.height;
	editor.drawCanvas.top = -size.height;

	templateDisplay = document.getElementById('templateDisplay');
	templateDisplay.style.width = size.width+"px";
	templateDisplay.style.height = size.height+"px";
	templateDisplay.style.minWidth = size.width+"px";
	templateDisplay.style.minHeight = size.height+"px";

	editor.drawCanvas.addEventListener('mousedown', mouseDown, false);
    editor.drawCanvas.addEventListener('mouseup', mouseUp, false);
    editor.drawCanvas.addEventListener('mousemove', mouseMove, false);
    editor.drawCanvas.addEventListener('mouseout', mouseOut, false);
    document.addEventListener("mouseup", mouseUpOutsideOfCanvas, false);

    var editorFieldsColorInput = document.getElementById('editorFieldsColorInput');
    editor.setEditorFieldsColor(editorFieldsColorInput.value);
    editorFieldsColorInput.onchange = function() { editor.setEditorFieldsColor(this.value); };

    var templateNameField = document.getElementById('templateName');
    templateNameField.addEventListener('paste', verifyTemplateName, false);
    templateNameField.addEventListener('input', verifyTemplateName, false);
}

function setWidth(width, height, maxWidth) {
    if (width != maxWidth){
        var ratio = maxWidth / width;
        return { width: width*ratio, height: height*ratio };
    }
    return {width: width, height: height};
}