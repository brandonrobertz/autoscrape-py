const controlsId = "#controls";
const startButtonId = "#start-scrape";
const stopButtonId = "#stop-scrape";
const resetButtonId = "#reset-scrape";
const statusId = "#status";
const statusTextId = "#scrape-status"
const screenshotId = "#screenshot-img";
const completeId = "#complete";
const subControls = {
  menu: "#sub-controls-menu",
  openBtn: "#toggle-button-open",
  closeBtn: "#toggle-button-close",
};
const pgControls = {
  next: "#next-page",
  prev: "#prev-page",
  download: "#download-all",
};

const baseUrl = "http://localhost:5000";

function fetchFile(id, file_id) {
  const url = `${baseUrl}/files/data/${id}/${file_id}`
  return fetch(url).then((response) => {
    return response.json();
  });
}

function saveZip(id, data) {
  if (!id || !data) {
    console.error("saveZip called without args");
    return;
  }
  const file_ids = data.map(data => data.id);
  Promise.all(file_ids.map((fid) => {
    changeStatusText(`Fetching file ID ${fid}`, "pending");
    return fetchFile(id, fid);
  }))
    .then((responses) => {
      return responses.map((r) => {
        return {
          "name": r.data.name,
          "data": r.data.data
        };
      });
    })
    .then((files) => {
      changeStatusText(`${files.length} files downloaded`, "pending");
      const zip = new JSZip();
      // const seenFileNames = [];
      files.forEach((file) => {
        const filename = `autoscrape-data/${file.name}`;
        // if (seenFileNames.indexOf(filename) !== -1) {
        //   console.warn("Skipping already included filename", filename);
        //   return;
        // }
        // seenFileNames.push(filename);
        changeStatusText(`Zipping ${filename}`, "pending");
        zip.file(filename, atob(file.data), {binary: true});
      });
      return zip.generateAsync({type:"blob"});
    })
    .then((blob) => {
      changeStatusText(`Completing ZIP`, "pending");
      const now = (new Date()).getTime();
      changeStatusText(`Zipping complete!`, "complete");
      saveAs(blob, `autoscrape-data-${now}.zip`);
    })
    .catch((err) => {
      console.error("Overall zip error", err);
    });
}

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

function renderPage(data, page) {
  $(".file-row").remove();
  const pageSize = 20;
  const maxPages = Math.ceil(data.data.length / pageSize);
  $(pgControls.next).prop("disabled", false);
  $(pgControls.prev).prop("disabled", false);
  if (page == maxPages) {
    page = maxPages;
    $(pgControls.next).prop("disabled", true);
  } else if (page == 1) {
    page = 1;
    $(pgControls.prev).prop("disabled", true);
  }
  const options = {
    paged: true,
    pageNo: page,
    append: true,
    elemPerPage: pageSize
  };
  const templateEl = $("#file-list-item");
  $("#files-list").loadTemplate(templateEl, data.data, options);
}

function renderFilesList (data) {
  let page = 1;
  renderPage(data, page);
  $(pgControls.next).off();
  $(pgControls.next).on("click", () => {
    renderPage(data, ++page);
  });
  $(pgControls.prev).off();
  $(pgControls.prev).on("click", () => {
    renderPage(data, --page);
  });
}

function scrapeComplete(id, data) {
  renderFilesList(data);
  if (data && data.data) {
    $(pgControls.download).on("click", saveZip.bind(this, id, data.data));
  }
}

function fetchFilesList (id) {
  const url = `${baseUrl}/files/list/${id}`;
  fetch(url).then((response) => {
    response.json().then(scrapeComplete.bind(this, id));
  });
}

function updateStatus (id, data) {
  if (data.message === "STARTED") {
    $(screenshotId).attr("src", `data:image/png;base64,${data.data}`);
    changeStatusText("Scrape running...", "pending");
  }
  else if (data.message === "SUCCESS") {
    $(screenshotId).hide();
    $(completeId).show();
    $(stopButtonId).hide();
    $(resetButtonId).show();
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
      updateStatus(id, data);
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

function checkUrl(url) {
  if (!url) {
    changeStatusText("Enter a scrape URL", "failure");
    return false;
  }
  if (!url.match(/^https?:\/\//)){
    changeStatusText("Bad scrape URL", "failure");
    return false;
  }
  return true;
}

function startScrape () {
  const url = $(`${controlsId} input`).val();
  if (!checkUrl(url)) {
    console.error("Bad scrape URL");
    return;
  }

  // clear any old screenshot
  $(screenshotId).attr("src", "");
  $(resetButtonId).hide();
  $(startButtonId).hide();
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
  $(startButtonId).hide();
  $(stopButtonId).hide();
  $(resetButtonId).show();
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

function reset() {
  menuClose();
  changeStatusText();
  $(statusId).hide();
  $(completeId).hide();
  $(".file-row").remove();
  $(startButtonId).show();
  $(stopButtonId).hide();
  $(resetButtonId).hide();
}

function start () {
  $(startButtonId).on("click", startScrape);
  $(`${controlsId} input`).keyup(function(e){
    // start scrape on enter
    if(e.which == 13) {
      e.preventDefault();
      startScrape();
    }
  });
  $(resetButtonId).on("click", reset);
  $(subControls.openBtn).on("click", menuOpen);
  $(subControls.closeBtn).on("click", menuClose);
}

$(document).ready(start);
