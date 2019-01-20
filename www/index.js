const controlsId = "#controls";
const startButtonId = "#start-scrape";
const stopButtonId = "#stop-scrape";
const statusId = "#status";
const screenshotId = "#screenshot-img";
const completeId = "#complete";

const baseUrl = "http://localhost:5000";

function updateStatus (data) {
  console.log("Updating status", data);
  if (data.message === "STARTED") {
    $(screenshotId).attr("src", `data:image/png;base64,${data.data}`);
    console.error("Scrape ongoing:", data);
  }
  else if (data.message === "SUCCESS") {
    $(screenshotId).hide();
    $(completeId).show();
    console.error("Scrape complete:", data);
  }
  else if (data.message === "FAILURE") {
    $(screenshotId).hide();
    console.error("Scrape failure:", data);
  }
}

function updateProgress (progressUrl, id) {
  console.log("Fetching progress", progressUrl, id);
  fetch(progressUrl).then(function(response) {
    response.json().then(function(data) {
      // update the appropriate UI components
      updateStatus(data);
      // re-run this, if we aren't failed
      if (data.message === "STARTED") {
        setTimeout(
          updateProgress.bind(this, progressUrl, id),
          500,
          progressUrl
        );
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
  const data = {
    baseurl: url,
    form_submit_wait: "5",
    input: null,
    save_graph: false,
    load_images: false,
    maxdepth: "0",
    next_match: "next page",
    leave_host: false,
    show_browser: false,
    driver: "Firefox",
    form_submit_natural_click: false,
    formdepth: "0",
    link_priority: null,
    keep_filename: false,
    ignore_links: null,
    form_match: null,
    save_screenshots: true,
    remote_hub: "http://localhost:4444/wd/hub",
    loglevel: "DEBUG",
    output: "http://flask:5001/receive",
    disable_style_saving: false
  };
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
    },
    failure: function(errMsg) {
      alert(errMsg);
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
    },
    failure: function(errMsg) {
      alert(errMsg);
    }
  });
}

function start () {
  $(startButtonId).on("click", startScrape);
}

$(document).ready(start);
