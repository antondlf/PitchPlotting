//webkitURL is deprecated but nevertheless
URL = window.URL || window.webkitURL;

var gumStream; 						//stream from getUserMedia()
var rec; 							//Recorder.js object
var input; 							//MediaStreamAudioSourceNode we'll be recording

// shim for AudioContext when it's not avb. 
var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext //audio context to help us record

var playButton = document.getElementById('playButton')
var recordButton = document.getElementById("recordButton");
var stopButton = document.getElementById("stopButton");
//var pauseButton = document.getElementById("pauseButton");
//var sendButton = document.getElementById("sendButton");
//get url from html
var url = window.location.href
var audioElem = document.getElementById("audio");
var useraudioElem = document.getElementById('useraudio');
var nextButton = document.getElementById('nextButton');
var replayButton = document.getElementById('replayButton')

if (playButton){
    console.log('Record button exists');
    playButton.addEventListener("click", playAudio);
}
if (replayButton){
    console.log('User Audio button exists');
    replayButton.addEventListener("click", playUserAudio);
}
if (nextButton) {
    console.log('Trial done')
    nextButton.addEventListener("click", nextChapter);
    if (recordButton){
        recordButton.disabled = true;
    }


}
else {
    console.log('trial in progress')
}

//add events to those 2 buttons
if (recordButton) {
    recordButton.addEventListener("click", startRecording);
}

if (stopButton) {
    stopButton.addEventListener("click", stopRecording);
}
//pauseButton.addEventListener("click", pauseRecording);
//sendButton.addEventListener("click", sendAudioEvent);
//if (nextButton != "undefined") {
//   nextButton.addEventListener("click", nextChapter);
//}



//playButton.addEventListener("click", handlePlayButton, false);
//playVideo();

async function playAudio() {
  console.log('Audio Playing')
  var duration = document.getElementById("audio").duration;
  console.log(duration)
  try {
    await audioElem.play();
    playButton.classList.add("playing");
  } catch(err) {
    playButton.classList.remove("playing");
  }
    playButton.disabled = true;
    recordButton.disabled = false;
}

async function playUserAudio() {
  console.log('Playing User Audio')
  try {
    await useraudioElem.play();
    replayButton.classList.add("playing");
  } catch(err) {
    replayButton.classList.remove("playing");
  }
    replayButton.disabled = true;
    nextButton.disabled = false;
}



function startRecording() {
	console.log("recordButton clicked");
	document.getElementById("formats").innerHTML="Wait..."

	/*
		Simple constraints object, for more advanced audio features see
		https://addpipe.com/blog/audio-constraints-getusermedia/
	*/
    
    var constraints = { audio: true, video:false }

 	/*
    	Disable the record button until we get a success or fail from getUserMedia() 
	*/

	recordButton.disabled = true;
	stopButton.disabled = false;
	//pauseButton.disabled = false;
	//sendButton.disabled = true;

	/*
    	We're using the standard promise based getUserMedia() 
    	https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia
	*/

	navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
		console.log("getUserMedia() success, stream created, initializing Recorder.js ...");

		/*
			create an audio context after getUserMedia is called
			sampleRate might change after getUserMedia is called, like it does on macOS when recording through AirPods
			the sampleRate defaults to the one set in your OS for your playback device

		*/

		audioContext = new AudioContext();
		console.log("audioContext initialized");

		//update the format 
		document.getElementById("formats").innerHTML="Go!"
        console.log("getElementById done");

		/*  assign to gumStream for later use  */
		gumStream = stream;
		
		/* use the stream */
		input = audioContext.createMediaStreamSource(stream);
		console.log("Stream input created");

		/* 
			Create the Recorder object and configure to record mono sound (1 channel)
			Recording 2 channels  will double the file size
		*/
		rec = new Recorder(input,{numChannels:1});
		console.log("Recorder created");

		//start the recording process
		rec.record();

		console.log("Recording started");

	}).catch(function(err) {
	  	//enable the record button if getUserMedia() fails
	  	console.log(err);
    	recordButton.disabled = false;
    	stopButton.disabled = true;
    	//pauseButton.disabled = true;
	});
}

function pauseRecording(){
	console.log("pauseButton clicked rec.recording=",rec.recording );
	if (rec.recording){
		//pause
		rec.stop();
		pauseButton.innerHTML="Resume";
	}else{
		//resume
		rec.record()
		pauseButton.innerHTML="Pause";

	}
}

function stopRecording() {
	console.log("stopButton clicked");

	//disable the stop button, enable the record too allow for new recordings
	stopButton.disabled = true;
	recordButton.disabled = true;
	//pauseButton.disabled = true;
	//sendButton.disabled = false;

	//reset button just in case the recording is stopped while paused
	//pauseButton.innerHTML="Pause";
	console.log("innerHTML.")
	
	//tell the recorder to stop the recording
	rec.stop();
	console.log('Stopped rec.');

	//stop microphone access
	gumStream.getAudioTracks()[0].stop();
	console.log('gumStream gotten.')

	//create the wav blob and pass it on to createDownloadLink
	rec.exportWAV(createDownloadLink);
	console.log('Exported Audio');
	sendAudioEvent();
}

function createDownloadLink(blob) {
	
	var url = URL.createObjectURL(blob);
	var au = document.createElement('audio');
	var li = document.createElement('li');
	var link = document.createElement('a');

	//name of .wav file to use during upload and download (without extension)
	var filename = new Date().toISOString();

	//add controls to the <audio> element
	au.controls = true;
	au.src = url;

	//save to disk link
	link.href = url;
	link.download = filename+".wav"; //download forces the browser to donwload the file using the  filename
	link.innerHTML = "Save to disk";

	//add the new audio element to li
	li.appendChild(au);
	
	//add the filename to the li
	li.appendChild(document.createTextNode(filename+".wav "))

	//add the save to disk link to li
	li.appendChild(link);
	
	//upload link
	var upload = document.createElement('a');
	upload.href="#";
	upload.innerHTML = "Upload";
	upload.addEventListener("click", function(event){
		  var xhr=new XMLHttpRequest();
		  xhr.onload=function(e) {
		      if(this.readyState === 4) {
		          console.log("Server returned: ",e.target.responseText);
		      }
		  };
		  var fd=new FormData();
		  fd.append("audio_data",blob, filename);
		  xhr.open("POST","upload.php",true);
		  xhr.send(fd);
	})
	li.appendChild(document.createTextNode (" "))//add a space in between
	li.appendChild(upload)//add the upload link to li

	//add the li element to the ol
	recordingsList.appendChild(li);
}

function sendAudio(data) {
/*    let audio = new FormData();

    audio.append("data", data);
    fetch(url, {method: "POST", body: audio});*/
    fetch(url, {method:"POST", body:data})
//            .then((res) => {
//                res.redirect(302, res.url)
//            }
//            )
            .then(response => {
                if (response.redirected) {window.location = response.url;}
                else {throw Error(`Server returned ${response.status}: ${response.statusText}`)}
            })
            //.then(response => console.log(response.text()))
            .catch(err => {
                alert(err);
            });
}

function sendAudioEvent() {
    rec.exportWAV(sendAudio);
}

function nextChapter() {
    console.log('redirect_started')
    console.log(window.location.href)
    var new_address = window.location.href + '/next_chapter'
    var new_page = new URL(new_address)
    console.log(new_address)
    window.location.replace(new_page);
}