const areas = {
  zip: "input#zip-selector",
  hext: "input#hext-selector",
  json: "pre#json-box",
};
const wrappers = {
  zip: "#zip-loader",
  hext: "#hext-loader",
};

const TEXT_EXTENSIONS = [
  "\.asp$",
  "\.aspx$",
  "\.axd$",
  "\.asx$",
  "\.asmx$",
  "\.ashx$",
  "\.cfm$",
  "\.yaws$",
  "\.html$",
  "\.htm$",
  "\.xhtml$",
  "\.jhtml$",
  "\.hta$",
  "\.jsp$",
  "\.jspx$",
  "\.wss$",
  "\.do$",
  "\.action$",
  "\.pl$",
  "\.php$",
  "\.php4$",
  "\.php3$",
  "\.phtml$",
  "\.rb$",
  "\.rhtml$",
  "\.shtml$",
  "\.xml$",
  "\.rss$",
  "\.svg$",
  "\.cgi$",
  "\.dll$",
  "\.axd$",
  "\.asx$",
  "\.asmx$",
  "\.ashx$",
  "\.aspx$",
  "\.xml$",
  "\.rss$",
  "\.atom$",
]

const checkWebExtension = (name) => {
  // AutoScrape directory files will always have an extension
  // TODO: handle other HTML-like non-.html extensions (e.g., .php)
  const re = RegExp(TEXT_EXTENSIONS.join("|"))
  if (name.match(re)) {
    return true;
  }
  return false;
};

const fromZipSelect = (file) => {
  return JSZip.loadAsync(file)
    .then(function(zip) {
      console.log("Unzipping");
      const promises =  [];
      zip.forEach((name, zipEntry) => {
        console.log("name", name);
        if (zipEntry.dir || !checkWebExtension(name))
          return;

        const p = zip.file(name)
          .async("string")
          .then((data) => {
            return {
              name: name,
              data: data
            };
          }).catch(e => {
            console.error("Error decompressing", e);
          });

        promises.push(p);
      });
      return Promise.all(promises);
    });
};

const fileToText = (file) => {
  return new Promise((res, rej) => {
    const filepath = file.name;
    const start = 0;
    const stop = file.size - 1;
    const blob = file.slice(start, stop + 1);
    const reader = new FileReader();
    reader.onloadend = (e) => {
      if (e.target.readyState == 2) { // DONE
        res(e.target.result);
      }
    };
    reader.readAsText(blob);
  });
}

const extractJSON = (hext, html) => {
  if (!Module) {
    return console.warn("No emscripten Hext library found. " +
      "Not performing additional highlighting.");
  }

  console.log("extracting",  html.slice(0, 50), "using", hext);
  const json = Module.ccall(
    "html2json",
    "string",
    ["string", "string"],
    [hext, html]
  );
  console.log("Module ccall response", json);
  try {
    return JSON.parse(json);
  }
  catch (e) {
    console.warn ("Unable to extract from file. Skipping.");
    return null;
  }
}

const startExtraction = (zip, hext) => {
  console.log("startExtraction", zip);
  fromZipSelect(zip)
    .then((files) => {
      console.log("Done unzipping!");
      return files.map(f => {
        return f.data;
      }).map((html) => {
        return extractJSON(hext, html);
      });
    })
    .then((jsons) => {
      return jsons.filter(x => x);
    })
    .then((jsons) => {
      console.log("JSONS", jsons);
      if (!jsons) {
        $(areas.json).append("No results found.");
      } else {
        jsons.forEach((j) => {
          const parsed = JSON.stringify(j, null, 2);
          $(areas.json).append(parsed);
        });
      }
    });
};

const start = () => {
  console.log("starting");
  document.querySelector(areas.zip).addEventListener("change", (e) => {
    const zip = e.target.files[0];
    $(wrappers.zip).hide();
    $(wrappers.hext).show();
    document.querySelector(areas.hext).addEventListener("change", (e) => {
    $(wrappers.hext).hide();
      const file = e.target.files[0];
      fileToText(file).then((hext) => {
        startExtraction(zip, hext);
      })
    });
  });
};

$(document).ready(start);
