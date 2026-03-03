const fileInput = document.getElementById("fileInput");
const dropzone = document.getElementById("dropzone");
const removeButton = document.getElementById("removeButton");
const resetButton = document.getElementById("resetButton");
const downloadButton = document.getElementById("downloadButton");
const statusText = document.getElementById("status");
const originalImage = document.getElementById("originalImage");
const resultImage = document.getElementById("resultImage");
const fallbackToggle = document.getElementById("fallbackToggle");
const apiRow = document.getElementById("apiRow");
const apiKeyInput = document.getElementById("apiKey");

let currentFile = null;
let resultBlob = null;

const setStatus = (message) => {
  statusText.textContent = message;
};

const updateButtons = () => {
  const hasFile = Boolean(currentFile);
  removeButton.disabled = !hasFile;
  resetButton.disabled = !hasFile;
  downloadButton.disabled = !resultBlob;
};

const resetState = () => {
  currentFile = null;
  resultBlob = null;
  originalImage.removeAttribute("src");
  resultImage.removeAttribute("src");
  setStatus("Waiting for an image…");
  updateButtons();
};

const handleFile = (file) => {
  if (!file || !file.type.startsWith("image/")) {
    setStatus("Please upload a valid image file.");
    return;
  }

  if (file.size > 12 * 1024 * 1024) {
    setStatus("Image too large. Max file size is 12MB.");
    return;
  }

  currentFile = file;
  resultBlob = null;
  originalImage.src = URL.createObjectURL(file);
  resultImage.removeAttribute("src");
  setStatus("Image loaded. Ready to remove the background.");
  updateButtons();
};

const removeBackgroundViaApi = async (file, apiKey) => {
  const formData = new FormData();
  formData.append("image", file);

  if (apiKey) {
    formData.append("api_key", apiKey);
  }

  const response = await fetch("/api/remove-background", {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const contentType = response.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      const payload = await response.json();
      throw new Error(payload.error || payload.details || "API request failed.");
    }
    const text = await response.text();
    throw new Error(text || "API request failed.");
  }

  return await response.blob();
};

const processRemoval = async () => {
  if (!currentFile) return;

  removeButton.disabled = true;
  setStatus("Removing background with API…");

  try {
    const userApiKey = fallbackToggle.checked ? apiKeyInput.value.trim() : "";
    const outputBlob = await removeBackgroundViaApi(currentFile, userApiKey);

    resultBlob = outputBlob;
    resultImage.src = URL.createObjectURL(outputBlob);
    setStatus("Done! Background removed with best quality output.");
  } catch (error) {
    setStatus(error.message || "Something went wrong. Please try again.");
  } finally {
    updateButtons();
  }
};

const downloadResult = () => {
  if (!resultBlob) return;

  const link = document.createElement("a");
  link.href = URL.createObjectURL(resultBlob);
  link.download = "background-removed.png";
  link.click();
};

fileInput.addEventListener("change", (event) => {
  const file = event.target.files?.[0];
  handleFile(file);
});

dropzone.addEventListener("dragover", (event) => {
  event.preventDefault();
  dropzone.classList.add("dragover");
});

dropzone.addEventListener("dragleave", () => {
  dropzone.classList.remove("dragover");
});

dropzone.addEventListener("drop", (event) => {
  event.preventDefault();
  dropzone.classList.remove("dragover");
  const file = event.dataTransfer.files?.[0];
  handleFile(file);
});

removeButton.addEventListener("click", processRemoval);
resetButton.addEventListener("click", resetState);
downloadButton.addEventListener("click", downloadResult);

fallbackToggle.addEventListener("change", () => {
  apiRow.hidden = !fallbackToggle.checked;
});

resetState();
