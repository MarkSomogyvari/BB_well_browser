library(xml2)
library(rvest)

# 1. Get Station List manually
message("Fetching station list for Berlin Groundwater...")
url <- "https://wasserportal.berlin.de/start.php?anzeige=tabelle_gw&messanzeige=ms_gw_berlin"
page <- read_html(url, encoding = "ISO-8859-1")
stations_table <- html_table(page)[[1]]
station_ids <- as.character(stations_table[[1]])
station_ids <- trimws(station_ids)
station_ids <- station_ids[grepl("^[0-9]+$", station_ids)]

message(sprintf("Found %d station IDs.", length(station_ids)))

# 2. Prepare Directory
dir.create("data/raw/Berlin_wells", recursive = TRUE, showWarnings = FALSE)

# 3. Direct Download Strategy
# The export URL format identified from the portal:
# https://wasserportal.berlin.de/export.php?snummer=XXXX&stype=gw&anzeige=d
# where anzeige=d is daily (Tagewerte)

success_count <- 0
error_count <- 0

for (sid in station_ids) {
  tryCatch({
    export_url <- sprintf("https://wasserportal.berlin.de/export.php?snummer=%s&stype=gw&anzeige=d", sid)
    dest_file <- file.path("data/raw/Berlin_wells", paste0("station_", sid, ".csv"))
    
    # Download using download.file
    # Berlin portal can be picky, sometimes needs a User-Agent
    download.file(export_url, dest_file, quiet = TRUE, mode = "wb", 
                  headers = c("User-Agent" = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"))
    
    # Verify file content
    if (file.exists(dest_file)) {
       sz <- file.size(dest_file)
       if (sz > 500) { # Small threshold to skip empty/error pages
         success_count <- success_count + 1
         if (success_count %% 50 == 0) message(sprintf("Downloaded %d stations...", success_count))
       } else {
         unlink(dest_file)
         error_count <- error_count + 1
       }
    } else {
       error_count <- error_count + 1
    }
  }, error = function(e) {
    error_count <<- error_count + 1
  })
  
  # Be polite to the server
  Sys.sleep(0.1)
}

message(sprintf("Final Summary: Downloaded %d stations successfully. %d failed/skipped.", success_count, error_count))
