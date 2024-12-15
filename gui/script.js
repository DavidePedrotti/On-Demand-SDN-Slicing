const baseDir = "images/"
const baseURL = "http://localhost:8081/controller/"

const green = "rgb(44, 151, 75)"
const red = "rgb(172, 17, 17)"

function alwaysOnMode() {
  fetchAndUpdate("first", "first/always_on_mode", "Topology1AlwaysOnMode.png", "Always On Mode", "alwaysOnBtn", "listenerBtn", "noGuestBtn", "speakerBtn")
}

function listenerMode() {
  fetchAndUpdate("first", "first/listener_mode", "Topology1ListenerMode.png", "Listener Mode", "listenerBtn", "alwaysOnBtn", "noGuestBtn", "speakerBtn")
}

function noGuestMode() {
  fetchAndUpdate("first", "first/no_guest_mode", "Topology1NoGuestMode.png", "No Guest Mode", "noGuestBtn", "alwaysOnBtn", "listenerBtn", "speakerBtn")
}

function speakerMode() {
  fetchAndUpdate("first", "first/speaker_mode", "Topology1SpeakerMode.png", "Speaker Mode", "speakerBtn", "alwaysOnBtn", "listenerBtn", "noGuestBtn")
}

function firstSlice() {
  fetchAndUpdate("second", "second/first_mode", "Topology1SpeakerMode.png", "First Mode", "firstBtn", "secondBtn", "thirdBtn")
}

function secondSlice() {
  fetchAndUpdate("second", "second/second_mode", "Topology1NoGuestMode.png", "Second Mode", "secondBtn", "thirdBtn", "firstBtn")
}

function thirdSlice() {
  fetchAndUpdate("second", "second/third_mode", "Topology1ListenerMode.png", "Third Mode", "thirdBtn", "firstBtn", "secondBtn")
}

function fetchAndUpdate(topology, slicingMode, imageSrc, text, btnId, ...btnIds) {
  fetch(baseURL + slicingMode)
    .then(response => {
      if (!response.ok) {
        document.getElementById("connectionStatus").textContent = "An error occurred during the update of slicing mode"
        document.getElementById("connectionStatus").style.color = "red"
        throw new Error('ERROR ' + response.statusText)
      }
      return response.text()
    })
    .then(data => {
      document.getElementById("connectionStatus").textContent = "Slicing mode update was successful"
      document.getElementById("connectionStatus").style.color = "green"
      document.getElementById("img").src = baseDir + imageSrc
      if(topology === "first") {
        document.getElementById("firstTopology").textContent = "Current: " + text
      } else {
        if(!data)
          data = "Default mode"
        document.getElementById("secondTopology").textContent = "Current: " + data
      }
      toggleButtonColor(topology, btnId, ...btnIds)
    })
    .catch(error => {
      document.getElementById("connectionStatus").textContent = "An error occurred during the update of slicing mode"
      document.getElementById("connectionStatus").style.color = "red"
      console.error('ERROR 2:', error)
    })
}

function toggleButtonColor(topology, btnId, ...btnIds) {
  if(topology === "first" && getButtonColor(btnId) === red) {
    document.getElementById(btnId).style.backgroundColor = green
    for(let id of btnIds) {
      document.getElementById(id).style.backgroundColor = red
    }
  } else if(topology === "second") {
    if(getButtonColor(btnId) === green) {
      document.getElementById(btnId).style.backgroundColor = red
    } else {
      document.getElementById(btnId).style.backgroundColor = green
    }
  }
}

function getButtonColor(btnId) {
  let btn = document.getElementById(btnId)
  var style = getComputedStyle(btn)
  return style['background-color']
}