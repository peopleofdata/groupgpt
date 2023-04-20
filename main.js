function formatCode(input) {
  input = input
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
  var lines = input.split("\n");
  for (var i = 0; i < lines.length; i++) {
    lines[i] = "    " + lines[i];
  }
  var output = lines.join("\n");
  return `${output}`;
}
function serializeCodeBlocks(str) {
  let counter = 0;
  while (str.indexOf("```") !== -1) {
    if (counter % 2 === 0) {
      const startIndex = str.indexOf("```") + 3;
      const endIndex = str.indexOf("```", startIndex);
      const codeContent = str.substring(startIndex, endIndex);
      str = str.replace(
        "```" + codeContent + "```",
        `<code>${formatCode(codeContent)}</code>`
      );
      return serializeCodeBlocks(str);
    } else {
      counter++;
    }
  }
  return str;
}
async function fetchHistory() {
  const responseDiv = document.getElementById("response");
  const response = await fetch("/get_history");
  const jsonResponse = await response.json();
  responseDiv.innerHTML = jsonResponse.history
    .map(
      (item, index) => `
            <div classname='response-box'>
                <div classname='user-box' style='display: flex; padding: 1rem'>
                    <image src='https://api.dicebear.com/6.x/pixel-art/svg?seed=${
                      item.input.length
                    }' style='width: 50px; height: 50px; background-color: black; padding: 0.25rem; border-radius: 5px;'/>
                    <p style='font-family: sans-serif; margin-left: 0.5rem; color: slategrey'>${
                      item.input
                    }</p>
                </div>
                <div classname='box-box' style='display: flex; padding: 1rem; background-color: ghostwhite; border-top: 1px solid whitesmoke; border-bottom: 1px solid whitesmoke;'>
                    <image src='https://api.dicebear.com/6.x/bottts-neutral/svg?seed=${
                      item.input.length
                    }' style='width: 50px; height: 50px; background-color: black; padding: 0.25rem; border-radius: 5px;'/>
                    <div style='flex-direction: column;'>
                        <p style='font-family: sans-serif; margin-left: 0.5rem;'>${serializeCodeBlocks(
                          item.response
                        )}</p>
                    </div>
                </div>
            </div>
            `
    )
    .join("\n");
}

async function sendText() {
  const textInput = document.getElementById("text-input");
  const sendButton = document.getElementById("sendButton");
  const textarea = document.getElementById("text-input");
  const loader = document.getElementById("loader");
  const svg = document.getElementById("svg-icon");
  sendButton.disabled = true;
  textarea.disabled = true;
  svg.style.display = "none";
  loader.style.display = "inherit";
  const response = await fetch("/store_text", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: `text=${encodeURIComponent(textInput.value)}`,
  });

  const jsonResponse = await response.json();
  fetchHistory().then(() => {
    const responseDiv = document.getElementById("response");
    responseDiv.scrollTop = responseDiv.scrollHeight;
  });
  sendButton.disabled = false;
  textarea.disabled = false;
  textarea.value = "";
  svg.style.display = "inherit";
  loader.style.display = "none";
}

window.onload = () => {
  fetchHistory().then(() => {
    const responseDiv = document.getElementById("response");
    responseDiv.scrollTop = responseDiv.scrollHeight;
  });
  //   setInterval(fetchHistory, 7000);
  var textarea = document.getElementById("text-input");
  textarea.value = "";
  textarea.addEventListener("keydown", function (event) {
    if (event.keyCode === 13 && !event.shiftKey) {
      event.preventDefault();
      sendText();
      var value = textarea.value.trim();
      textarea.value = "";
    }
  });
};
