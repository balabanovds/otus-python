# Log parser

Parsing nginx log files and provides report about time consumed by each url

## Config

The following json config expected
```json
{
    "REPORT_SIZE": 10,              // number of top time consuming urls
    "ERR_THRESHOLD_PERC": 10,       // parsing input error threshold in percents
    "REPORT_DIR": "./reports",      // where to store report
    "LOG_DIR": "./log",             // where to look for input
    "logger": {
        "filename": "some_file",    // log file, stdout if omitted
        "level":    "debug"         // log level (KO)
    },
}
```

Default config file path `./config.json`

If no config file found - the following parametes are hard-coded
```json
{
    "REPORT_SIZE": 10,             
    "ERR_THRESHOLD_PERC": 10,      
    "REPORT_DIR": "./reports",     
    "LOG_DIR": "./log",            
    "logger": {                    
        "level":    "info"         
    },
}
```


## Input

Only gzipped and plain text files accepted as input
e.g. `nginx-access-ui.log-20200202` `nginx-access-ui.log-20200202.gz`

The following format inside logfile expected:
```
# log_format ui_short 
'$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" ' \
'$status $body_bytes_sent "$http_referer" ' \
'"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" ' \
'$request_time';
```

## Output

Saves into "REPORT_DIR" html file with stats table

