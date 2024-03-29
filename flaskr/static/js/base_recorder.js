//webkitURL is deprecated but nevertheless
URL = window.URL || window.webkitURL;

var gumStream; 						//stream from getUserMedia()
var rec; 							//Recorder.js object
var input; 							//MediaStreamAudioSourceNode we'll be recording

// shim for AudioContext when it's not avb.
var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext //audio context to help us record

var recordButton = document.getElementById("recordButton");
var stopButton = document.getElementById("stopButton");
//var sendButton = document.getElementById("sendButton");
var nextButton = document.getElementById('nextButton');

var currentButton = recordButton

window.addEventListener('keydown', pressCurrent);
function pressCurrent(event){
    if (event.keyCode === 32){
        currentButton.click()
        console.log('Spacebar pressed')
    }
}

//add events to those 2 buttons
recordButton.addEventListener("click", startRecording);

stopButton.addEventListener("click", stopRecording);

//sendButton.addEventListener("click", sendAudioEvent);
nextButton.addEventListener("click", nextChapter);




function startRecording() {
	console.log("recordButton clicked");

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
	currentButton = stopButton
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
		recordButton.disabled=false;
		recordButton.className='clickplz';

		console.log("Recording started");

	}).catch(function(err) {
	  	//enable the record button if getUserMedia() fails
	  	console.log(err);
    	recordButton.disabled = false;
    	currentButton = recordButton
    	stopButton.disabled = true;
    	//pauseButton.disabled = true;
	});
}

//function pauseRecording(){
//	console.log("pauseButton clicked rec.recording=",rec.recording );
//	if (rec.recording){
//		//pause
//		rec.stop();
//		//pauseButton.innerHTML="Resume";
//	}else{
//		//resume
//		rec.record()
//		//pauseButton.innerHTML="Pause";
//
//	}
//}

function stopRecording() {
	console.log("stopButton clicked");

	recordButton.className='';

	//disable the stop button, enable the record too allow for new recordings
	stopButton.disabled = true;
	recordButton.disabled = true;
	//sendButton.disabled = false;
	nextButton.disabled = false;
	currentButton = nextButton

	document.getElementById("formats").innerHTML="Done!"

	//reset button just in case the recording is stopped while paused
	//pauseButton.innerHTML="Pause";

	//tell the recorder to stop the recording
	rec.stop();

	//stop microphone access
	gumStream.getAudioTracks()[0].stop();

	//create the wav blob and pass it on to createDownloadLink
	rec.exportWAV(createDownloadLink);
	sendAudioEvent();
}

function createDownloadLink(blob) {

	var url = URL.createObjectURL(blob);
	var au = document.createElement('audio');
	var li = document.createElement('li');
	var link = document.createElement('a');

	//name of .wav file to use during upload and download (without extendion)
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

function nextChapter() {
    console.log('redirect_started')
    var new_page = new URL("/next_chapter", location)
    window.location.replace(new_page);
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
//                else {throw Error(`Server returned ${response.status}: ${response.statusText}`)}
            })
            .then(response => console.log(response.text()))
            //.catch(err => {
            //    alert(err);
           // });
}

function sendAudioEvent() {
    rec.exportWAV(sendAudio);
}

function nextChapter() {
    console.log('send audio')
    sendAudioEvent()
    console.log('redirect_started')
    console.log(window.location.href)
    var new_address = window.location.href + '/post_trial/next_chapter'
    var new_page = new URL(new_address)
    console.log(new_address)
    window.location.replace(new_page);
}