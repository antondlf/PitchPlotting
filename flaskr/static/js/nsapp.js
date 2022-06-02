var firstButton = document.getElementById('firstButton')
var secondButton = document.getElementById('secondButton')
var startTrial = document.getElementById('startTrial')

var firstRecording = document.getElementById('firstAudio')
var secondRecording = document.getElementById('secondAudio')

console.log(firstButton.disabled, secondButton.disabled)

if (startTrial){
startTrial.addEventListener('click', playTrialAudio)
}

window.addEventListener('keydown', trialResponse);
function trialResponse(event){

    if (firstButton.disabled == true && secondButton.disabled == true){
        if (event.keyCode === 32){
            playTrialAudio()
        }
    }

    else if (firstButton.disabled == false && secondButton.disabled == false){



    // If 'a' key is pressed first recording is selected
    // 'a' key code is 65
    if (event.keyCode === 65){
        firstButton.disabled = true;
        secondButton.disabled = true;
        firstButton.click();
        sendData('first');
        console.log('a pressed, first recording picked')
    }
    else if (event.keyCode === 76){
        firstButton.disabled = true;
        secondButton.disabled = true;
        secondButton.click();
        sendData('second');
        console.log('l key pressed, second recording picked')
    }
    // go to next trial
}
    else{
        console.log('Some issue came up with button uncoordination')
        location.reload()
    }
}

function playTrialAudio(){

    startTrial.diabled = true
    console.log('trial started')

    playAudio(firstRecording, firstButton)
    firstRecording.addEventListener('ended',
    function(){
    firstButton.classList.remove("playing")
    playAudio(secondRecording, secondButton)
    }
    )
    secondRecording.addEventListener('ended', function(){
    secondButton.classList.remove("playing")
  firstButton.disabled = false
  secondButton.disabled = false
  }
  )


}


async function playAudio(audio, button){

    try {
    await audio.play();
    button.classList.add("playing");
  } catch(err) {
    button.classList.remove("playing");
    startTrial.disabled = false
  };

}


function sendData(nsResponse){

    var xhr = new XMLHttpRequest();
xhr.open("POST", window.location.href, true);
xhr.setRequestHeader('Content-Type', 'application/json');
xhr.send(JSON.stringify({
    value: nsResponse
}));

}