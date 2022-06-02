var firstButton = document.getElementById('firstButton')
var secondButton = document.getElementById('secondButton')
var startTrial = document.getElementById('startTrial')

var firstRecording = document.getElementById('firstAudio')
var secondRecording = document.getElementById('secondAudio')

startTrial.addEventListener('click', playTrialAudio)

window.addEventListener('keydown', trialResponse);
function trialResponse(event){

    if (firsButton.disabled == true && secondButton.disabled == true){
        if (event.keyCode === 32){
            playTrialAudio()
        }
    }

    else if (firstButton.disabled == false && secondButton.disabled == false){


    }
    // If 'a' key is pressed first recording is selected
    // 'a' key code is 65
    if (event.keyCode === 65){
        firstButton.disabled = true;
        secondButton.disabled = true;
        firstButton.click();
        console.log('a pressed, first recording picked')
    }
    else if (event.keyCode === 76){
        firstButton.disabled = true;
        secondButton.disabled = true;
        secondButton.click();
        console.log('l key pressed, second recording picked')
    }
    // go to next trial

    else{
        console.log('Some issue came up with button uncoordination')
        location.reload()
    }
}

function playTrialAudio(){

    startTrial.diabled = true

    try {
    await firstRecording.play();
    firstButton.classList.add("playing");
  } catch(err) {
    firstButton.classList.remove("playing");
    startTrial.diabled = false
  };

    try {
    await secondRecording.play();
    secondButton.classList.add("playing");
  } catch(err) {
    secondButton.classList.remove("playing");
    startTrial.diabled = false
  };

  firstButton.disabled = false
  secondButton.disabled = false


}