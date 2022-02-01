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
var menuButton = document.getElementById('menuButton')
//var pauseButton = document.getElementById("pauseButton");
//var sendButton = document.getElementById("sendButton");
//get url from html
var url = window.location.href
var audioElem = document.getElementById("audio");
var useraudioElem = document.getElementById('useraudio');
var nextButton = document.getElementById('nextButton');
var replayButton = document.getElementById('replayButton');
var plotButton = document.getElementById('plotButton')
var resetDemo = document.getElementById('resetDemo')

function getCurrentButton(){
        // First branching, is there user audio
        // This would mean that the user is in post_trial
        if (useraudioElem){
            if (replayButton.disabled){
                if (playButton.disabled){
                    if (currentButton){
                    currentButton = nextButton
                    }
                    else if (resetDemo){
                    currentButton = resetDemo
                    }
                }
                else {currentButton = playButton}
            }
            else {currentButton = replayButton}
        }
        else if (playButton.disabled){
            if (stopButton.disabled){
            currentButton = recordButton
            }
            else {currentButton = stopButton}
        }
        else {currentButton = playButton}
        return currentButton
}

window.addEventListener('keydown', pressCurrent);
function pressCurrent(event){
    if (event.keyCode === 32){
        currentButton = getCurrentButton()
        currentButton.click()
        console.log('Spacebar pressed')
    }
}

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


if (menuButton){
    menuButton.addEventListener('click', window.location.href='/demo');
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
  try {
    await audioElem.play();
    playButton.classList.add("playing");
  } catch(err) {
    playButton.classList.remove("playing");
  };
    playButton.disabled = true;
    audioElem.addEventListener('ended', function(){
    console.log('Audio ended')
    if (recordButton) {
    recordButton.disabled = false
    console.log('Record button enabled')
    } else if ((replayButton.disabled) && (nextButton)){
    nextButton.disabled = false
    console.log('Next button enabled')
    }
    }
    );
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
    useraudioElem.addEventListener('ended', function(){
    console.log('User audio ended')
    if ((playButton.disabled)&&(nextButton)) {
    nextButton.disabled = false
    console.log('Next button enabled')
    }else{console.log('Native speaker audio button still active')}
    }
    );
}



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
		//recordButton.disabled=false
		recordButton.className='clickplz';
		stopButton.disabled = false

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

	recordButton.className='';

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

	sendAudioEvent();
	console.log('Exported Audio');
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
            //});
}

function sendAudioEvent() {
    rec.exportWAV(sendAudio);
}

function PlotAudio(){
    console.log('plot button clicked');
    var new_address = window.location.href + '/plot'
    var new_page = new URL(new_address)
    console.log(new_address)
    window.location.replace(new_page);
}

function nextChapter() {
    console.log('redirect_started')
    console.log(window.location.href)
    var new_address = window.location.href + '/next_chapter'
    var new_page = new URL(new_address)
    console.log(new_address)
    window.location.replace(new_page);
}