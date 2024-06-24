from bs4 import BeautifulSoup
import requests
import string
import pandas as pd

df = pd.DataFrame()

#Function to remove links that don't lead to a street page
def has_street_name(link):
  """
  Returns True if a link contains a street name parameter, false otherwise.
  """
  if "Name=" in link["href"]:
    return True
  else:
    return False
  
#Function to remove links that don't lead to a house page
def has_link_to_house(link):
  """
  Returns True if a link contains a PID (property identification number) parameter, false otherwise.
  """
  if "pid=" in link["href"]:
    return True
  else:
    return False

street_letters = "123456789"+string.ascii_uppercase

#Loop through pages containing streets that begin with a certain letter
for i in street_letters: 
  URL = f"https://gis.vgsi.com/lexingtonma/Streets.aspx?Letter={i}"
  print(URL)
  page = requests.get(URL, verify=False)

  #Parse page into html
  html_soup = BeautifulSoup(page.content, "html.parser")
  links = html_soup.find_all("a", href=True)

  #Remove non-street links
  links = filter(has_street_name, links)

  for anchor_tag in links: #anchor_tag is a tag such as <a href="Streets.aspx?Name=LEE RD">LEE RD</a>
    strt_name = anchor_tag["href"] #anchor_tag["href"] returns the link part of the tag (our URL route)

    #Visit the page listing houses for the specific street:
    streetURL = f"https://gis.vgsi.com/lexingtonma/{strt_name}"
    strt_page = requests.get(streetURL, verify=False)

    #Parse page into html
    strt_html_soup = BeautifulSoup(strt_page.content, "html.parser")
    house_links = strt_html_soup.find_all("a", href=True)

    #Remove non-house links
    house_links = filter(has_link_to_house, house_links)

    for anchor_tag in house_links: #anchor_tag is a tag such as <a href="Parcel.aspx?pid=123">10 LEE RD</a>
      house_pid = anchor_tag["href"] #anchor_tag["href"] returns the pid part of the tag (our URL route)
      houseURL = f"https://gis.vgsi.com/lexingtonma/{house_pid}"
      house_page = requests.get(houseURL, verify=False)
      house_html_soup = BeautifulSoup(house_page.content, "html.parser")
