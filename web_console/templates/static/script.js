var canvas;
var context;

var drawCanvas;
var drawContext;
var startX, endX, startY, endY;
var drawColor = "green";

var drag = false
var rect = {}

var squares = [];

var mouseIsDown = false;


function handleFileSelect(evt) {
    evt.stopPropagation();
    evt.preventDefault();

    var files = evt.dataTransfer.files; // FileList object.

    var reader = new FileReader();
      // Closure to capture the file information.
      reader.onload = (function(theFile) {
        return function(e) {
		  $('#image').attr('src', e.target.result).load(imageLoaded);
		  $('#stepOne').hide();
		  context.drawImage(document.getElementById("image"), 0, 0);
        };
      })(files[0]);

      // Read in the image file as a data URL.
      reader.readAsDataURL(files[0]);
  }



  function handleDragOver(evt) {
    evt.stopPropagation();
    evt.preventDefault();
    evt.dataTransfer.dropEffect = 'copy'; // Explicitly show this is a copy.
  }



$(document).ready(function() {
	canvas = document.getElementById('canvas');
	context = canvas.getContext('2d');
	
	drawCanvas = document.getElementById('drawCanvas');
	drawContext = drawCanvas.getContext('2d');

    var dropZone = document.getElementById('drop_zone');
	dropZone.addEventListener('dragover', handleDragOver, false);
	dropZone.addEventListener('drop', handleFileSelect, false);

	init();
	
	$('#submit').click(function() {
		setTimeout(function() {
		    var jsonData = {}
		    jsonData['name'] = document.getElementById('template-name').value;
		    var jsonPic = {}
		    jsonPic['data'] = canvas.toDataURL();

		    var jsonMetadata = {};
		    jsonMetadata['fields'] = []

		    var radios = document.getElementsByName('font');
            for (var i = 0, length = radios.length; i < length; i++)
                {
                if (radios[i].checked)
                    {
                    jsonMetadata['font'] = radios[i].value
                    break;
                    }
                }

            for (var i = 0; i < squares.length; i++) {
                var shape = squares[i];
                field = {}
                field['point_1'] = {}
                field['point_1']['x'] = shape.startX
                field['point_1']['y'] = shape.startY
                field['point_2'] = {}
                field['point_2']['x'] = shape.endX
                field['point_2']['y'] = shape.endY
                jsonMetadata['fields'].push(field)
            };

            jsonData['image'] = jsonPic
            jsonData['metadata'] = jsonMetadata

            var xhr = new XMLHttpRequest();
            var url = "/create";
            xhr.open("POST", url, true);
            xhr.setRequestHeader("Content-Type", "application/json");
            xhr.onreadystatechange = function() {
                if (xhr.readyState == XMLHttpRequest.DONE) {
                    if (xhr.status != 201){
                        document.getElementById("result").style.color = 'red';
                    }
                    else {
                        document.getElementById("result").style.color = 'green';
                    }
                    console.log(xhr.responseText);
                    document.getElementById("result").textContent = xhr.responseText;
                }
            }
//            xhr.onreadystatechange = function () {
//                if (xhr.readyState === 4 && xhr.status === 200) {
//                    var json = JSON.parse(xhr.responseText);
//                    console.log(json.email + ", " + json.password);
//                }
//            };
            var data = JSON.stringify(jsonData);
            xhr.send(data);


			// TODO submit request
		}, 5);
	});

	$('#reset').click(function() {
	    squares = [];
	    draw();
	});
});

function imageLoaded ()
{
    size = calculateAspectRatioFit($('#image').width(), $('#image').height(), 600, 600);
//    $('img').show();
	$('#stepTwo').show();
	$('#stepThree').show();

	canvas.width = size.width;
	canvas.height = size.height;

	context.drawImage(document.getElementById("image"),0,0,size.width,size.height);
	
	$(canvas).width(size.width);
	$(canvas).height(size.height);

//	$(canvas).css('left', $('#image').position().left);
//	$(canvas).css('top', $('#image').position().top);
	$(canvas).css('opacity', '100');

	drawContext.fillStyle = drawColor;
	drawContext.fillRect(0,0,canvas.width,canvas.height);
	
	drawCanvas.width = size.width;
	drawCanvas.height = size.height;
	$(drawCanvas).width(size.width);
	$(drawCanvas).height(size.height);

//	$(drawCanvas).css('left', $('#image').position().left);
//	$(drawCanvas).css('top', $('#image').position().top);
	$(drawCanvas).css('opacity', '0.5');
	
	drawContext.fillStyle = drawColor;


}

/**
  * Conserve aspect ratio of the original region. Useful when shrinking/enlarging
  * images to fit into a certain area.
  *
  * @param {Number} srcWidth width of source image
  * @param {Number} srcHeight height of source image
  * @param {Number} maxWidth maximum available width
  * @param {Number} maxHeight maximum available height
  * @return {Object} { width, height }
  */
function calculateAspectRatioFit(srcWidth, srcHeight, maxWidth, maxHeight) {
    var ratio = Math.min(maxWidth / srcWidth, maxHeight / srcHeight);
    return { width: srcWidth*ratio, height: srcHeight*ratio };
 }

function init() {
  drawCanvas.addEventListener('mousedown', mouseDown, false);
  drawCanvas.addEventListener('mouseup', mouseUp, false);
  drawCanvas.addEventListener('mousemove', mouseMove, false);
}

function mouseDown(e) {
  rect.startX = e.pageX - this.offsetLeft;
  rect.startY = e.pageY - this.offsetTop;
  drag = true;
}

function mouseUp() {
  drag = false;

  rect.endX = rect.startX + rect.w
  rect.endY = rect.startY + rect.h

  if (rect.endX < rect.startX){
     temp = rect.endX
     rect.endX = rect.startX
     rect.startX = rect.endX
  }

  if (rect.endY < rect.startY){
     temp = rect.endY
     rect.endY = rect.startY
     rect.startY = rect.endY
  }

  squares.push(rect)
  rect={}
  draw()
}

function mouseMove(e) {
  if (drag) {
    rect.w = (e.pageX - this.offsetLeft) - rect.startX;
    rect.h = (e.pageY - this.offsetTop) - rect.startY ;
    drawContext.clearRect(rect.startX,rect.startY,rect.startX+rect.w,rect.startY+rect.h);
    drawContext.fillRect(rect.startX, rect.startY, rect.w, rect.h);
  }
}

function draw() {
    console.log(squares);
    drawContext.clearRect(0,0,canvas.width,canvas.height);
    for (var i = 0; i < squares.length; i++) {
        var shape = squares[i];
        drawContext.fillRect(shape.startX, shape.startY, shape.w, shape.h);
    };
}