const baseURL = "http://localhost:8081/controller/"
const green = "rgb(44, 151, 75)"
const red = "rgb(172, 17, 17)"

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

// Update buttons color and current mode on load
document.addEventListener("DOMContentLoaded", function() {
  getActiveMode("first")
  getActiveMode("second")
})

// Change the slicing mode
function alwaysOnMode() { changeMode("first", "alwaysOn") }
function listenerMode() { changeMode("first", "listener") }
function noGuestMode() { changeMode("first", "noGuest") }
function speakerMode() { changeMode("first", "speaker") }
function firstSlice() { changeMode("second", "first") }
function secondSlice() { changeMode("second", "second") }
function thirdSlice() { changeMode("second", "third") }

/**
 * Change the slicing mode of the topology
 * @param {string} topology - The current topology
 * @param {string} mode - The new mode
 */
function changeMode(topology, mode) {
  const modeConfig = modeConfigurations[topology][mode]
  updateSliceMode(topology, modeConfig.url, modeConfig.caption, modeConfig.activeBtn, ...modeConfig.inactiveBtns)
}

/**
 * Update the slicing mode of the topology
 * @param {string} topology - Current topology
 * @param {string} url - URL to send the request
 * @param {string} caption - Text to display after the update
 * @param {string} activeBtn - Button that will show as active after the update
 * @param  {Array} inactiveBtns - Buttons that will show as inactive after the update
 */
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

/**
 * Send the new QoS values to the controller
 *
 * The values must be separated by commas
 * The sum of the values must be at most 9
 * The number of values must be 3
 * Each value must be greater than or equal to 1
 */
function updateQoS() {
  let values = document.getElementById("qosValues").value
  values = values.split(",").map(value => parseInt(value))
  let total = values.reduce((a, b) => a + b, 0)
  if(total > 9) {
    document.getElementById("connectionStatus").textContent = "The sum of the values must be at most 9"
    document.getElementById("connectionStatus").style.color = "red"
    return
  } else if(values.length !== 3) {
    document.getElementById("connectionStatus").textContent = "The number of values must be 3"
    document.getElementById("connectionStatus").style.color = "red"
    return
  } else if(values.some(value => value < 1)) {
    document.getElementById("connectionStatus").textContent = "Each value must be greater than or equal to 1"
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

// Utility functions
/**
 * Check the active modes of the topology and update the buttons and text content
 * @param {string} topology - The topology to check the active modes for
 */
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

/**
 * Change the color of the buttons
 * @param {string} topology - Current topology
 * @param {Array} activeBtns - Buttons that will show as active
 * @param  {Array} inactiveBtns - Buttons that will show as inactive
 * @returns
 */
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

/**
 * Get the color of the button
 * @param {string} activeBtn - The id of the button to get the color of
 * @return {string} The color of the button
 */
function getButtonColor(activeBtn) {
  let btn = document.getElementById(activeBtn)
  var style = getComputedStyle(btn)
  return style['background-color']
}

export { alwaysOnMode, listenerMode, noGuestMode, speakerMode, firstSlice, secondSlice, thirdSlice, updateQoS }