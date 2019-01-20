const controlsId = "#controls";
const startButtonId = "#start-scrape";
const stopButtonId = "#stop-scrape";
const statusId = "#status";
const statusTextId = "#scrape-status"
const screenshotId = "#screenshot-img";
const completeId = "#complete";
const subControls = {
  menu: "#sub-controls-menu",
  openBtn: "#toggle-button-open",
  closeBtn: "#toggle-button-close",
};

const baseUrl = "http://localhost:5000";


function changeStatusText (text, status) {
    $(statusTextId).removeClass("pending");
    $(statusTextId).removeClass("failure");
    $(statusTextId).removeClass("complete");
    $(statusTextId).text("");
    if (status)
      $(statusTextId).addClass(status);
    if (text)
      $(statusTextId).text(text);
}

function renderFilesList (data) {
  console.log("renderFilesList", data);
  const templateEl = $("#file-list-item");
  const options = {
    paged: true,
    append: true, elemPerPage: 20
  };
  $("#files-list").loadTemplate(templateEl, data.data, options);
}

function fetchFilesList (id) {
  console.log("fetchFilesList", id);
  const url = `${baseUrl}/files/list/${id}`;
  fetch(url).then((response) => {
    console.log("response", response);
    response.json().then(renderFilesList);
  });
}

function updateStatus (data) {
  if (data.message === "STARTED") {
    $(screenshotId).attr("src", `data:image/png;base64,${data.data}`);
    changeStatusText("Scrape running...", "pending");
  }
  else if (data.message === "SUCCESS") {
    $(screenshotId).hide();
    $(completeId).show();
    changeStatusText("Scrape complete", "complete");
  }
  else if (data.message === "FAILURE") {
    $(screenshotId).hide();
    changeStatusText("Scrape failed", "failure");
  }
}

function updateProgress (progressUrl, id) {
  fetch(progressUrl).then(function(response) {
    response.json().then(function(data) {
      // update the appropriate UI components
      updateStatus(data);
      // re-run this, if we aren't failed
      if (data.message === "STARTED" || data.message === "PENDING") {
        setTimeout(
          updateProgress.bind(this, progressUrl, id),
          2000,
          progressUrl
        );
      }
      else if (data.message === "SUCCESS") {
        fetchFilesList(id);
      }
    });
  });
}

function pollProgress (id) {
  $(statusId).show();
  $(screenshotId).show();
  const progressUrl = `${baseUrl}/status/${id}`;
  updateProgress(progressUrl, id);
}

function startScrape () {
  const url = $(`${controlsId} input`).val();
  console.log("Scraping from URL", url);
  // clear any old screenshot
  $(screenshotId).attr("src", "");
  menuClose();
  const data = {
    baseurl: url,
    form_submit_wait: $("#sub-controls-form_submit_wait").val(),
    input: $("#sub-controls-input").val(),
    save_graph: false,
    load_images: $("#sub-controls-load_images").is("checked"),
    maxdepth: $("#sub-controls-maxdepth").val(),
    next_match: $("#sub-controls-next_match").val(),
    leave_host: $("#sub-controls-leave_host").is("checked"),
    show_browser: false,
    driver: "Firefox",
    form_submit_natural_click: $("#sub-controls-form_submit_natural_click").is("checked"),
    formdepth: $("#sub-controls-formdepth").val(),
    link_priority: $("#sub-controls-link_priority").val(),
    keep_filename: false,
    ignore_links: $("#sub-controls-ignore_links").val(),
    form_match: $("#sub-controls-form_match").val(),
    save_screenshots: true,
    remote_hub: "http://localhost:4444/wd/hub",
    loglevel: "DEBUG",
    output: "http://flask:5001/receive",
    disable_style_saving: false
  };
  console.log("data", data);
  $.ajax({
    type: "POST",
    url: `${baseUrl}/start`,
    data: JSON.stringify(data),
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    success: function(data){
      const taskId = data.data;
      pollProgress(taskId);
      $(statusId).show();
      $(stopButtonId).show();
      $(stopButtonId).on("click", stopScrape.bind(this, taskId));
      changeStatusText("Scrape pending...", "pending");
    },
    failure: function(errMsg) {
      console.error("Failure to start scrape", errMsg);
    }
  });
}

function stopScrape (id) {
  console.log("Stopping scrape", id);
  const data = {};
  $.ajax({
    type: "POST",
    url: `${baseUrl}/stop/${id}`,
    data: JSON.stringify(data),
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    success: function(data){
      const taskId = data.data;
      pollProgress(taskId);
      $(stopButtonId).hide();
      changeStatusText("Scrape stopped", "failure");
    },
    failure: function(errMsg) {
      console.error("Failure to stop scrape", errMsg);
    }
  });
}

function menuOpen() {
  $(subControls.menu).show();
  $(subControls.closeBtn).show();
  $(subControls.openBtn).hide();
}

function menuClose() {
  $(subControls.menu).hide();
  $(subControls.openBtn).show();
  $(subControls.closeBtn).hide();
}

function start () {
  $(startButtonId).on("click", startScrape);
  $(subControls.openBtn).on("click", menuOpen);
  $(subControls.closeBtn).on("click", menuClose);
}

$(document).ready(start);
