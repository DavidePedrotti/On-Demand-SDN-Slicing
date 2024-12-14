const baseDir = "images/"
const baseURL = "http://localhost:8081/controller/second/"

function alwaysOnMode() {
  fetchAndUpdate("always_on_mode", "Topology1AlwaysOnMode.png", "Always On Mode")
}

function listenerMode() {
  fetchAndUpdate("listener_mode", "Topology1ListenerMode.png", "Listener Mode")
}

function noGuestMode() {
  fetchAndUpdate("no_guest_mode", "Topology1NoGuestMode.png", "No Guest Mode")
}

function speakerMode() {
  fetchAndUpdate("speaker_mode", "Topology1SpeakerMode.png", "Speaker Mode")
}

function fetchAndUpdate(mode, imageSrc, text) {
  fetch(baseURL + mode)
    .then(response => {
      if (!response.ok) {
        document.getElementById("connectionStatus").textContent = "An error occurred during change of slicing mode"
        throw new Error('ERROR ' + response.statusText)
      }
      return response.text()
    })
    .then(data => {
      console.log(data)
      document.getElementById("connectionStatus").textContent = "Slicing mode change was successful"
      document.getElementById("img").src = baseDir + imageSrc
      document.getElementById("topologyMode").textContent = "Current mode: " + text
    })
    .catch(error => {
      document.getElementById("connectionStatus").textContent = "An error occurred during change of slicing mode"
      console.error('ERROR 2:', error)
    })
}