const baseURL = "http://localhost:8081/controller/"

const green = "rgb(44, 151, 75)"
const red = "rgb(172, 17, 17)"

// update buttons color and current mode on load
document.addEventListener("DOMContentLoaded", function() {
  getActiveMode("first")
  getActiveMode("second")
})

// change the slicing mode
function alwaysOnMode() { changeMode("first", "alwaysOn") }
function listenerMode() { changeMode("first", "listener") }
function noGuestMode() { changeMode("first", "noGuest") }
function speakerMode() { changeMode("first", "speaker") }
function firstSlice() { changeMode("second", "first") }
function secondSlice() { changeMode("second", "second") }
function thirdSlice() { changeMode("second", "third") }

// change the QoS
function updateQoS() {
  let values = document.getElementById("qosValues").value
  values = values.split(",").map(value => parseInt(value))
  let total = values.reduce((a, b) => a + b, 0)
  if(total > 10) {
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
    return response.text()
  })
  .then(data => {
    document.getElementById("connectionStatus").textContent = "Values updated correctly"
    document.getElementById("connectionStatus").style.color = "green"
  })
  .catch(error => {
    document.getElementById("connectionStatus").textContent = "An error occurred during the update of the values"
    document.getElementById("connectionStatus").style.color = "red"
    throw new Error('ERROR ' + error)
  })
}

// Utils
function changeMode(topology, mode) {
  const modeConfig = modeConfigurations[topology][mode]
  updateSliceMode(topology, modeConfig.url, modeConfig.caption, modeConfig.activeBtn, ...modeConfig.inactiveBtns)
}

function getActiveMode(topology) {
  fetch(baseURL + topology + "/active_modes")
  .then(response => {
    if (!response.ok) {
      throw new Error('ERROR ' + response.statusText)
    }
    return response.text()
  })
  .then(data => {
    if(!data) {
      return
    }
    let buttons = data.split(",").map(value => parseInt(value)).sort()
    let textContentId = topology === "first" ? "firstTopology": "secondTopology"
    if(isNaN(buttons[0])) {
      document.getElementById(textContentId).textContent = "Current: Default Mode"
    } else {
      document.getElementById(textContentId).textContent = "Current: " + buttons.map(index => btnIndexToCaption[topology][index]).join(", ")
      toggleButtonColor(topology,buttons.map(index => btnIndexToBtnId[topology][index]))
    }
  })
  .catch(error => {
    console.error('ERROR 2:', error)
  })
}

function updateSliceMode(topology, url, caption, activeBtn, ...inactiveBtns) {
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
      if(topology === "first") {
        document.getElementById("firstTopology").textContent = "Current: " + caption
      } else {
        data = data.split(",").map(value => modeCaptions[value.trim()]).join(", ")
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

const modeConfigurations = {
  first: {
    alwaysOn: { url: "first/always_on_mode", caption: "Always On Mode", activeBtn: "alwaysOnBtn", inactiveBtns: ["listenerBtn", "noGuestBtn", "speakerBtn"] },
    listener: { url: "first/listener_mode", caption: "Listener Mode", activeBtn: "listenerBtn", inactiveBtns: ["alwaysOnBtn", "noGuestBtn", "speakerBtn"] },
    noGuest: { url: "first/no_guest_mode", caption: "No Guest Mode", activeBtn: "noGuestBtn", inactiveBtns: ["alwaysOnBtn", "listenerBtn", "speakerBtn"] },
    speaker: { url: "first/speaker_mode", caption: "Speaker Mode", activeBtn: "speakerBtn", inactiveBtns: ["alwaysOnBtn", "listenerBtn", "noGuestBtn"] }
  },
  second: {
    first: { url: "second/first_mode", caption: "First Mode", activeBtn: "firstBtn", inactiveBtns: ["secondBtn", "thirdBtn"] },
    second: { url: "second/second_mode", caption: "Second Mode", activeBtn: "secondBtn", inactiveBtns: ["thirdBtn", "firstBtn"] },
    third: { url: "second/third_mode", caption: "Third Mode", activeBtn: "thirdBtn", inactiveBtns: ["firstBtn", "secondBtn"] }
  }
}

const btnIndexToBtnId = {
  first: {
    0: "alwaysOnBtn",
    1: "listenerBtn",
    2: "noGuestBtn",
    3: "speakerBtn"
  },
  second: {
    0: "firstBtn",
    1: "secondBtn",
    2: "thirdBtn"
  }
}

const btnIndexToCaption = {
  first: {
    0: "Always On Mode",
    1: "Listener Mode",
    2: "No Guest Mode",
    3: "Speaker Mode"
  },
  second: {
    0: "First Mode",
    1: "Second Mode",
    2: "Third Mode"
  }
}

const modeCaptions = {
  "first_mode": "First Mode",
  "second_mode": "Second Mode",
  "third_mode": "Third Mode"
}

function toggleButtonColor(topology, activeBtns, ...inactiveBtns) {
  if(!activeBtns) {
    return
  }
  if(topology === "first" && getButtonColor(activeBtns) === red) {
    document.getElementById(activeBtns).style.backgroundColor = green
    for(let id of inactiveBtns) {
      document.getElementById(id).style.backgroundColor = red
    }
  } else if(topology === "second") {
    if(typeof activeBtns === "string") {
      activeBtns = [activeBtns]
    }
    for(let id of activeBtns) {
      if(getButtonColor(id) === green) {
        document.getElementById(id).style.backgroundColor = red
      } else {
        document.getElementById(id).style.backgroundColor = green
      }
    }
  }
}

function getButtonColor(activeBtn) {
  let btn = document.getElementById(activeBtn)
  var style = getComputedStyle(btn)
  return style['background-color']
}

export { alwaysOnMode, listenerMode, noGuestMode, speakerMode, firstSlice, secondSlice, thirdSlice, updateQoS }