from bs4 import BeautifulSoup
import requests
import string
import re
import pandas as pd

#Disable SSL certificate verification warnings
requests.packages.urllib3.disable_warnings()

df = pd.DataFrame(columns=["Location", "Acct#", "Current Assessment", "Building Count", 
                           "Mblu",  "PID", "Owner", "Co-Owner", "Owner Address", 
                           "Sale Price", "Certificate", "Book & Page", "Sale Date", 
                           "Instrument", "Ownership History", "Year Built", 
                           "Living Area", "Replacement Cost", "Building Percent Good", 
                           "Replacement Cost Less Depreciation", "Building Attributes", 
                           "Building Sub-Areas","Extra Features",
                            "Land Use Code", "Land Description",
                             "Land Zone", "Neighborhood", "Alt Land Appr", "Land Category",
                             "Land Size (Sqr Feet)", "Land Frontage", "Land Depth",
                            "Land Assessed Value", "Outbuildings", "Valuation History"
                           ])

counter = 0

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
      soup = BeautifulSoup(house_page.content, "html.parser")

      #Parse the page of the house
      row = {}
      location = soup.find(id="MainContent_lblLocation").get_text()
      print(location)
      print(counter)
      acct = soup.find(id="MainContent_lblAcctNum").get_text()
      assessment = soup.find(id="MainContent_lblGenAssessment").get_text()
      bld_count = soup.find(id="MainContent_lblBldCount").get_text()
      mblu = pid = soup.find(id="MainContent_lblMblu").get_text()
      pid = soup.find(id="MainContent_lblPid").get_text()
      owner = soup.find(id="MainContent_lblGenOwner").get_text()
      co_owner = soup.find(id="MainContent_lblCoOwner").get_text()
      owner_address = soup.find(id="MainContent_lblAddr1").get_text()
      sl_price = soup.find(id="MainContent_lblPrice").get_text()
      cert = soup.find(id="MainContent_lblCertificate").get_text()
      bp = soup.find(id="MainContent_lblBp").get_text()
      sl_date = soup.find(id="MainContent_lblSaleDate").get_text()
      ins = soup.find(id="MainContent_lblInstrument")
      ins = ins.get_text() if ins else None
      yr_blt = soup.find(id="MainContent_ctl01_lblYearBuilt").get_text()
      lvg_area = soup.find(id="MainContent_ctl01_lblBldArea").get_text()
      rplce_cost = soup.find(id="MainContent_ctl01_lblRcn").get_text()
      bld_pc_good = soup.find(id="MainContent_ctl01_lblPctGood").get_text()
      rplce_cost_lsdep = soup.find(id="MainContent_ctl01_lblRcnld").get_text()
      ld_use_code = soup.find(id="MainContent_lblUseCode").get_text()
      ld_description = soup.find(id="MainContent_lblUseCodeDescription").get_text()
      ld_zone = soup.find(id="MainContent_lblZone").get_text()
      nbhd = soup.find(id="MainContent_lblNbhd").get_text()
      alt_ld_appr = soup.find(id="MainContent_lblAltApproved").get_text()
      ld_ctg = soup.find(id="MainContent_lblLndCategory").get_text()
      ld_size = soup.find(id="MainContent_lblLndSf").get_text()
      ld_frontage = soup.find(id="MainContent_lblLndFront").get_text()
      ld_depth = soup.find(id="MainContent_lblDepth").get_text()
      ld_value = soup.find(id="MainContent_lblLndAsmt").get_text()

      #Owner history of a house is itself a dataframe
      own_hist = pd.DataFrame()
      try:
        own_hist_table = soup.find("table", id="MainContent_grdSales")
        if own_hist_table:
          #Get the table's column headers
          header_tags = own_hist_table.find("tr", class_ = "HeaderStyle")
          #extract just the th tags
          header_tags = header_tags.find_all("th", scope="col")
          for header in header_tags:
            #Add header (e.g. "Instrument") to the dataframe
            own_hist[header.get_text()] = None
          white_rows = own_hist_table.find_all("tr", class_ = "RowStyle")
          for white_row in white_rows:
            white_td_tags = white_row.find_all("td")
            new_row = {}
            for column, tag in zip(own_hist.columns, white_td_tags):
              text = tag.get_text()
              if "&nbsp" not in text:
                new_row[column] = text
            own_hist = own_hist._append(new_row, ignore_index=True)
            #print(new_row)
          gray_rows = own_hist_table.find_all("tr", class_ = "AltRowStyle")
          for gray_row in gray_rows:
            gray_td_tags = gray_row.find_all("td")
            new_row = {}
            for column, tag in zip(own_hist.columns, gray_td_tags):
              text = tag.get_text()
              if "&nbsp" not in text:
                new_row[column] = text
            own_hist = own_hist._append(new_row, ignore_index=True)
      except Exception as e:
        print("Exception occured in retrieving owner history data.")
        print(e)

      #bld_attr is a dictionary where the keys are headers, such as Style  
      #and Model, and values are the actual attributes, such as Contempory
      bldg_attr = {}
      try:
        bldg_attr_table = soup.find("table", id="MainContent_ctl01_grdCns")
        if bldg_attr_table:
          white_rows = bldg_attr_table.find_all("tr", class_ = "RowStyle")
          for white_row in white_rows:
            white_td_tags = white_row.find_all("td")
            style, description = white_td_tags
            style_text = style.get_text()
            description_text=description.get_text()
            if "&nbsp" not in description_text:
              bldg_attr[style_text] = description_text
          gray_rows = bldg_attr_table.find_all("tr", class_ = "AltRowStyle")
          for gray_row in gray_rows:
            gray_td_tags = gray_row.find_all("td")
            style, description = gray_td_tags
            style_text = style.get_text()
            description_text=description.get_text()
            if "&nbsp" not in description_text:
              bldg_attr[style_text] = description_text
      except Exception as e:
        print("Exception occured when retrieving building attributes.")
        print(e)
                  
      #bld_sub_areas is a dictionary where the keys are building area codes, such as FBM, 
      #and values are tuples, where the first element is the Gross Area
      #and the second element is the Living Area
      bld_sub_areas = {}
      try:
        sub_areas_tbl = soup.find("table", id="MainContent_ctl01_grdSub")
        all_rows = sub_areas_tbl.find_all("tr")
        for one_row in all_rows:
          if (one_row["class"] != "HeaderStyle") and (one_row["class"] != "FooterStyle"):
            td_tags = one_row.find_all("td")
            if(len(td_tags) >= 4):
              try:
                bld_sub_areas[td_tags[0].get_text()] = (td_tags[2].get_text().strip().replace(",",""), 
                                                        td_tags[3].get_text().strip().replace(",",""))
              except Exception as e:
                 print("Exception occured when retrieving one building sub-area.")
                 print(e)
              # print ("\n", td_tags[0].get_text())
              # print ("\n", re.findall(r'\b\d{1,3}(?:,\d{3})*\b', td_tags[2].get_text()))
              # print ("\n", re.findall(r'\b\d{1,3}(?:,\d{3})*\b', td_tags[3].get_text()))
              # print ("\n", td_tags[0].get_text().strip())
              # print ("\n", td_tags[2].get_text().strip().replace(",",""))
              # print ("\n", td_tags[3].get_text().strip().replace(",",""))
              # print("\n", td_tags[0])
              # print("\n", td_tags[2])
              # print("\n", td_tags[3])
      except Exception as e:
        print("Exception occured when retrieving building sub-areas.")
        print(e)

      #Valuation history of a house is itself a dataframe
      val_hist = pd.DataFrame()
      try:
        val_hist_table = soup.find("table", id="MainContent_grdHistoryValuesAsmt")
        if val_hist_table:
          #Get the table's column headers
          header_tags = val_hist_table.find("tr", class_ = "HeaderStyle")
          #extract just the th tags
          header_tags = header_tags.find_all("th", scope="col")
          for header in header_tags:
            #Add header (e.g. "Land") to the dataframe
            val_hist[header.get_text()] = None
          #The tables have white rows and gray rows
          white_rows = own_hist_table.find_all("tr", class_ = "RowStyle")
          for white_row in white_rows:
            white_td_tags = white_row.find_all("td")
            new_row = {}
            for column, tag in zip(val_hist.columns, white_td_tags):
              text = tag.get_text()
              if "&nbsp" not in text:
                new_row[column] = text
            val_hist = val_hist._append(new_row, ignore_index=True)
          gray_rows = own_hist_table.find_all("tr", class_ = "AltRowStyle")
          for gray_row in gray_rows:
            gray_td_tags = gray_row.find_all("td")
            new_row = {}
            for column, tag in zip(own_hist.columns, gray_td_tags):
              text = tag.get_text()
              if "&nbsp" not in text:
                new_row[column] = text
            val_hist = val_hist._append(new_row, ignore_index=True)
            try:
              val_hist.sort_values(by=["Valuation Year"])
            except:
              print("Exception occured when sorting valuation history.")
      except:
        print("Exception occured in retrieving valuation history.")


      extra_fts = []
      try:
        extra_fts_table = soup.find("table", id="MainContent_grdXf")
        if extra_fts_table:
          tr_tags = extra_fts_table.find_all("tr")
          for tr_tag in tr_tags:
            if (tr_tag["class"] == "RowStyle") or (tr_tag["class"] == "AltRowStyle"):
              #Find the first cell in the row, e.g. "FPL" for fireplace, and append it to extra_fts
              td_tag = tr_tag.find("td")
              extra_fts.append(td_tag.get_text())
      except:
        print("Exception occured when retreiving extra features.")

      #Outbuildings that a house contains will be a list of outbuilding codes (e.g. SHD1 for shed frame)
      outblds = []
      try:
        outblds_table = soup.find("table", id="MainContent_grdOb")
        if outblds_table:
          tr_tags = outblds_table.find_all("tr")
          for tr_tag in tr_tags:
            if  (tr_tag["class"] == "RowStyle") or (tr_tag["class"] == "AltRowStyle"):
              #Find the first cell in the row, e.g. "FPL" for fireplace, and append it to extra_fts
                td_tag = tr_tag.find("td")
                outblds.append(td_tag.get_text())
      except:
        print("Exception occured when retreiving outbuildings.")

      try:
        row["Location"] = location
        row["Acct#"] = acct
        row["Current Assessment"] = assessment
        row["Building Count"] = bld_count
        row["Mblu"] = mblu
        row["PID"] = pid
        row["Owner"] = owner
        row["Co-Owner"] = co_owner
        row["Owner Address"] = owner_address
        row["Sale Price"] = sl_price
        row["Certificate"] = cert
        row["Book & Page"] = bp
        row["Sale Date"] = sl_date
        row["Instrument"] = ins
        row["Ownership History"] = own_hist
        row["Year Built"] = yr_blt
        row["Living Area"] = lvg_area
        row["Replacement Cost"] = rplce_cost
        row["Building Percent Good"] = bld_pc_good
        row["Replacement Cost Less Depreciation"] = rplce_cost_lsdep
        row["Building Attributes"] = bldg_attr
        row["Land Use Code"] = ld_use_code
        row["Land Description"] = ld_description
        row["Land Zone"] = ld_zone
        row["Neighborhood"] = nbhd
        row["Alt Land Appr"] = alt_ld_appr
        row["Land Category"] = ld_ctg
        row["Land Size (Sqr Feet)"] = ld_size
        row["Land Frontage"] = ld_frontage
        row["Land Depth"] = ld_depth
        row["Land Assessed Value"] = ld_value
        row["Building Sub-Areas"] = bld_sub_areas
        row["Extra Features"] = extra_fts
        row["Valuation History"] = val_hist
        row["Outbuildings"] = outblds

        df = df._append(row, ignore_index=True)
      except Exception as e:
        print("Exception occured in adding house row to dataframe.")
        print(e)

      counter+=1
      if counter==200:
        break
    if counter==200:
      break
  if counter==200:
    break

df.to_csv("output.csv")
