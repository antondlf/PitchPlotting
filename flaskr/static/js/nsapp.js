var pickFirst = document.getElementById('pickFirstButton')
var pickSecond = document.getElementById('pickSecondButton')
var playFirst = document.getElementById('playFirstButton')
var playSecond = document.getElementById('playSecondButton')
var startTrial = document.getElementById('startTrial')

var firstRecording = document.getElementById('firstAudio')
var secondRecording = document.getElementById('secondAudio')

console.log(pickFirst.disabled, pickSecond.disabled)

if (playFirst){
    playFirst.addEventListener('click', function func(){
    playAudio(firstRecording, playFirst);
    playSecond.disabled = false
    })
}

if (playSecond){
    playSecond.addEventListener('click', function func(){playAudio(secondRecording, playSecond);
    pickFirst.disabled=false;
    pickSecond.disabled=false
    })
}

if (pickFirst){pickFirst.addEventListener('click', function func(){
        pickFirst.disabled = true;
        pickSecond.disabled = true;
        pickFirst.click();
        sendData('first');
        console.log('First button clicked, first recording picked')
})}

if (pickSecond){pickSecond.addEventListener('click', function func(){
        pickFirst.disabled = true;
        pickSecond.disabled = true;
        pickSecond.click();
        sendData('second');
        console.log('Second button clicked, second recording picked')
})}

/*if (startTrial){
startTrial.addEventListener('click', playTrialAudio)
}
*/
window.addEventListener('keydown', trialResponse);
function trialResponse(event){

    if (playFirst.disabled == false && playSecond.disabled == true){
        if (event.keyCode === 32){
            //console.log('Spacebar pressed')
            playAudio(firstRecording, playFirst);
            playSecond.disabled = false
        }
    }
    else if (playFirst.disabled == true && playSecond.disabled == false){
            if (event.keyCode === 32){
            playAudio(secondRecording, playSecond)
            pickFirst.disabled = false;
            pickSecond.disabled = false;
        }
    }

    else if (playFirst.disabled == true && playSecond.disabled == true){



    // If 'a' key is pressed first recording is selected
    // 'a' key code is 65
    if (event.keyCode === 65){
        pickFirst.disabled = true;
        pickSecond.disabled = true;
        pickFirst.click();
        sendData('first');
        console.log('a pressed, first recording picked')
    }
    else if (event.keyCode === 76){
        pickFirst.disabled = true;
        pickSecond.disabled = true;
        pickSecond.click();
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

/*function playTrialAudio(){

    startTrial.diabled = true
    console.log('trial started')

    playAudio(firstRecording, firstButton)
    firstRecording.addEventListener('ended',
    function(){
    //firstButton.classList.remove("playing")
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
*/


async function playAudio(audio, button, button2){

    try {
    await audio.play();
    button.disabled = true
    //if (button2 === playSecond){button2.disabled = false}
    //button.classList.add("playing");
  } catch(err) {
    //button.classList.remove("playing");
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

    nextTrial()

}

function nextTrial() {
    console.log('redirect_started')
    console.log(window.location.href)
    var new_address = window.location.href + '/next_trial'
    var new_page = new URL(new_address)
    console.log(new_address)
    window.location.replace(new_page);
}

