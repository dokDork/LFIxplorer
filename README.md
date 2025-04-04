# LFIxplorer
[![License](https://img.shields.io/badge/license-MIT-_red.svg)](https://opensource.org/licenses/MIT)  
<img src="https://github.com/dokDork/LFIxplorer/blob/main/images/LFIexplorer.png" width="250" height="250"> 
  
## Description
**LFIxplorer** is a tool designed to exploit Local File Inclusion (LFI) vulnerabilities in web applications. It works by identifying vulnerable parameters and reading files on the server, helping users locate and potentially exploit insecure file inclusion flaws.
The tool requires only a single input: a request file exported from Burp Suite. This file should contain the HTTP request to a page where one of the parameters is affected by an LFI vulnerability.
To use the tool, simply save the request file and mark the parameter value vulnerable to LFI with the placeholder tag **FUZZ**. LFIxplorer will then process the request and attempt to exploit the vulnerability accordingly.

## Example Usage
 ```
python3 LFIxplorer.py GET-burp-example.txt
 ``` 

  
## Command-line parameters
```
python3 LFIxplorer.py <burp file>
```

| Parameter | Description                          | Example       |
|-----------|--------------------------------------|---------------|
| `burp file`      | File saved from burSuite with FUZZ tag | `GET-burp-example.txt`, `POST-burp-example.txt`, ... |


  
## How to install it on Kali Linux (or Debian distribution)
It's very simple  
```
cd /opt
sudo git clone https://github.com/dokDork/LFIxmplorer.git
cd LFIxplorer 
chmod 755 LFIxplorer.py 
python3 LFIxplorer.py 
