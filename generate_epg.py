import xml.etree.ElementTree as ET
import re
import os
import requests
import base64

# Function to get the current sha of the file in the repository
def get_file_sha(repo, path, token):
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('sha')
    return None

# Function to upload the XML file to GitHub
def upload_to_github(repo, path, token, file_path):
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    with open(file_path, "rb") as file:
        content = base64.b64encode(file.read()).decode()
    
    sha = get_file_sha(repo, path, token)
    
    data = {
        "message": "Upload epg.xml",
        "content": content,
        "sha": sha
    }
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.put(url, json=data, headers=headers)
    if response.status_code in [200, 201]:
        print(f"Successfully uploaded {file_path} to GitHub.")
    else:
        print(f"Failed to upload {file_path} to GitHub. Status code: {response.status_code}, Response: {response.json()}")

# Function to download the XML file from a URL
def download_xml(url, local_path):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        with open(local_path, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded XML file from {url} to {local_path}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to download XML file from {url}. Error: {e}")

# Function to update XML ids and channel attributes
def update_xml_ids_and_channels(xml_file):
    if not os.path.exists(xml_file):
        print(f"Error: The file '{xml_file}' does not exist.")
        return
    
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Update channel ids
        for channel in root.findall('channel'):
            id_attr = channel.get('id')
            new_id = re.sub(r'\s+', '', id_attr)
            if new_id.startswith('AT:'):
                new_id = new_id.replace('AT:', '') + '.at'
            elif new_id.startswith('DE:'):
                new_id = new_id.replace('DE:', '') + '.de'
            elif new_id.startswith('CH:'):
                new_id = new_id.replace('CH:', '') + '.ch'
            channel.set('id', new_id)
        
        # Update programme channel attributes
        for programme in root.findall('programme'):
            channel_attr = programme.get('channel')
            new_channel = re.sub(r'\s+', '', channel_attr)
            if new_channel.startswith('AT:'):
                new_channel = new_channel.replace('AT:', '') + '.at'
            elif new_channel.startswith('DE:'):
                new_channel = new_channel.replace('DE:', '') + '.de'
            elif new_channel.startswith('CH:'):
                new_channel = new_channel.replace('CH:', '') + '.ch'
            programme.set('channel', new_channel)
        
        # Write the updated XML to a file called epg.xml
        tree.write("/home/heel/epg/epg.xml", encoding='utf-8', xml_declaration=True)
        print("The updated XML has been written to epg.xml")
    
    except ET.ParseError as e:
        print(f"Error parsing XML file: {e}")

# URL of the XML file to download
xml_url = 'https://xmltv.info/de/epg.xml'

# Path to save the downloaded XML file
local_xml_file = '/home/heel/epg/input_epg.xml'

# Download the XML file
download_xml(xml_url, local_xml_file)

# Update XML ids and channels
update_xml_ids_and_channels(local_xml_file)

# GitHub repository details
repo = "Darkatek7/german_epg"  # Replace with your GitHub username and repository name
path = "epg.xml"  # Replace with the path where you want to upload the file in the repository
token = "secret"

# Upload the updated XML file to GitHub
upload_to_github(repo, path, token, "/home/heel/epg/epg.xml")
