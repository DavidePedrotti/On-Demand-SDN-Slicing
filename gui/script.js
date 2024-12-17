const baseDir = "images/"
const baseURL = "http://localhost:8081/controller/"

const green = "rgb(44, 151, 75)"
const red = "rgb(172, 17, 17)"

const modeConfigurations = {
  first: {
    alwaysOn: { url: "first/always_on", imageSrc: "Topology1AlwaysOnMode.png", caption: "Always On Mode", activeBtn: "alwaysOnBtn", inactiveBtns: ["listenerBtn", "noGuestBtn", "speakerBtn"] },
    listener: { url: "first/listener", imageSrc: "Topology1ListenerMode.png", caption: "Listener Mode", activeBtn: "listenerBtn", inactiveBtns: ["alwaysOnBtn", "noGuestBtn", "speakerBtn"] },
    noGuest: { url: "first/no_guest", imageSrc: "Topology1NoGuestMode.png", caption: "No Guest Mode", activeBtn: "noGuestBtn", inactiveBtns: ["alwaysOnBtn", "listenerBtn", "speakerBtn"] },
    speaker: { url: "first/speaker", imageSrc: "Topology1SpeakerMode.png", caption: "Speaker Mode", activeBtn: "speakerBtn", inactiveBtns: ["alwaysOnBtn", "listenerBtn", "noGuestBtn"] }
  },
  second: {
    first: { url: "second/first", imageSrc: "Topology1SpeakerMode.png", caption: "First Mode", activeBtn: "firstBtn", inactiveBtns: ["secondBtn", "thirdBtn"] },
    second: { url: "second/second", imageSrc: "Topology1NoGuestMode.png", caption: "Second Mode", activeBtn: "secondBtn", inactiveBtns: ["thirdBtn", "firstBtn"] },
    third: { url: "second/third", imageSrc: "Topology1ListenerMode.png", caption: "Third Mode", activeBtn: "thirdBtn", inactiveBtns: ["firstBtn", "secondBtn"] }
  }
}

function changeMode(topology, mode) {
  const modeConfig = modeConfigurations[topology][mode]
  updateSliceMode(topology, modeConfig.url, modeConfig.imageSrc, modeConfig.caption, modeConfig.activeBtn, ...modeConfig.inactiveBtns)
}

function alwaysOnMode() {
  changeMode("first", "alwaysOn")
}

function listenerMode() {
  changeMode("first", "listener")
}

function noGuestMode() {
  changeMode("first", "noGuest")
}

function speakerMode() {
  changeMode("first", "speaker")
}

function firstSlice() {
  changeMode("second", "first")
}

function secondSlice() {
  changeMode("second", "second")
}

function thirdSlice() {
  changeMode("second", "third")
}

function updateSliceMode(topology, url, imageSrc, caption, activeBtn, ...inactiveBtns) {
  fetch(baseURL + url)
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
      console.log(data)
      if(topology === "first") {
        document.getElementById("firstTopology").textContent = "Current: " + caption
      } else {
        if(!data)
          data = "Default mode"
        document.getElementById("secondTopology").textContent = "Current: " + data
      }
      toggleButtonColor(topology, activeBtn, ...inactiveBtns)
    })
    .catch(error => {
      document.getElementById("connectionStatus").textContent = "An error occurred during the update of slicing mode"
      document.getElementById("connectionStatus").style.color = "red"
      console.error('ERROR 2:', error)
    })
}

function updateQoS() {
  let values = document.getElementById("qosValues").value
  values = values.split(",").map(value => parseInt(value))
  let total = values.reduce((a, b) => a + b, 0)
  if(total <= 10) {
    document.getElementById("connectionStatus").textContent = "The sum of the values must be at most 10"
    document.getElementById("connectionStatus").style.color = "red"
    return
  } else if(values.length !== 3) {
    document.getElementById("connectionStatus").textContent = "The number of values must be 3"
    document.getElementById("connectionStatus").style.color = "red"
    return
  }
  fetch(baseURL + "second/qos", {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      values: values
    })
  })
  .then(response => {
    if (!response.ok) {
      document.getElementById("connectionStatus").textContent = "An error occurred during the update of the values"
      document.getElementById("connectionStatus").style.color = "red"
      throw new Error('ERROR ' + response.statusText)
    }
    return response.caption()
  })
  .then(data => {
    document.getElementById("connectionStatus").textContent = "Values updated correctly"
    document.getElementById("connectionStatus").style.color = "green"
    console.log(data)
  })
  .catch(error => {
    document.getElementById("connectionStatus").textContent = "An error occurred during the update of the values"
  })
}


// Utils
function toggleButtonColor(topology, activeBtn, ...inactiveBtns) {
  if(topology === "first" && getButtonColor(activeBtn) === red) {
    document.getElementById(activeBtn).style.backgroundColor = green
    for(let id of inactiveBtns) {
      document.getElementById(id).style.backgroundColor = red
    }
  } else if(topology === "second") {
    if(getButtonColor(activeBtn) === green) {
      document.getElementById(activeBtn).style.backgroundColor = red
    } else {
      document.getElementById(activeBtn).style.backgroundColor = green
    }
  }
}

function getButtonColor(activeBtn) {
  let btn = document.getElementById(activeBtn)
  var style = getComputedStyle(btn)
  return style['background-color']
}